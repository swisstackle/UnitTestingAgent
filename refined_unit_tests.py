from pydantic import BaseModel, Field
from typing import List

class refined_unit_tests(BaseModel):
    new_unit_test_code: str = Field(description="The new unit test code. Make sure it is valid C# code without ```csharp tags.")
    new_test_project_file_content: str = Field(description="The new content of the test project file (csproj). The variable is called test_project_file. Do not include anything else but the content.")
    thought_process: str = Field(description="The thought process that was used to refine the unit test code or take other actions such as installing nuget packages.")
    namespace_and_classname : str = Field(description="The namespace and class name of the test file. For example: TestNameSpace.UnitTestClass")
