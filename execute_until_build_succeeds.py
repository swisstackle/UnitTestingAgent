from pydantic import ValidationError
import time
from refine_unit_test_code import refine_code_based_on_errors, parse_function_calls_until_success
from execute_build_and_tests import execute_build_and_tests
from update_project_file import update_project_file
from agent_check_past_actions import check_actions
from github_bot import create_repo, create_branch, stage_and_commit, push_to_origin, get_diffs
import os
from VectorStore import VectorStore
from parse_error_resolvements import parse_error_resolvements

def stage_and_commit_and_push(root_directory:str, test_file_path, csproj_path):
    repo = create_repo(root_directory)
    branch_and_pr_name = os.path.splitext(os.path.basename(test_file_path))[0]
    branch = create_branch(repo, branch_and_pr_name)
    stage_and_commit(repo, test_file_path, "Making a commit.")
    if(csproj_path is not None):
        stage_and_commit(repo, csproj_path, "Add or edit project file")
    push_to_origin(repo, branch)

def execute_until_build_succeeds(
    testprojectdirectory,
    namespace_and_classname,
    sut_content,
    unit_tests_first,
    test_file_path,
    unit_testing_engine,
    additional_information=None,
    knowledge_base_content=None,
    file_contents=None,
    function_name=None,
    root_directory=None,
    csproj_path=None
):
    """
    Executes build and tests repeatedly until successful, refining tests as needed.
    
    Args match the original loop's requirements exactly, with some made optional
    for flexibility. The function will continue executing until tests pass successfully.
    """
    build_result = ""
    max_tries = 5
    attempt_to_resolve_errors = 0
    parsed = None

    repo = create_repo(root_directory)
    while(("All tests passed successfully!" not in build_result) and (attempt_to_resolve_errors <= max_tries)):
        # Execute the build and tests
        build_result = execute_build_and_tests(testprojectdirectory, namespace_and_classname)

        if "All tests passed successfully!" in build_result:
            print("Success! All tests passed.")
            break
        else:
            print("Tests failed. Build errors:\n" + build_result)

        # Get past 10 diffs so that we can pass it to the refiner so that he doesnt repeat the same solutions all over again.
        diffs = "\n\n".join(get_diffs(repo, 10, test_file_path))

        if(attempt_to_resolve_errors >= max_tries):
            needs_human = check_actions(diffs).parsed.needs_human
            if(needs_human):
                from refiner_with_user_feedback import refine_code_based_on_suggestion
                # commit and push code
                stage_and_commit_and_push(root_directory, test_file_path, csproj_path)
                user_response = input(f"[INPUT NEEDED] I need your help with an error or with a failing test. Please pull the code and check it out. Once you checked it out, please either let me know how to fix it (or a hint) or fix it yourself.")
                # call refine with feedback, get the result, parse it to get the code (and set "parsed" to it) and continue with execution
                test_cases = unit_tests_first
                if parsed is not None and hasattr(parsed, 'new_unit_test_code'):
                    test_cases = parsed.new_unit_test_code
                refined_unparsed = refine_code_based_on_suggestion(sut_content,
                function_name,
                additional_information,
                knowledge_base_content,
                test_file_path,
                unit_testing_engine,
                file_contents,
                user_response,
                test_cases,
                build_result)
                # Getting the tool calls from the refined unit tests
                toolsparsed = parse_function_calls_until_success(refined_unparsed, test_file_path)
                # Executing the tool calls
                for tool_call in toolsparsed.tool_calls:
                    tool_call()
                attempt_to_resolve_errors = 0

        # Generate unit tests
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                test_cases = unit_tests_first
                if parsed is not None and hasattr(parsed, 'new_unit_test_code'):
                    test_cases = parsed.new_unit_test_code
                
                unit_tests = refine_code_based_on_errors(
                    sut=sut_content,
                    test_cases=test_cases,
                    build_errors=build_result,
                    additional_information=additional_information,
                    knowledge_base_content=knowledge_base_content,
                    file_contents=file_contents,
                    function=function_name,
                    tool_outputs=diffs,
                    test_file_path=test_file_path,
                    unit_testing_engine=unit_testing_engine
                )
                break
            except ValidationError as e:
                print(f"Attempt {attempt + 1} failed due to validation error: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Unable to refine code.")
                    raise

        # Getting the tool calls from the refined unit tests
        toolsparsed = parse_function_calls_until_success(unit_tests, test_file_path)

        # Executing the tool calls
        for tool_call in toolsparsed.tool_calls:
            tool_call()

        with open(test_file_path, 'r') as file:
            test_file_content = file.read()
        namespace_and_classname = update_project_file(test_file_content, test_file_path, root_directory, csproj_path)
        stage_and_commit_and_push(root_directory, test_file_path, csproj_path)
        diffs = "\n\n".join(get_diffs(repo, 1, test_file_path))
        if(diffs.strip()):
            parse_errors_and_diffs = parse_error_resolvements(build_result, diffs).parsed
            if(parse_errors_and_diffs.key_value_pairs):
                vector_store = VectorStore.from_dict_json_file("memories.json")
                for errorPair in parse_errors_and_diffs.key_value_pairs:
                    vector_store.add_memory_dict_inmemory(errorPair.error_type, errorPair.solution)
                vector_store.save_dict_to_json("memories.json")

        attempt_to_resolve_errors = attempt_to_resolve_errors + 1
