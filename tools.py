import ell
from ell import Field
from install_libs import install_nuget_package

@ell.tool()
def install_nuget_package_tool(
    test_project_file_path: str = Field(description="The path to the test project file (csproj). The variable is called test_project_file_path. Do not include anything else but the path. Make sure the file path has the correct format: for example: C:\\Users\\user\\Documents\\test.csproj"),
    nuget_package: str = Field(description="The nuget package to install. Do not include anything else but the package name."),
):
    # install the nuget package using inside the test project directory
    test_project_file_path = test_project_file_path.replace('/', '\\')
    return install_nuget_package(nuget_package, test_project_file_path)

@ell.tool()
def rewrite_test_project_file(
    test_project_file_path: str = Field(description="The path to the test project file (csproj). The variable is called test_project_file_path. Do not include anything else but the path. Make sure the file path is in the right format: for example: C:\\Users\\user\\Documents\\test.csproj Note how the backslashes are escaped only once." ),
    test_project_file_content: str = Field(description="The content of the test project file (csproj). The variable is called test_project_file. Do not include anything else but the content."),
):
    test_project_file_path = test_project_file_path.replace('/', '\\')
    try:
        with open(test_project_file_path, 'w') as file:
            file.write(test_project_file_content)
        return f"Successfully rewritten test project file in {test_project_file_path}"
    except Exception as e:
        return f"Error in rewrite_test_project_file: {str(e)}"
    
@ell.tool()
def rewrite_unit_test_file(
    tests_file_path: str = Field(description="The path to the unit test file. The variable is called test_file_path. Do not include anything else but the path. Make sure the file path is in the right format: for example: C:\\Users\\user\\Documents\\tests.cs Note how the backslashes are escaped only once." ),
    test_file_content: str = Field(description="The code of the unit tests. Make sure it is valid C# code without ```csharp tags."),
):
    tests_file_path = tests_file_path.replace('/', '\\')
    try:
        # Extract the code between the ```csharp tags
        with open(tests_file_path, 'w') as file:
            file.write(test_file_content)
    except Exception as e:
        print(f"Failed to create test file '{tests_file_path}': {str(e)}")