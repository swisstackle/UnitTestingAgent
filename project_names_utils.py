import re
import subprocess
import os
import xml.etree.ElementTree as ET
from typing import List, Dict, Union

def test_project_reference_checker(
    project_file_path: str,
    project_name: str
):
    project_file_path = project_file_path.replace('/', '\\')
    # Before running the command, check if the project file exists
    if not os.path.exists(project_file_path):
        return f"Error: The project file '{project_file_path}' does not exist."
    command = f"dotnet list {project_file_path} reference | Select-String \"{project_name}\""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return project_name in result.stdout

# This function scans the codebase for .csproj files and creates a mapping of project names to their file paths.
# It's crucial for identifying all available projects in the solution, which is necessary for accurate reference matching.
def scan_csproj_files(root_directory):
    project_dict = {}
    for root, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith('.csproj'):
                full_path = os.path.join(root, file)
                project_name = os.path.splitext(file)[0]
                if project_name in project_dict:
                    if isinstance(project_dict[project_name], list):
                        project_dict[project_name].append(full_path)
                    else:
                        project_dict[project_name] = [project_dict[project_name], full_path]
                else:
                    project_dict[project_name] = full_path
    return project_dict

# This function extracts the namespace from a C# file's content.
# It's important for identifying the current file's namespace, which helps in excluding self-references.
def extract_namespace(content):
    namespace_match = re.search(r'namespace\s+([\w.]+)', content)
    return namespace_match.group(1) if namespace_match else None

# This function finds projects that match the given namespace.
# It's essential for identifying which projects should be excluded from the reference search,
# preventing self-references and references to parent projects.
def find_matching_projects(namespace, project_dict):
    if not namespace:
        return []
    
    parts = namespace.split('.')
    matching_projects = []
    
    for i in range(len(parts), 0, -1):
        potential_project = '.'.join(parts[:i])
        if potential_project in project_dict.keys():
            matching_projects.append(potential_project)
            break;
    
    return matching_projects

# This function analyzes a C# file to find references to other projects.
# It's the core of the reference detection process, identifying which projects are used in the file
# while excluding self-references and references to parent projects.
def analyze_cs_file(cs_file_path, project_dict):
    with open(cs_file_path, 'r') as file:
        content = file.read()
    
    file_namespace = extract_namespace(content)
    projects_to_exclude = find_matching_projects(file_namespace, project_dict)

    matched_projects = set()
    for project_name in project_dict.keys():
        if project_name in projects_to_exclude:
            continue

        # Look for project name in using statements
        if re.search(rf'\busing\s+{re.escape(project_name)}[.;]', content):
            matched_projects.add(project_name)
        # Look for project name in fully qualified names
        elif re.search(rf'\b{re.escape(project_name)}\.[A-Z]', content):
            matched_projects.add(project_name)
    
    return matched_projects

# This function resolves project names to their full file paths.
# It's necessary for converting the matched project names into actual file paths that can be used for referencing.
def resolve_project_references(matched_projects, project_dict):
    referenced_projects = []
    for project in matched_projects:
        paths = project_dict[project]
        if isinstance(paths, list):
            referenced_projects.extend(paths)
        else:
            referenced_projects.append(paths)
    return referenced_projects

# This is the main function that orchestrates the entire process of finding project references.
# It ties together all the other functions to provide a complete solution for identifying
# which projects need to be referenced based on the content of a given C# file.
def get_project_references(cs_file_path, root_directory):
    project_dict = scan_csproj_files(root_directory)
    matched_projects = analyze_cs_file(cs_file_path, project_dict)
    return resolve_project_references(matched_projects, project_dict)

# This function identifies which test .csproj files are not referenced in a primary .csproj file.
# It takes the primary project's path and a list of test project paths, then returns the test project paths
# that are not currently referenced in the primary project. The returned paths are relative to the primary project's directory.
def find_unreferenced_csproj_files(primary_csproj_path: str, test_csproj_paths: List[str]) -> List[str]:
    """
    Identifies which test .csproj files are not referenced in the primary .csproj file.

    Args:
        primary_csproj_path (str): Absolute path to the primary .csproj file.
        test_csproj_paths (List[str]): List of absolute paths to test project .csproj files.

    Returns:
        List[str]: List of test .csproj file paths (relative to the primary project directory) that are not referenced.
    """
    # Extract the directory of the primary .csproj file
    primary_dir = os.path.dirname(os.path.abspath(primary_csproj_path))

    # Parse the primary .csproj file to extract existing ProjectReferences
    tree = ET.parse(primary_csproj_path)
    root = tree.getroot()
    namespace = {'msbuild': 'http://schemas.microsoft.com/developer/msbuild/2003'}

    # Handle XML namespaces if present
    if root.tag.startswith('{'):
        uri, tag = root.tag[1:].split('}')
        ns = {'ns': uri}
    else:
        ns = {}

    existing_references = set()
    for proj_ref in root.findall('.//ProjectReference', ns):
        include_path = proj_ref.get('Include')
        if include_path:
            # Normalize the path
            normalized_path = os.path.normpath(os.path.join(primary_dir, include_path))
            existing_references.add(os.path.abspath(normalized_path))

    # Convert test_csproj_paths to absolute paths
    test_absolute_paths = {os.path.abspath(path) for path in test_csproj_paths}

    # Determine which test projects are not referenced
    unreferenced_absolute = test_absolute_paths - existing_references

    # Convert unreferenced absolute paths to relative paths
    unreferenced_relative = [
        os.path.relpath(path, primary_dir) for path in unreferenced_absolute
    ]

    return unreferenced_relative
