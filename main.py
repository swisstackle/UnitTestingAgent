import ell
from ell import Field
from openai import Client
import os
import argparse
import subprocess
from pydantic import BaseModel, Field
from refined_unit_tests import refined_unit_tests
from pydantic import ValidationError
import time
from tools import *
import re
from refine_unit_test_code import refine_code_based_on_errors, parse_function_calls
from project_names_utils import get_project_references, find_unreferenced_csproj_files
from project_file_agents import add_project_references
from create_files import create_test_file, create_DTO_file, create_factory_file
from openai_client import openai_client

ell.init(default_client=openai_client, store='./logdir', autocommit=True, verbose=True)

@ell.simple(model="openai/gpt-4o-mini", temperature=0.0, seed=42)
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

class ActionSummary(BaseModel):
    action: str = Field(description="The action that was taken. Be detailed. Don't only summarize what was done, but also how and why it was done. You're summary can only be 200 characters long. Example: 'Changed the name space of the BankService from Tests.BankService to Engine.BankService'")

@ell.simple(model="openai/o1-mini", seed=42, temperature=0.0)
def build_unit_tests(
    function: str,
    sut: str,
    test_cases: str,
    test_project_file: str,
    additional_information: str,
    knowledge_base_content: str,
    unit_testing_engine: str,
    file_contents: list = None,
):
    """
    This method sends the system prompt and the user prompt to the LLM.
    The system prompt is used to guide the LLM in building the unit test cases.
    The user prompt is used to provide the LLM with the necessary information to build the unit test cases.
    The goal is to create code without errors and exceptions.
    To avoid namespace conflicts, you HAVE TO use namespaces directly instead of using the using statement.
    For example if you wanted to call the method "classname.foo" that resides in the namespace "thenamespace", you have to call it like this: "thenamespace.classname.foo".
    """

    user_prompt = f"""
    You are an expert in C# and .NET. You are an expert in creating unit test cases for .NET applications.
    You are given the file where the function under test is located, the name of the function under test, the unit test cases, important additional information, the knowledge base. Create the unit test cases into the test project.
    The code must be between ```csharp tags. Dont put the individual functions in ```csharp tags, but put the whole code in ```csharp tags. If you do not do this, you will be fired.
    You will probably also have to create DTO's and Factory classes. The unit testing code, the DTO's and the Factory classes must be in the same namespace and ```csharp tags.
    You MUST show your thought process for building the unit test cases.

        Follow these steps to build the unit tests for the function `{{function}}`:
        Use {unit_testing_engine} to write the unit test cases.
        # 1. Integrate the unit test cases into the test project using the following system under test where the function lays:
        ```csharp
        {{sut}}
        ```

        # 2.  Unit test Cases you must implement:
        ```csharp
        {{test_cases}}
        ```

        # 3. Make sure to utilize the additional information provided to you:
        ```
        {{additional_information}}
        ```
        <IMPORTANT>
        # Make sure to follow the knowledge base relligiously:
        ```
        {{knowledge_base_content}}
        ```
        </IMPORTANT>

        # Here are other potentially relevant files:
        ```
        {{file_contents}}
        ```
    """.format(knowledge_base_content=knowledge_base_content, unit_testing_engine=unit_testing_engine, function=function, sut=sut, test_cases=test_cases, test_project_file=test_project_file, additional_information=additional_information, file_contents=file_contents)

    return [
        ell.user(user_prompt)
    ]

