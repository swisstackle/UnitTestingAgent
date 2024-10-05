import ell
from ell import Field
from openai import Client
import os
import argparse
import subprocess
import re

ell_key = os.getenv("MODALBOX_KEY")
openai_client = Client(
  api_key=ell_key,
  base_url="https://api.model.box/v1",
)
ell.init(default_client=openai_client, store='./logdir', autocommit=True, verbose=True)

@ell.simple(model="openai/gpt-4o-mini", temperature=0.0)
def ask_follow_up_questions(sut: str, function: str, knowledge_base_content: str, file_contents: list = None):
    """
        You are an agent responsible for verifying the availability of all necessary files for the task.
        In the user prompt, you will be given the function under test, the file where it is located and a list of potentiallyrelevant files.
        Your task is to verify whether all the necessary dependencies of the function under test are available in the relevanbt files given.
        For example, if the function under test uses a class that is defined in another file, then that file is necessary for the test.
        Check for:
        - Other classes that are used in the function under test
        - Other functions that are used in the function under test
        - Other files that are used in the function under test
        - Other libraries that are used in the function under test
        - Other resources that are used in the function under test
        - And anything else that is necessary for the function under test to work.
        You MUST answer in markdown format.
        You MUST return an unordered list of the necessary files.
        If you need no files, just return "Thank you for the information".
        The format will be as follows (this is just an example):
        [THOUGHT PROCESS FROM THE USER PROMPT]
        Dependencies I need from you:
        - BankService
        - PayService
        - DistilService

        The dependencies are not file names, but the class names, enum names, etc. that are needed for the function under test to work.
        You MUST share your thought process with the user as outlined in the user prompt. If you don't share your thought process, you will be fired.
        """
    return """
        Follow these steps:
        # 1. Read the function under test name:
        ```csharp
        {function}
        ```
        # 2. Read the file where the function under test is located:
        ```csharp
        {sut_content}
        ```
        # 3. Read the knowledge base:
        ```
        {knowledge_base_content}
        ```
        # 4. Read the file contents of other potentially relevant files:
        ```csharp
        {file_contents}
        ```
        # 5. Find all the dependencies of {function}
        using 
        ```csharp
        {sut_content}
        ```
        # 6. Scan the main file again and the potentially relevent filesto and check which dependencies it does not define:
        Main File:
        ```csharp
        {sut_content}
        ```
        Potentially Relevant Files:
        ```csharp
        {file_contents}
        ```
        # 7. Repeat steps 5 - 6 atleast 5 times to ensure you have a comprehensive list of dependencies. If you dont do this and lay out the thought process, you will be fired.
        # 8. Return the list of dependencies that are not defined in either the main file or the potentially relevant files.
    """.format(knowledge_base_content=knowledge_base_content, function=function, sut_content=sut, file_contents=file_contents)
@ell.simple(model="openai/gpt-4o-mini", temperature=0.0)
def unit_test_case_generation(sut: str, function: str, knowledge_base_content: str, additional_information: str, test_project_file: str, file_contents: list = None):
    """
    You are an agent responsible for generating unit test cases for the function under test.
    You will be given the function under test, the file where it is located, a list of potentially relevant files and the knowledge base.
    Your task is to generate a list of unit test cases for the function under test. You MUST NOT generate any code.
    You MUST answer in markdown format.
    You MUST return an unordered list of the unit test cases.
    You MUST share your thought process with the user as outlined in the user prompt. If you don't share your thought process, you will be fired.
    You MUST cover every possible path through the function under test. If you don't do this, you will be fired.
    You MUST respect the additional information given by the user prompt. You will get fired if you don't.
    """

    return """
        Hello unit test case generation agent.
        # Knowledge Base:
        ```
        {knowledge_base_content}
        ```
        # Function Under Test:
        ```csharp
        {function}
        ```
        # File where the function under test is located:
        ```csharp
        {sut_content}
        ```
        # Potentially Relevant Files:
        ```
        {file_contents}
        ```
        # Additional Information:
        ```
        {additional_information}

        # Test Project File:
        ```
        {test_project_file}
        ```
    """.format(additional_information=additional_information, knowledge_base_content=knowledge_base_content, function=function, sut_content=sut, file_contents=file_contents, test_project_file=test_project_file)

