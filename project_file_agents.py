import ell
from tools import rewrite_test_project_file

@ell.complex(model="gpt-4o-mini", temperature=0.0, tools=[rewrite_test_project_file])
def add_project_references(test_project_file_path: str, project_paths_to_add_to_references: list[str]):
    """
    Your only responsibility is to add project references to the csproj test project file that are given to you.
    You are not allowed to add any other project references or remove any project references.
    Use the rewrite_project_file tool to rewrite the test project file.
    """
    with open(test_project_file_path, 'r') as file:
        test_project_file_content = file.read()
    return f"""
        Rewrite the test project file to add the following project references: {project_paths_to_add_to_references}

        # Test project file content:
        ```
        {test_project_file_content}
        ```

        # Test project file path:
        ```
        {test_project_file_path}
        ```
    """
