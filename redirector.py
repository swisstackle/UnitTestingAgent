import re
import os
from typing import List

def extract_error_files(build_errors: str) -> List[str]:
    """
    Extracts a list of unique file paths from the provided build errors.
    Filters out warnings and project-level errors.
    Works with both Windows and Linux file paths.

    Parameters:
    - build_errors (str): The raw output from the `dotnet build` command.

    Returns:
    - List[str]: A list of file paths where errors are present.
    """
    # Regex pattern to match error lines and extract file paths
    # This pattern works for both Windows and Linux paths
    error_pattern = re.compile(r'^(.+?)\((\d+),(\d+)\):\s*error\s')

    # Set to store unique file paths
    error_files = set()

    # Process each line of the build errors
    for line in build_errors.splitlines():
        match = error_pattern.match(line)
        if match:
            file_path = match.group(1)
            # Exclude project-level errors and ensure it's a code file
            if os.path.splitext(file_path)[1].lower() in ['.cs', '.vb', '.fs']:
                error_files.add(file_path)

    return list(error_files)

# Example usage (can be removed in production)
if __name__ == "__main__":
    sample_errors = """
C:\\Project\\File1.cs(10,5): error CS1002: ; expected
C:\\Project\\File8.cs(15,10): warning CS0168: Variable declared but never used
C:\\Project\\File2.cs(25,15): error CS0029: Cannot implicitly convert type 'int' to 'string'
C:\\Project\\Project.csproj(1,1): error MSB4025: The project file could not be loaded.
D:\\AnotherProject\\File3.cs(5,7): error CS0103: The name 'undefined_variable' does not exist in the current context
/home/user/Project/File4.vb(8,3): error BC30201: Expression expected
/var/www/AnotherProject/File5.fs(12,9): error FS0001: This expression was expected to have type 'int' but here has type 'string'
    """
    result = extract_error_files(sample_errors)
    print("Files with errors:")
    for file in result:
        print(file)