def execute_build_and_tests(test_project_directory: str, test_namespace_and_classname:str):
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
        command = f"dotnet test --filter \"FullyQualifiedName={test_namespace_and_classname}\" --no-restore --no-build"
        test_process = subprocess.run(
            command,
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
            ```n
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

@ell.complex(model="openai/gpt-4o-mini", temperature=0.0, response_format=ActionSummary, seed=42)
def summarize_action(action_taken: str, unit_tests_old: str, unit_tests_new: str):
    """
    You are responsible for summarizing the action that was taken by the agent that is responsible for refining the unit test code based on error messages.
    You will be given the old and new unit test code, the old and new test project file content to compare and see what was changed. There might be no changes in those files at all and the agent only installed nuget packages.
    """
    return f"""
    The agent has taken the following action: {action_taken}.
    The old unit test code was:
    ```csharp
    {unit_tests_old}
    ```
    The new unit test code is:
    ```csharp
    {unit_tests_new}
    ```
    """

@ell.complex(model="openai/gpt-4o-mini", temperature=0.0, response_format=refined_unit_tests, seed=42)
def parse_refined_unit_tests(output: str):
    """
    You are responsivle for parsing the output of the refine_code_based_on_errors agent into RefinedUnitTests format.
    """
    return f"""
    {output}
    """

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
    parser.add_argument('--unittestingengine', type=str, required=True, help='The unit testing engine to use', choices=['xunit', 'NUnit'])
    parser.add_argument('--root_directory', type=str, required=True, help='The root directory of the solution')
    args = parser.parse_args()

    testprojectdirectory = os.path.dirname(args.csproj)


    # Initialize the optimizer
        # parse the arguments and log them for debugging
    args = parser.parse_args()
    with open(args.knowledge, 'r') as file:
        knowledge_base_content = file.read()
    file_contents = {}
    if args.files:
        for file_path in args.files:
            with open(file_path, 'r') as file:
                file_contents[file_path] = file.read()
    with open(args.sut, 'r') as file:
        sut_content = file.read()
    with open(args.csproj, 'r') as file:
        test_project_file = file.read()

    # Installing the specified unit testing engine NuGet package in the test project directory
    install_nuget_package(args.unittestingengine, testprojectdirectory)

    # Generating the unit test cases for the function under test
    # This does not spit out any code yet, just the test cases.
    test_cases = unit_test_case_generation(
        sut_content,
        args.function,
        knowledge_base_content,
        args.additional_information,
        test_project_file,
        file_contents if args.files else None
    )

    # This section is responsible for building the initial unit tests based on the provided parameters.
    # The build_unit_tests function is called with the following parameters:
    # - function: The name of the function to be tested.
    # - sut: The content of the file where the system under test is located.
    # - test_cases: The test cases generated for the function.
    # - test_project_file: The content of the test project file.
    # - additional_information: Any additional information provided about the prompt.
    # - knowledge_base_content: The content of the knowledge base.
    # - file_contents: The contents of any additional files provided, if any.
    # - unit_testing_engine: The unit testing engine to use for the tests.
    # The function returns the initial unit tests code, which is stored in the unit_tests_first variable.
    unit_tests_first = build_unit_tests(
        function=args.function,
        sut=sut_content,
        test_cases=test_cases,
        test_project_file=test_project_file,
        additional_information=args.additional_information,
        knowledge_base_content=knowledge_base_content,
        file_contents=file_contents if args.files else None,
        unit_testing_engine=args.unittestingengine
        )
    if "```csharp" in unit_tests_first:
        # Here, we are parsing the unit tests generated to identify any tool calls that need to be executed.
        # The only possible tool call that can be parsed at this point is to create the unit test file.
        # We use the parse_function_calls function to identify this tool call within the response of the previous agent.
        # Why are we not directly outputting the tool calls with build_unit_tests? The reason is because o1-mini and reflection-70b models do not support tool calls.
        function_calls = parse_function_calls(unit_tests_first, args.test_file)
        
        # Once we have identified the tool call, we iterate through each of them and execute them.
        # This is necessary to ensure that the unit test file is created before proceeding with the testing process.
        for tool_call in function_calls.tool_calls:
            tool_call()

        with open(args.test_file, 'r') as file:
            test_file_content = file.read()
        
        # Extracting namespace and class names from the test file content to identify the test class and its namespace
        namespace_match = re.search(r'namespace\s+(\w+(?:\.\w+)*)', test_file_content)
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
        project_references = get_project_references(args.test_file, args.root_directory)
        unreferenced_csproj_files = find_unreferenced_csproj_files(args.csproj, project_references)
        function_calls = add_project_references(args.csproj, unreferenced_csproj_files)
        for tool_call in function_calls.tool_calls:
            tool_call()
    else:
        raise Exception("Unit test code was not generated correctly. Please try again.")

    # This section is responsible for executing the build and tests.
    # It repeatedly attempts to build and run the tests until successful.
    # If the build fails, it prints the error messages and retries.
    build_result = ""
    while("Build and Tests Executed Successfully" not in build_result):

        # Execute the build and tests
        build_result = execute_build_and_tests(testprojectdirectory, namespace_and_classname)

        if "Build and Tests Executed Successfully" in build_result:
            print("Success! All tests passed.")
            break
        else:
            print("Tests failed. Build errors:\n" + build_result)
        # Generate unit tests
        past_actions = past_actions if 'past_actions' in locals() else []
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                unit_tests = refine_code_based_on_errors(
                    sut=sut_content,
                    test_cases=unit_tests_first if len(past_actions) == 0 else parsed.new_unit_test_code,
                    build_errors=build_result,
                    additional_information=args.additional_information,
                    knowledge_base_content=knowledge_base_content,
                    file_contents=file_contents if args.files else None,
                    function=args.function,
                    tool_outputs=past_actions,
                    test_file_path=args.test_file,
                    unit_testing_engine=args.unittestingengine
                )
                # If successful, break out of the retry loop
                break
            except ValidationError as e:
                print(f"Attempt {attempt + 1} failed due to validation error: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Unable to refine code.")
                    raise  # Re-raise the last exception if all retries fail

        # Getting the tool calls from the refined unit tests
        toolsparsed = parse_function_calls(unit_tests, args.test_file)
        # Here, we are parsing the refined unit tests to extract the action taken by the agent.
        parsed = parse_refined_unit_tests(unit_tests)
        parsed = parsed.parsed
        past_actions.append(parsed.action_taken + "!!!")
        # Executing the tool calls
        for tool_call in toolsparsed.tool_calls:
            tool_call()

if __name__ == "__main__":
    main()

