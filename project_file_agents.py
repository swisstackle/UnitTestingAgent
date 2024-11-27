import ell
from tools import rewrite_test_project_file
from llm_clients import openai_client_for_openrouter
import os

@ell.complex(client=openai_client_for_openrouter, model="openai/gpt-4o-mini-2024-07-18", temperature=0.0, tools=[rewrite_test_project_file])
def add_project_references(test_project_file_path: str, project_paths_to_add_to_references: list[str]):
    """
    Your only responsibility is to add project references to the csproj test project file that are given to you.
    You are not allowed to add any other project references or remove any project references.
    Use the rewrite_project_file tool to rewrite the test project file.
    Don't insert any weird BOM characters.
    """
    if not os.path.exists(test_project_file_path):
        raise FileNotFoundError(f"Test project file not found: {test_project_file_path}")

    try:
        with open(test_project_file_path, 'r') as file:
            test_project_file_content = file.read()
    except IOError as e:
        raise IOError(f"Failed to read test project file: {e}")
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
