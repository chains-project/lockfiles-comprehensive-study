import json
import requests
import re
import base64
import time

def count_poetry_dependencies(json_file_path):
    with open(json_file_path, 'r') as f:
        projects = json.load(f)
    
    github_token = ""
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    for project_name, project_data in projects.items():    
        if 'POETRY' in project_data.get('projectType', []):
            print(f"Processing Poetry project: {project_name}")
            
            # Get repository contents
            repo_url = project_data['url']
            api_url = repo_url.replace('https://api.github.com/repos/', '')
            
            try:
                # Get the pyproject.toml file content
                pyproject_url = f"https://api.github.com/repos/{api_url}/contents/pyproject.toml"
                response = requests.get(pyproject_url, headers=headers)
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
                # print(f"File content (first 200 chars): {file_content[:200]}...")

                dependencies_count = 0
                # There are two types of formats to consider: traditional Poetry format and PEP 621 format
                # Process traditional Poetry format
                # [tool.poetry.dependencies] section
                main_deps_match = re.search(r'\[tool\.poetry\.dependencies\](.*?)(\[|\Z)', file_content, re.DOTALL)
                if main_deps_match:
                    deps_section = main_deps_match.group(1)
                    deps_lines = [line.strip() for line in deps_section.split('\n') 
                                 if line.strip() and not line.strip().startswith('#') and '=' in line]
                    dependencies_count += len(deps_lines)
                    # print(f"Found {len(deps_lines)} dependencies in [tool.poetry.dependencies] section")
                
                # [tool.poetry.dev-dependencies] section
                dev_deps_match = re.search(r'\[tool\.poetry\.dev-dependencies\](.*?)(\[|\Z)', file_content, re.DOTALL)
                if dev_deps_match:
                    dev_deps_section = dev_deps_match.group(1)
                    dev_deps_lines = [line.strip() for line in dev_deps_section.split('\n') 
                                     if line.strip() and not line.strip().startswith('#') and '=' in line]
                    dependencies_count += len(dev_deps_lines)
                    # print(f"Found {len(dev_deps_lines)} dependencies in [tool.poetry.dev-dependencies] section")
                
                # Process PEP 621 format
                dependencies_pattern = r'dependencies\s*=\s*\[(.*?)\]'
                dependencies_matches = re.findall(dependencies_pattern, file_content, re.DOTALL)
                
                project_deps_count = 0
                for deps_content in dependencies_matches:
                    # print(f"Found dependencies array content: {deps_content}")
                    # Count quoted strings in this content (each is a dependency)
                    quoted_strings = re.findall(r'["\']([^"\']+)["\']', deps_content)
                    # print(f"  Quoted strings found: {quoted_strings}")
                    project_deps_count += len(quoted_strings)
                
                if project_deps_count > 0:
                    print(f"Found {project_deps_count} dependencies in project dependencies array")
                    dependencies_count += project_deps_count
                
                # Look for optional dependencies patterns
                print("Looking for optional dependencies...")
                optional_deps_pattern = r'\[project\.optional-dependencies\]'
                optional_section_match = re.search(optional_deps_pattern, file_content)

                if optional_section_match:
                    # Find the start position of the section
                    start_pos = optional_section_match.end()
                    
                    # Find the next section or end of file
                    next_section_match = re.search(r'\[\w+', file_content[start_pos:])
                    if next_section_match:
                        end_pos = start_pos + next_section_match.start()
                        optional_section = file_content[start_pos:end_pos]
                    else:
                        optional_section = file_content[start_pos:]
                    
                    print(f"Optional dependencies section content:\n{optional_section}")
                    
                    # Find all key-value pairs where value is an array
                    optional_deps = re.findall(r'(\w+)\s*=\s*\[(.*?)\]', optional_section, re.DOTALL)
                    
                    optional_deps_count = 0
                    for key, value in optional_deps:
                        # Count quoted strings in the array
                        quoted_strings = re.findall(r'["\']([^"\']+)["\']', value)
                        group_count = len(quoted_strings)
                        print(f"  Found {group_count} dependencies in optional group '{key}'")
                        optional_deps_count += group_count
                    
                    if optional_deps_count > 0:
                        print(f"Found {optional_deps_count} dependencies in optional dependencies")
                        dependencies_count += optional_deps_count
                # Add the count to the project data
                project_data['dependenciesCount'] = dependencies_count
                print(f"TOTAL: Found {dependencies_count} dependencies in {project_name}")
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching pyproject.toml for {project_name}: {e}")
                project_data['dependenciesCount'] = -1
            except Exception as e:
                print(f"Unexpected error processing {project_name}: {e}")
                project_data['dependenciesCount'] = -1
            
            time.sleep(1)
    
    with open(json_file_path, 'w') as f:
        json.dump(projects, f, indent=2)
    
    print(f"Processing complete. Updated {json_file_path}")

def check_requirements_and_setup(json_file_path):
    """
    Poetry can read deps from requirements.txt or setup.py/setup.cfg too.
    Check for requirements.txt, setup.py, and setup.cfg in projects with 0 dependencies.
    Update 'dependenciesCount' to 'requirements' or 'setup' accordingly.
    """
    # Read the JSON file
    with open(json_file_path, 'r') as f:
        projects = json.load(f)
    
    # Set up GitHub API headers
    github_token = ""
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    # Process each project
    for project_name, project_data in projects.items():
        # Only check projects with dependenciesCount of 0
        if 'dependenciesCount' in project_data and project_data['dependenciesCount'] == 0:
            print(f"Checking additional files in {project_name}...")
            
            # Get repository contents
            repo_url = project_data['url']
            api_url = repo_url.replace('https://api.github.com/repos/', '')
            
            # Check for requirements.txt
            req_url = f"https://api.github.com/repos/{api_url}/contents/requirements.txt"
            try:
                req_response = requests.get(req_url, headers=headers)
                req_response.raise_for_status()
                
                # If we get here, requirements.txt exists
                print(f"Found requirements.txt in {project_name}")
                project_data['dependenciesCount'] = "requirements"
                
                # Continue to the next project since we've already found requirements.txt
                continue
                    
            except requests.exceptions.RequestException as e:
                print(f"No requirements.txt found in {project_name}")
            
            # Check for setup.py
            setup_py_url = f"https://api.github.com/repos/{api_url}/contents/setup.py"
            try:
                setup_py_response = requests.get(setup_py_url, headers=headers)
                setup_py_response.raise_for_status()
                
                # If we get here, setup.py exists
                print(f"Found setup.py in {project_name}")
                project_data['dependenciesCount'] = "setup"
                
                # Continue to the next project since we've already found setup.py
                continue
                    
            except requests.exceptions.RequestException as e:
                print(f"No setup.py found in {project_name}")
            
            # Check for setup.cfg
            setup_cfg_url = f"https://api.github.com/repos/{api_url}/contents/setup.cfg"
            try:
                setup_cfg_response = requests.get(setup_cfg_url, headers=headers)
                setup_cfg_response.raise_for_status()
                
                # If we get here, setup.cfg exists
                print(f"Found setup.cfg in {project_name}")
                project_data['dependenciesCount'] = "setup"
                    
            except requests.exceptions.RequestException as e:
                print(f"No setup.cfg found in {project_name}")

            time.sleep(1)
    
    with open(json_file_path, 'w') as f:
        json.dump(projects, f, indent=2)
    
    print(f"Processing complete. Updated {json_file_path}")

if __name__ == "__main__":
    count_poetry_dependencies("path_to_the_poetry_projects_json_file.json")
    check_requirements_and_setup("path_to_the_poetry_projects_json_file.json")