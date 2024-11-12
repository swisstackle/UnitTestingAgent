import ell
import os
import argparse
from refined_unit_tests import refined_unit_tests
from pydantic import ValidationError
import time
from tools import *
import re
from refine_unit_test_code import refine_code_based_on_errors, parse_function_calls
from project_names_utils import get_project_references, find_unreferenced_csproj_files
from project_file_agents import add_project_references
from llm_clients import openai_client
from unit_test_case_generation import unit_test_case_generation
from build_unit_tests import build_unit_tests
from execute_build_and_tests import execute_build_and_tests
from github_bot import *

ell.init(default_client=openai_client, store='./logdir', autocommit=True, verbose=True)

@ell.complex(model="openai/gpt-4o-mini", temperature=0.0, client=openai_client, response_format=refined_unit_tests, seed=42)
def parse_refined_unit_tests(output: str):
    """
    You are responsivle for parsing the output of the refine_code_based_on_errors agent into RefinedUnitTests format.
    """
    return f"""
    {output}
    """
def update_project_file(test_file_content, test_file_path, root_directory, project_file_path):
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
        project_references = get_project_references(test_file_path, root_directory)
        unreferenced_csproj_files = find_unreferenced_csproj_files(project_file_path, project_references)
        function_calls = add_project_references(project_file_path, unreferenced_csproj_files)
        for tool_call in function_calls.tool_calls:
            tool_call()
        return namespace_and_classname

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

    #repo = create_repo(args.root_directory)
    #branch = create_branch(repo, args.test_file)
    #checkout_branch(branch)

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

        namespace_and_classname = update_project_file(test_file_content, args.test_file, args.root_directory, args.csproj)
        

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
            #stage_and_commit(repo, [args.test_file], "new commit")
            #push_to_origin(repo, branch)
            #random_nr = 1;
            #create_pr_to_master_on_lean("New Pr " + random_nr, "PR for " + arg.test_file, args.test_file)
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
        with open(args.test_file, 'r') as file:
            test_file_content = file.read()

        update_project_file(test_file_content, args.test_file, args.root_directory, args.csproj)

if __name__ == "__main__":
    main()

