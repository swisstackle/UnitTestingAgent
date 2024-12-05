import ell
from pydantic import Field
from pathlib import Path
from install_libs import install_nuget_package

@ell.tool()
def install_nuget_package_tool(
    test_project_file_path: str = Field(description="The path to the test project file (csproj). The variable is called test_project_file_path. Do not include anything else but the path. Make sure the file path has the correct format: for example: C:\\Users\\user\\Documents\\test.csproj"),
    nuget_package: str = Field(description="The nuget package to install. Do not include anything else but the package name."),
):
    # install the nuget package using inside the test project directory
    test_project_file_path = str(Path(test_project_file_path).resolve())
    return install_nuget_package(nuget_package, test_project_file_path)

@ell.tool()
def rewrite_test_project_file(
    test_project_file_path: str = Field(description="The path to the test project file (csproj). The variable is called test_project_file_path. Do not include anything else but the path. Make sure the file path is in the right format: for example: C:\\Users\\user\\Documents\\test.csproj Note how the backslashes are escaped only once." ),
    test_project_file_content: str = Field(description="The content of the test project file (csproj). The variable is called test_project_file. Do not include anything else but the content."),
):
    try:
        file_path = Path(test_project_file_path).resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(test_project_file_content, encoding='utf-8')
        return f"Successfully rewritten test project file in {file_path}"
    except Exception as e:
        return f"Error in rewrite_test_project_file: {str(e)}"
    
@ell.tool()
def rewrite_unit_test_file(
    tests_file_path: str = Field(description="The path to the unit test file. The variable is called test_file_path. Do not include anything else but the path. Make sure the file path is in the right format: for example: C:\\Users\\user\\Documents\\tests.cs Note how the backslashes are escaped only once." ),
    test_file_content: str = Field(description="The code of the unit tests. Make sure it is valid C# code without ```csharp tags."),
):
    try:
        file_path = Path(tests_file_path).resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(test_file_content, encoding='utf-8')
    except Exception as e:
        print(f"Failed to create test file '{file_path}': {str(e)}")
