#add all imports here
import ell
# add importds for rewrite_unit_test_file and rewrite_test_project_file
from tools import rewrite_unit_test_file

@ell.simple(model="mattshumer/reflection-70b", temperature=0.0, seed=42)
def refine_code_based_on_errors(sut: str, test_cases: str, test_project_file_path: str, function: str, build_errors: str, additional_information: str, knowledge_base_content: str, test_project_file: str, test_file_path: str, unit_testing_engine: str, file_contents: list = None, tool_outputs: str = None):

    user_prompt = """
Your only responsibility is to find out whether the source of the errors of the build of unit test code are because of the unit testing code, DTOs or Factory code or a combination of all of them.
You will be provided with the system under test (sut), the unit testing code, the DTOs and Factory code, any error messages from the build and test execution, and the content of the test project file (csproj).
You are only allowed to change the unit testing code and !NOT! the test project file
<important>The most important thing is that you follow the program logic of the steps. If you do not do this, you will be fired.
YOU ARE TO RESPOND IN MARKDOWN</important>

            **No errors detected during the build and testing process.**

            Your unit test cases are syntactically correct and ready for execution. No refinement needed at this stage.
        """
    user_prompt_with_errors = f"""
Your only responsibility is to find out whether the source of the errors of the build of unit test code are because of the unit testing code or not.
You will be provided with the system under test (sut), the unit testing code, any error messages from the build and test execution, and the content of the test project file (csproj).
You are only allowed to change the unit testing code and !NOT! the test project file
<important>The most important thing is that you follow the program logic of the steps. If you do not do this, you will be fired.
YOU ARE TO RESPOND IN MARKDOWN</important>

        Tools you can use: rewrite_project_file

        Follow the following steps:

        if(any changes in the unit testing code are neessary):
	        changes.append("rewrote unit testing code")

        if(using statements are correct && some sort of object can't be found)
	        This means there likely is a namespace conflict. Use the fully qualified name for the object / function

        if(past_actions contains an item from changes):
	        redo the steps without including the change that is included in past_actions or conclude that no changes are necessary depending on whether you think if there is more to consider!

        Respond with entire unit test code file in output tags, even if there are not any changes! Include the entire file! No partials! Enclose it in ```csharp tags!

        if(not entire file was provided)
	        redo providing the entire final unit test code
        
        if(there is no error but not all tests passed):
	        change the test cases so that all tests pass. This is testing after development philosophy.

        if(did you not provide the entire file?!!!):
	        redo providing the entire final unit test code

        !Format the output code with 4-space indentation, and use new lines to separate method declarations, block statements, and logical sections of code.!

        # Function Under Test:
        ```csharp
        {{function}}
        ```
        # Error Messages:
        ```bash
        {{build_errors}}
        ```

        # System Under Test (SUT):
        ```csharp
        {{sut}}
        ```

        # Unit Test Code:
        ```csharp
        {{test_cases}}
        ```
        # Potentially Relevant Files:
        ```
        {{file_contents}}
        ```
        # Additional Information:
        ```
        {{additional_information}}
        ```
        # Make sure to follow the knowledge base relligiously:
        ```
        {{knowledge_base_content}}
        ```
        # test_project_file_path:
        ```
        {{test_project_file_path}}
        ```
        # test_project_file:
        ```csharp
        {{test_project_file}}
        ```
        # test_file_path:
        ```
        {{test_file_path}}
        ```
        # Your past actions that you took and should not repeat:
        ```
        {{tool_outputs}}
        ```
    """.format(
        knowledge_base_content=knowledge_base_content,
        test_file_path=test_file_path,
        build_errors=build_errors,
        function=function,
        sut=sut,
        test_cases=test_cases,
        test_project_file=test_project_file,
        additional_information=additional_information,
        file_contents=file_contents,
        tool_outputs=tool_outputs,
        test_project_file_path=test_project_file_path,
        unit_testing_engine=unit_testing_engine
    )
    if not build_errors.strip():
        return [
            ell.user(user_prompt)
        ]
    return [
        ell.user(user_prompt_with_errors)
    ]

@ell.simple(model="mattshumer/reflection-70b", temperature=0.0, seed=42)
def refine_dto_file(sut: str, test_cases: str, test_project_file_path: str, function: str, build_errors: str, additional_information: str, knowledge_base_content: str, test_project_file: str, test_file_path: str, unit_testing_engine: str, file_contents: list = None, tool_outputs: str = None):
    return ""

@ell.simple(model="mattshumer/reflection-70b", temperature=0.0, seed=42)
def refine_factor_file(sut: str, test_cases: str, test_project_file_path: str, function: str, build_errors: str, additional_information: str, knowledge_base_content: str, test_project_file: str, test_file_path: str, unit_testing_engine: str, file_contents: list = None, tool_outputs: str = None):
    return ""


def parse_function_calls(reasoningoutput:str, unit_test_path:str):
    """
    Your only responsibility is to parse the reasoning output of the LLM and return the function calls that are needed.
    If there are no function calls, return an empty list.
    """
    return f"""A
    {reasoningoutput}
    # Unit Test Path:
    {unit_test_path}
    """
