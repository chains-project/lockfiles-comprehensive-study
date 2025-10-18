import json
import requests
import re
import base64
import os
import sys
import time

def count_gradle_dependencies(json_file_path):
    with open(json_file_path, 'r') as f:
        projects = json.load(f)
    
    github_token = ""
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    for project_name, project_data in projects.items():
        if 'GRADLE' in project_data.get('projectType', []):
            print(f"Processing Gradle project: {project_name}")
            
            # Get repository contents
            repo_url = project_data['url']
            api_url = repo_url.replace('https://api.github.com/repos/', '')
            
            try:
                # Get the build.gradle file content
                build_gradle_url = f"https://api.github.com/repos/{api_url}/contents/build.gradle"
                response = requests.get(build_gradle_url, headers=headers)
                
                # Try build.gradle.kts if build.gradle is not found
                if response.status_code == 404:
                    build_gradle_url = f"https://api.github.com/repos/{api_url}/contents/build.gradle.kts"
                    response = requests.get(build_gradle_url, headers=headers)
                
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

                # Count dependencies, this is probably the simplest approach
                dependencies_count = 0
                
                # Look for dependencies in the dependencies block
                deps_block_match = re.search(r'dependencies\s*\{(.*?)\}', file_content, re.DOTALL)
                if deps_block_match:
                    deps_block = deps_block_match.group(1)
                    print(f"Found dependencies block in {project_name}")
                    
                    # Remove comments from the block
                    # Remove single-line comments
                    deps_block = re.sub(r'//.*$', '', deps_block, flags=re.MULTILINE)
                    # Remove multi-line comments
                    deps_block = re.sub(r'/\*.*?\*/', '', deps_block, flags=re.DOTALL)
                    
                    # Count non-empty lines
                    non_empty_lines = [line.strip() for line in deps_block.split('\n') if line.strip()]
                    dependencies_count = len(non_empty_lines)
                
                # Add the count to the project data
                project_data['dependenciesCount'] = dependencies_count
                print(f"Found {dependencies_count} dependencies in {project_name}")
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching build.gradle for {project_name}: {e}")
                project_data['dependenciesCount'] = -1 
            
            time.sleep(1)
    
    with open(json_file_path, 'w') as f:
        json.dump(projects, f, indent=2)
    
    print(f"Processing complete. Updated {json_file_path}")

if __name__ == "__main__":
    count_gradle_dependencies("path_to_the_gradle_projects_json_file.json")
