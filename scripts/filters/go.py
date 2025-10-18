import json
import requests
import re
import base64
import time

def count_go_dependencies(json_file_path):
    with open(json_file_path, 'r') as f:
        projects = json.load(f)
    
    github_token = ""
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    for project_name, project_data in projects.items():
        if 'GO' in project_data.get('projectType', []):
            print(f"Processing Go project: {project_name}")
            
            # Get repository contents
            repo_url = project_data['url']
            api_url = repo_url.replace('https://api.github.com/repos/', '')
            
            try:
                # Get the go.mod file content
                go_mod_url = f"https://api.github.com/repos/{api_url}/contents/go.mod"
                response = requests.get(go_mod_url, headers=headers)
                response.raise_for_status()
                
                # API rate limit handling
                if int(response.headers.get('X-RateLimit-Remaining', 1)) < 5:
                    print("API rate limit nearly reached, sleeping...")
                    reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 3600))
                    sleep_time = max(reset_time - time.time(), 0) + 10
                    print(f"Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                
                # Decode content
                file_content = base64.b64decode(response.json()['content']).decode('utf-8')
                
                # Count dependencies
                dependencies_count = 0
                
                # Look for dependencies in the require block or individual require statements
                require_block_match = re.search(r'require\s*\((.*?)\)', file_content, re.DOTALL)
                if require_block_match:
                    # Dependencies in a require block
                    require_block = require_block_match.group(1)
                    # Count each dependency line (skipping empty lines and comments)
                    for line in require_block.split('\n'):
                        if line.strip() and not line.strip().startswith('//'):
                            dependencies_count += 1
                
                # Look for single-line require statements (require module version)
                single_requires = re.findall(r'require\s+(\S+)\s+(\S+)', file_content)
                dependencies_count += len(single_requires)
                
                # Add the count to the project data
                project_data['dependenciesCount'] = dependencies_count
                print(f"Found {dependencies_count} dependencies in {project_name}")
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching go.mod for {project_name}: {e}")
                project_data['dependenciesCount'] = -1
            # This is just a small delay to avoid hitting rate limits too quickly.
            time.sleep(1)
    
    with open(json_file_path, 'w') as f:
        json.dump(projects, f, indent=2)
    
    print(f"Processing complete. Updated {json_file_path}")

if __name__ == "__main__":
    count_go_dependencies("path_to_the_go_projects_json_file.json")