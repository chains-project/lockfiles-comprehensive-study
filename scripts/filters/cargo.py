import json
import requests
import re
import base64
import time

def count_cargo_dependencies(json_file_path):
    with open(json_file_path, 'r') as f:
        projects = json.load(f)
    
    github_token = ""
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    for project_name, project_data in projects.items():
        
        if 'CARGO' in project_data.get('projectType', []):
            print(f"Processing Cargo project: {project_name}")
            
            # Get repository contents
            repo_url = project_data['url']
            api_url = repo_url.replace('https://api.github.com/repos/', '')
            
            try:
                # Get the Cargo.toml file content
                cargo_url = f"https://api.github.com/repos/{api_url}/contents/Cargo.toml"
                response = requests.get(cargo_url, headers=headers)
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
                
                # Look for dependencies in the [dependencies] section
                deps_match = re.search(r'\[dependencies\](.*?)(\[|\Z)', file_content, re.DOTALL)
                if deps_match:
                    deps_section = deps_match.group(1)
                    # Count each dependency line
                    # This matches lines like "brotli = "7"" or "clap = { version = "4.5.29", features = ["derive"] }"
                    for line in deps_section.split('\n'):
                        if '=' in line and not line.strip().startswith('#') and line.strip():
                            dependencies_count += 1
                
                # Look for dev dependencies in the [dev-dependencies] section
                dev_deps_match = re.search(r'\[dev-dependencies\](.*?)(\[|\Z)', file_content, re.DOTALL)
                if dev_deps_match:
                    dev_deps_section = dev_deps_match.group(1)
                    # Count each dependency line
                    for line in dev_deps_section.split('\n'):
                        if '=' in line and not line.strip().startswith('#') and line.strip():
                            dependencies_count += 1
                
                # If dependencies_count is 0, check for workspace members
                if dependencies_count == 0:
                    # First check if there's a workspace section
                    has_workspace = re.search(r'\[workspace\]', file_content) is not None
                    
                    if has_workspace:
                        # We use direct pattern matching for members array similar to the dependency approach
                        # We double check for workspace members array pattern
                        print(f"Looking for workspace members array in {project_name}...")
                        # Pattern matches: members = [ ... ] with any content including nested brackets
                        members_pattern = r'members\s*=\s*\[([\s\S]*?)\]'
                        members_match = re.search(members_pattern, file_content, re.DOTALL)
                        
                        if members_match:
                            members_content = members_match.group(1)
                            # Count quoted strings in this content (each is a workspace member)
                            quoted_strings = re.findall(r'["\']([^"\']+)["\']', members_content)
                            member_count = len(quoted_strings)
                            
                            print(f"Found {member_count} workspace members in {project_name}")
                            
                            if member_count > 0:
                                # Mark as workspace if it has members
                                project_data['dependenciesCount'] = "workspace"
                                print(f"Marking {project_name} as 'workspace' with {member_count} members")
                            else:
                                # No members found, set the count to 0
                                project_data['dependenciesCount'] = dependencies_count
                                print(f"Found workspace but no members in {project_name}")
                        else:
                            # No members array found, set the count to 0
                            project_data['dependenciesCount'] = dependencies_count
                            print(f"Found workspace but no members array in {project_name}")
                    else:
                        # No workspace section found, set the count to 0
                        project_data['dependenciesCount'] = dependencies_count
                        print(f"No workspace section in {project_name}, found {dependencies_count} dependencies")
                else:
                    # Dependencies found, set the count
                    project_data['dependenciesCount'] = dependencies_count
                    print(f"Found {dependencies_count} dependencies in {project_name}")
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching Cargo.toml for {project_name}: {e}")
                project_data['dependenciesCount'] = -1 
            
            time.sleep(1)
    
    with open(json_file_path, 'w') as f:
        json.dump(projects, f, indent=2)
    
    print(f"Processing complete. Updated {json_file_path}")

if __name__ == "__main__":
    count_cargo_dependencies("path_to_the_cargo_projects_json_file.json")