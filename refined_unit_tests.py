from pydantic import BaseModel, Field
from typing import List

class refined_unit_tests(BaseModel):
    new_unit_test_code: str = Field(description="The new unit test code. Make sure it is valid C# code without ```csharp tags.")
    new_test_project_file_content: str = Field(description="The new content of the test project file (csproj). The variable is called test_project_file. Do not include anything else but the content.")
    thought_process: str = Field(description="The thought process that was used to refine the unit test code or take other actions such as installing nuget packages.")
    action_taken: str = Field(description="The action that was taken. Be detailed. Don't only summarize what was done, but also how and why it was done. If you made any code changes, please explain why you made the changes and what you changed specifically. Example: 'Changed the name space of the BankService from Tests.BankService to Engine.BankService' Keep it as short as possible.")