@ell.simple(model="openai/gpt-4o-mini", temperature=0.0)
def unit_test_case_refiner(sut: str, function: str, knowledge_base_content: str, feedback: str, old_unit_test_cases: str, additional_information: str, test_project_file: str, file_contents: list = None):
    """
    You are an agent responsible for refining and adding unit test cases for the function under test based on feedback from your teacher.
    You will be given the the feedback from your teacher,  the function under test, the file where it is located, a list of potentially relevant files and the knowledge base.
    Your task is to generate a list of unit test cases for the function under test. You MUST NOT generate any code.
    You MUST answer in markdown format.
    You MUST return an unordered list of the unit test cases.
    You MUST share your thought process with the user as outlined in the user prompt. If you don't share your thought process, you will be fired.
    You MUST cover every possible path through the function under test. If you don't do this, you will be fired.
    You MUST summarize the changes you made to the old unit test cases and explain why you made those changes and refer to the feedback from your teacher.
    """

    return """
        Hello unit test case generation agent.
        # Knowledge Base:
        ```
        {knowledge_base_content}
        ```
        # Function Under Test:
        ```csharp
        {function}
        ```
        # File where the function under test is located:
        ```csharp
        {sut_content}
        ```
        # Potentially Relevant Files:
        ```
        {file_contents}
        ```
        # Feedback from teacher:
        ```
        {feedback}
        ```
        # Old Unit Test Cases:
        ```
        {old_unit_test_cases}
        ```
        # Additional Information:
        ```
        {additional_information}
        ```
        # Test Project File:
        ```
        {test_project_file}
        ```
    """.format(additional_information=additional_information,feedback=feedback, old_unit_test_cases=old_unit_test_cases, knowledge_base_content=knowledge_base_content, function=function, sut_content=sut, file_contents=file_contents, test_project_file=test_project_file)

@ell.simple(model="openai/gpt-4o-mini", temperature=0.0)
def unit_test_case_criticism(sut: str, function: str, knowledge_base_content: str, unit_test_cases: str, additional_information: str, test_project_file: str, file_contents: list = None):
    """
    You are an agent responsible for judging if your computer science student did a good job with creating unit test cases for the function under test. You are extremely critical and disagreeable.
    Do not hold back or do not try to be politically correct. Feel free to insult the student intelligence by saying "you are smarter than this" if you think they could have done better.
    You will be given the function under test, the file where it is located, a list of potentially relevant files and the knowledge base.
    Your task is to critisize the student's unit test cases and look for missing test cases, logical errors, edge cases, to check whether the student adhered to the knowledhe base and more.
    The goal is to cover every possible path through the function under test. If you miss something, you will get fired as a teacher.
    You MUST answer in markdown format.
    You MUST return an unordered list of missing unit test cases.
    You MUST respect the additional information given by the user prompt. You will get fired if you don't.
    You MUST ensure that all possible combinations of inputs are tested (mathematically speaking), if you dont do this, you will get fired.
    # Knowledge Base:
    ```
    {knowledge_base_content}
    ```
    # Function Under Test:
    ```csharp
    {function}
    ```
    # File where the function under test is located:
    ```csharp
    {sut_content}
    ```
    # Potentially Relevant Files:
    ```
    {file_contents}
    ```
    # Test Project File:
    ```
    {test_project_file}
    ```
    You must provide atleast 1 ciriticism unless you reallt cant find one. If you really cant find one, say "FINISHED".
    """.format(knowledge_base_content=knowledge_base_content, function=function, sut_content=sut, file_contents=file_contents, test_project_file=test_project_file)

    return """
        Hello teacher, here are the unit test cases and my thought process you need to judge:
        ```
        {unit_test_cases}
        ```
        # Additional Information:
        ```
        {additional_information}
        ```
    """.format(additional_information=additional_information, unit_test_cases=unit_test_cases)


@ell.simple(model="openai/gpt-4o-mini")
def build_unit_tests(
    function: str,
    sut: str,
    test_cases: str,
    test_project_file: str,
    additional_information: str,
    knowledge_base_content: str,
    file_contents: list = None,
):
    """
    This method sends the system prompt and the user prompt to the LLM.
    The system prompt is used to guide the LLM in building the unit test cases.
    The user prompt is used to provide the LLM with the necessary information to build the unit test cases.
    The goal is to create code without errors and exceptions.
    """
    system_prompt = """
    You are an expert in C# and .NET. You are an expert in creating unit test cases for .NET applications.
    You are given the file where the function under test is located, the name of the function under test, the unit test cases, important additional information, the knowledge base. Create the unit test cases into the test project.
    The code must be between ```csharp tags. Dont put the individual functions in ```csharp tags, but put the whole code in ```csharp tags. If you do not do this, you will be fired.
    You MUST show your thought process for building the unit test cases.
    """

    user_prompt = f"""
        Follow these steps to build the unit tests for the function `{{function}}`:

        # 1. Integrate the unit test cases into the test project using the following system under test where the function lays:
        ```csharp
        {{sut}}
        ```

        # 2. Ensure that the unit test cases are properly placed within the test project directory.
        ```csharp
        {{test_cases}}
        ```

        # 3. Make sure to utilize the additional information provided to you:
        ```
        {{additional_information}}
        ```

        # Make sure to follow the knowledge base relligiously:
        ```
        {{knowledge_base_content}}
        ```

        # Here are other potentially relevant files:
        ```
        {{file_contents}}
        ```
    """.format(knowledge_base_content=knowledge_base_content, function=function, sut=sut, test_cases=test_cases, test_project_file=test_project_file, additional_information=additional_information, file_contents=file_contents)

    return [
        ell.system(system_prompt),
        ell.user(user_prompt)
    ]

