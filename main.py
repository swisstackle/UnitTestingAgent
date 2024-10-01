import ell
from ell import Field
from openai import Client
import os
import argparse
import subprocess

ell_key = os.getenv("MODALBOX_KEY")
openai_client = Client(
  api_key=ell_key,
  base_url="https://api.model.box/v1",
)
ell.init(default_client=openai_client, store='./logdir', autocommit=True, verbose=True)

@ell.simple(model="openai/gpt-4o", temperature=0.0)
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
@ell.simple(model="openai/gpt-4o", temperature=0.0)
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

@ell.simple(model="openai/gpt-4o", temperature=0.0)
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

@ell.simple(model="openai/gpt-4o", temperature=0.0)
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

@ell.tool()
def create_file(
    filepath: str = Field(description="The path where the file will be created."),
    content: str = Field(description="The content to write into the file."),
):
    """Creates a file at the specified filepath with the given content."""
    try:
        with open(filepath, 'w') as file:
            file.write(content)
        return f"File '{filepath}' created successfully."
    except Exception as e:
        return f"Failed to create file '{filepath}': {str(e)}"

@ell.complex(model="openai/gpt-4o", tools=[create_file])
def build_unit_tests(
    function: str,
    sut: str,
    test_cases: str,
    test_project_file: str,
    additional_information: str,
    knowledge_base_content: str,
    file_contents: list = None
):
    """
    Compiles and builds unit tests for the specified function.
    
    Use the `create_file` tool to generate a file containing the unit tests.
    
    Steps:
    1. You are given the file where the function under test is located, the name of the function under test, the unit test cases, important additional information, the knowledge base. Create the unit test cases into the test project.
    2. Use the `create_file` tool to create a file with the generated unit tests. For the arguments for `create_file`, use filepath = {test_project_file} and content should equal the unit tests that you generated.
    3. Return a confirmation message or detailed error messages if the build fails.
    """.format(knowledge_base_content=knowledge_base_content, function=function, sut=sut, test_cases=test_cases, test_project_file=test_project_file, additional_information=additional_information, file_contents=file_contents)
    return f"""
        Follow these steps to build the unit tests for the function `{function}`:

        # 1. Integrate the unit test cases into the test project using the following system under test where the function lays:
        ```csharp
        {sut}
        ```

        # 2. Ensure that the unit test cases are properly placed within the test project directory.
        ```csharp
        {test_cases}
        ```

        # 3. Make sure to utilize the additional information provided to you:
        ```
        {additional_information}
        ```

        # Make sure to follow the knowledge base relligiously:
        ```
        {knowledge_base_content}
        ```

        # Here are other potentially relevant files:
        ```
        {file_contents}
        ```
    """.format(knowledge_base_content=knowledge_base_content, function=function, sut=sut, test_cases=test_cases, test_project_file=test_project_file, additional_information=additional_information, file_contents=file_contents)

def execute_build_and_tests(test_project_directory: str):
    try:
        # Navigate to the test project directory and execute build
        build_process = subprocess.run(
            ["dotnet", "build"],
            cwd=test_project_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        build_output = build_process.stdout

        # Execute the tests only if build was successful
        test_process = subprocess.run(
            ["dotnet", "test"],
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

@ell.simple(model="openai/gpt-4o", temperature=0.0)
def refine_code_based_on_errors(sut: str, test_cases: str, build_errors: str, additional_information: str, knowledge_base_content: str, file_contents: list = None):
    """
    You are an agent responsible for refining the unit test code based on error messages.
    You will be provided with the system under test (sut), the generated unit test cases,
    any error messages from the build and test execution, and additional information.

    Your task is to analyze the error messages and refine the unit test code to resolve the issues.
    You MUST NOT create entirely new test cases but focus on fixing the existing ones.

    You MUST answer in markdown format.
    You MUST return the refined unit test code along with explanations for the changes made.
    """
    if not build_errors.strip():
        return """
            **No errors detected during the build and testing process.**

            Your unit test cases are syntactically correct and ready for execution. No refinement needed at this stage.
        """

    return f"""
        Analyze the following error messages and refine the unit test cases accordingly:

        # Error Messages:
        ```bash
        {build_errors}
        ```

        # System Under Test (SUT):
        ```csharp
        {sut}
        ```

        # Original Unit Test Cases:
        ```csharp
        {test_cases}
        ```
        # Potentially Relevant Files:
        ```
        {file_contents}
        ```
        # Additional Information:
        ```
        {additional_information}
        ```
        # Make sure to follow the knowledge base relligiously:
        ```
        {knowledge_base_content}
        ```

        # Refined Unit Test Cases:
        ```csharp
        // Refined unit tests based on the error messages
        // [Provide the corrected code here]
        ```

        # Explanation:
        - **Error 1:** [Description of the first error and how it was resolved]
        - **Error 2:** [Description of the second error and how it was resolved]
        - ...
    """

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files and prompt for knowledge generation.")
    parser.add_argument('--files', type=str, nargs='+', required=False, help='List of relevant files for the prompt (relative filepaths)')
    parser.add_argument('--knowledge', type=str, required=True, help='A path to the knowledge base (txt or md file)')
    parser.add_argument('--sut', type=str, required=True, help='Path to the file where the system under test is located')
    parser.add_argument('--function', type=str, required=True, help='The function to be tested')
    parser.add_argument('--additional_information', type=str, required=False, help='Any additional information about the prompt')
    parser.add_argument('--model', type=str, required=False, help='The model to use for the prompt')
    parser.add_argument('--csproj', type=str, required=True, help='Path to the csproj file of the test project')


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
        file_contents
    )

    # Step 2: Criticize the Generated Test Cases
    criticism = unit_test_case_criticism(
        sut_content,
        args.function,
        knowledge_base_content,
        test_cases,
        args.additional_information,
        test_project_file,
        file_contents
    )

    # Step 3: Refine the Test Cases Based on Criticism
    refined_test_cases = unit_test_case_refiner(
        sut_content,
        args.function,
        knowledge_base_content,
        criticism,
        test_cases,
        args.additional_information,
        test_project_file,
        file_contents
    )
    print(refined_test_cases)
    # Step 4: Build Unit Tests
    test_project_directory = os.path.dirname(args.csproj)
    build_results = build_unit_tests(
        args.function,
        sut_content,
        refined_test_cases,
        test_project_directory,
        args.additional_information,
        knowledge_base_content,
        file_contents
    )

    # Step 5: Execute Build and Tests
    execution_results = execute_build_and_tests(
        os.path.dirname(args.csproj),
    )

    # Step 6: Extract Build Errors (if any)
    import re

    # Extract error messages from build_results
    build_errors_match = re.search(r'```bash\n(.*?)\n```', build_results, re.DOTALL)
    build_errors = build_errors_match.group(1).strip() if build_errors_match else ""

    # Step 7: Refine Code Based on Build Errors
    final_test_cases = refine_code_based_on_errors(
        sut_content,
        refined_test_cases,
        build_errors,
        args.additional_information,
        knowledge_base_content,
        file_contents
    )

    print(final_test_cases)