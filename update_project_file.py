import re
from project_names_utils import get_project_references, find_unreferenced_csproj_files
from project_file_agents import add_project_references

def update_project_file(test_file_content, test_file_path, root_directory, project_file_path):
        # Extracting namespace and class names from the test file content to identify the test class and its namespace
        namespace_match = re.search(r'namespace\s+([a-zA-Z0-9_\.]+)(?:\s|//[^\n]*)*{', test_file_content, re.MULTILINE)
        class_matches = re.finditer(r'(?:public|private|internal)?\s*class\s+(\w+)', test_file_content)
        
        # Find the test class (not DTO or Factory)
        test_class_name = None
        for match in class_matches:
            class_name = match.group(1)
            if 'DTO' not in class_name and 'Factory' not in class_name:
                test_class_name = class_name
                break
        
        # The following steps are necessary to ensure that all required project references are correctly added to the test project.
        # This includes identifying the namespace and class name of the test class, finding project references in the test file,
        # identifying any unreferenced .csproj files, and adding those references to the primary .csproj file.
        namespace_name = namespace_match.group(1) if namespace_match else None
        namespace_and_classname = f"{namespace_name}.{test_class_name}" if namespace_name and test_class_name else test_class_name
        project_references = get_project_references(test_file_path, root_directory)
        unreferenced_csproj_files = find_unreferenced_csproj_files(project_file_path, project_references)
        function_calls = add_project_references(project_file_path, unreferenced_csproj_files)
        for tool_call in function_calls.tool_calls:
            tool_call()
        return namespace_and_classname