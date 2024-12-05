import ell
import os
import argparse
from refined_unit_tests import refined_unit_tests
from pydantic import ValidationError
import time
from tools import *
import re
from refine_unit_test_code import refine_code_based_on_errors, parse_function_calls_until_success
from project_names_utils import get_project_references, find_unreferenced_csproj_files
from project_file_agents import add_project_references
from llm_clients import openai_client, openai_client_for_openrouter
from unit_test_case_generation import unit_test_case_generation
from build_unit_tests import build_unit_tests
from execute_build_and_tests import execute_build_and_tests
from github_bot import create_repo, create_branch, checkout_branch
from execute_until_build_succeeds import execute_until_build_succeeds
from update_project_file import update_project_file

ell.init(default_client=openai_client_for_openrouter, store='./logdir', autocommit=True, verbose=True)

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
    parser.add_argument('--branch', type=str, required=True, help='Name of the branch')
    args = parser.parse_args()

    # Create a Git repository object from the root directory path
    repo = create_repo(args.root_directory)
    # Get the test file name without extension to use as branch and PR name
    branch_and_pr_name = args.branch
    # Create a new Git branch with the test file name
    branch = create_branch(repo, branch_and_pr_name)
    # Switch to the newly created branch
    checkout_branch(branch)

    testprojectdirectory = os.path.dirname(args.csproj)

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
        function_calls = parse_function_calls_until_success(unit_tests_first, args.test_file)
        
        # Once we have identified the tool call, we iterate through each of them and execute them.
        # This is necessary to ensure that the unit test file is created before proceeding with the testing process.
        for tool_call in function_calls.tool_calls:
            tool_call()

        with open(args.test_file, 'r') as file:
            test_file_content = file.read()

        namespace_and_classname = update_project_file(test_file_content, args.test_file, args.root_directory, args.csproj)
    else:
        raise Exception("Unit test code was not generated correctly. Please try again.")

    # This section is responsible for executing the build and tests.
    # It repeatedly attempts to build and run the tests until successful.
    # If the build fails, it prints the error messages and retries.
    execute_until_build_succeeds(
        testprojectdirectory=testprojectdirectory,
        namespace_and_classname=namespace_and_classname,
        sut_content=sut_content,
        unit_tests_first=unit_tests_first,
        test_file_path=args.test_file,
        unit_testing_engine=args.unittestingengine,
        additional_information=args.additional_information,
        knowledge_base_content=knowledge_base_content,
        file_contents=file_contents if args.files else None,
        function_name=args.function,
        root_directory=args.root_directory,
        csproj_path=args.csproj
    )

if __name__ == "__main__":
    main()