def create_test_file(test_cases: str, test_project_file: str):
    """
    This method createsa test file and inserts the code in test_cases into it.
    If the file already exists, it will be overwritten.
    We will use try catch to handle the file creation.
    The code in test_cases is between ```csharo tags (markdown formatting).
    This function first extracts the code between the ```csharp tags and then writes it to the test project file.
    """
    try:
        # Extract the code between the ```csharp tags
        test_cases_code = str(test_cases).split("```csharp")[1].split("```")[0]
        print("test cases code: " + test_cases_code)
        print("test project file: " + test_project_file)
        with open(test_project_file, 'w') as file:
            file.write(test_cases_code)
    except Exception as e:
        print(f"Failed to create test file '{test_project_file}': {str(e)}")

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
def install_nuget_package(
    test_project_file_path: str = Field(description="The path to the test project file (csproj). The variable is called test_project_file_path. Do not include anything else but the path. Make sure the file path has the correct format: for example: C:\\Users\\user\\Documents\\test.csproj"),
    nuget_package: str = Field(description="The nuget package to install. Do not include anything else but the package name."),
):
    # install the nuget package using inside the test project directory
    test_project_file_path = test_project_file_path.replace('/', '\\')
    try:
        subprocess.run(["dotnet", "add", "package", nuget_package], cwd=os.path.dirname(test_project_file_path), check=True)
        return f"Successfully installed nuget package {nuget_package} in {test_project_file_path}"
    except Exception as e:
        return f"Error in install_nuget_package: {str(e)}"


def execute_build_and_tests(test_project_directory: str, test_file_path:str):
    try:
        # Navigate to the test project directory and execute build
        build_process = subprocess.run(
            ["dotnet", "build", "-consoleloggerparameters:ErrorsOnly"],
            cwd=test_project_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        build_output = build_process.stdout

        # Execute the tests only if build was successful
        test_process = subprocess.run(
            ["dotnet", "test", test_file_path],
            cwd=test_project_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        test_output = test_process.stdout

        return f"""
            ```bash
            {build_output}
            ```
            ```bash
            {test_output}
            ```
            **Build and Tests Executed Successfully.**
        """
    except subprocess.CalledProcessError as e:
        error_message = e.stderr if e.stderr else e.stdout
        return f"""
            ```bash
            {error_message}
            ```
            **An error occurred during build or testing. Please review the above error messages.**
        """
@ell.complex(model="openai/gpt-4o-mini", temperature=0.0, tools=[rewrite_test_project_file, install_nuget_package])
def refine_code_based_on_errors(sut: str, test_cases: str, test_project_file_path: str, function: str, build_errors: str, additional_information: str, knowledge_base_content: str, test_project_file: str, file_contents: list = None, tool_outputs: str = None):
    """
        This method sends the system prompt and the user prompt to the LLM.
        The system prompt is used to guide the LLM in refining the unit test code based on error messages.
        The user prompt is used to provide the LLM with the necessary information to refine the unit test code.
        The goal is to create code without errors and exceptions.
        args:
            function: the function under test
            sut: the file where the function under test is located
            test_cases: the unit test cases code
            build_errors: the build errors
            additional_information: any additional information about how to create the unit test cases
            knowledge_base_content: the knowledge base content
            test_project_file: the test project file (csproj file)
            file_contents: the potentially relevant files
    """
    system_prompt = """
    You are an agent responsible for refining the unit test code based on error messages.
    You will be provided with the system under test (sut), the generated unit test cases,
    any error messages from the build and test execution, and additional information.
    Your task is to analyze the error messages and refine the unit test code to resolve the issues.
    You MUST NOT create entirely new test cases but focus on fixing the existing ones.
    You MUST answer in markdown format.
    You MUST return the refined unit test code along with explanations for the changes made.
    You MUST show your thought process for refining the unit test cases.
    The code must be between ```csharp tags. If you do not do this, you will be fired.
    You can use the rewrite_test_project_file tool to rewrite the test project file if there is need.
    You can use the install_nuget_package tool to install any nuget package if there is need.
    You are also potentially given tool outputs from past tool calls. Those tool called might have errors or warnings that you need to fix. 
    <important>If the tool errors indicate that the nuget package doesnt exist, dont try to install the same package twice. Either try a different variation of the name of the package or try a completely different approach</important>
    """

    user_prompt = """
            **No errors detected during the build and testing process.**

            Your unit test cases are syntactically correct and ready for execution. No refinement needed at this stage.
        """
    user_prompt_with_errors = f"""
        Analyze the following error messages and refine the unit test cases accordingly:
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

        # Original Unit Test Cases:
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
        # Tool Outputs:
        ```
        {{tool_outputs}}
        ```

        # Refined Unit Test Cases:
        ```csharp
        // Refined unit tests based on the error messages
        // []
        ```

        # Explanation:
        - **Error 1:** [Description of the first error and how it was resolved]
        - **Error 2:** [Description of the second error and how it was resolved]
        - ...
    """.format(knowledge_base_content=knowledge_base_content,test_project_file_path=test_project_file_path.replace('\\', '/'), build_errors=build_errors, function=function, sut=sut, test_cases=test_cases, test_project_file=test_project_file, additional_information=additional_information, file_contents=file_contents, tool_outputs=tool_outputs)
    if not build_errors.strip():
        return [
            ell.system(system_prompt),
            ell.user(user_prompt)
        ]
    return [
        ell.system(system_prompt),
        ell.user(user_prompt_with_errors)
    ]

def main():
    parser = argparse.ArgumentParser(description="Generate and execute unit tests.")
    parser.add_argument('--files', type=str, nargs='+', required=False, help='List of relevant files for the prompt (relative filepaths)')
    parser.add_argument('--knowledge', type=str, required=True, help='A path to the knowledge base (txt or md file)')
    parser.add_argument('--sut', type=str, required=True, help='Path to the file where the system under test is located')
    parser.add_argument('--function', type=str, required=True, help='The function to be tested')
    parser.add_argument('--additional_information', type=str, required=False, help='Any additional information about the prompt')
    parser.add_argument('--model', type=str, required=False, help='The model to use for the prompt')
    parser.add_argument('--csproj', type=str, required=True, help='Path to the csproj file of the test project')
    parser.add_argument('--test_file', type=str, required=True, help='Path where the test file will be created')
    args = parser.parse_args()

    # Initialize the optimizer
        # parse the arguments and log them for debugging
    args = parser.parse_args()
    with open(args.knowledge, 'r') as file:
        knowledge_base_content = file.read()
    file_contents = []
    if args.files:
        for file_path in args.files:
            with open(file_path, 'r') as file:
                file_contents.append(file.read())
    with open(args.sut, 'r') as file:
        sut_content = file.read()
    with open(args.csproj, 'r') as file:
        test_project_file = file.read()


    # Step 1: Generate Unit Test Cases
    test_cases = unit_test_case_generation(
        sut_content,
        args.function,
        knowledge_base_content,
        args.additional_information,
        test_project_file,
        file_contents if args.files else None
    )
    # Step 2: Criticize the Generated Test Cases
    # criticism = unit_test_case_criticism(
    #     sut_content,
    #     args.function,
    #     knowledge_base_content,
    #     test_cases,
    #     args.additional_information,
    #     test_project_file,
    #     file_contents if args.files else None
    # )
    # test_cases = unit_test_case_refiner(
    #     sut_content,
    #     args.function,
    #     knowledge_base_content,
    #     criticism,
    #     test_cases,
    #     args.additional_information,
    #     test_project_file,
    #     file_contents if args.files else None
    # )
    #
    unit_tests = build_unit_tests(
        function=args.function,
        sut=sut_content,
        test_cases=test_cases,
        test_project_file=test_project_file,
        additional_information=args.additional_information,
        knowledge_base_content=knowledge_base_content,
        file_contents=file_contents if args.files else None
        )
    build_result = ""
    while("Build and Tests Executed Successfully" not in build_result):
        if "```csharp" in unit_tests:
            create_test_file(unit_tests, args.test_file)
            print("created test file in " + args.test_file)
        # Execute the build and tests
        build_result = execute_build_and_tests(os.path.dirname(args.csproj), args.test_file)

        if "Build and Tests Executed Successfully" in build_result:
            print("Success! All tests passed.")
        else:
            print("Tests failed. Build errors:\n" + build_result)
        # Generate unit tests
        tool_outputs = tool_outputs if 'tool_outputs' in locals() else ""
        unit_tests = refine_code_based_on_errors(
            sut=sut_content,
            test_cases=unit_tests,
            build_errors=build_result,
            additional_information=args.additional_information,
            knowledge_base_content=knowledge_base_content,
            test_project_file=test_project_file,
            file_contents=file_contents if args.files else None,
            function=args.function,
            test_project_file_path=rf'{args.csproj}',
            tool_outputs=tool_outputs
        )
        # call all tool functions in unit_tests
        # build a concentated string of the outputs of the tool calls
        tool_outputs = unit_tests.call_tools_and_collect_as_message()
        print(tool_outputs)
if __name__ == "__main__":
    main()