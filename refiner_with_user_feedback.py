import argparse
from pathlib import Path
from execute_until_build_succeeds import execute_until_build_succeeds
from tools import rewrite_unit_test_file
from llm_clients import anthropic_client, openai_client
import ell

@ell.simple(model="claude-3-5-sonnet-20241022", max_tokens=8000, client=anthropic_client, temperature=0.0)
def refine_code_based_on_suggestion(sut: str, function: str, additional_information: str, knowledge_base_content: str, test_file_path: str, unit_testing_engine: str, file_contents: list = None, suggestion_from_developer : str, test_cases_code : str):
    # I want to format all entries in file_contants in markdown code blocks
    # It should be a formatted string in markdown
    formatted_file_contents = ""
    for file_path, file_content in file_contents.items():
        formatted_file_contents += f"# {file_path}\n```\n{file_content}\n```\n"

    user_prompt = """
You are a senior C# developer with expertise in unit approval testing. Your task is to implement a suggestion from a real human senior software developer.
You are a test after development developer, which means that you have to adjust the unit test code so that the tests pass. This is also called "approval testing."
Make sure the unit test class will be in the "Enveritus2.Test" namespace.
Please review the following information carefully:

<suggestion>
{suggestion_from_developer}
</suggestion>

<relevant_files>
{formatted_file_contents}
</relevant_files>

<unit_test_code>
{test_cases_code}
</unit_test_code>

You solely are responsible for implementing the suggestion. Do NOTHING else.
Make sure the unit test class will be in the "Enveritus2.Test" namespace.

<function_under_test>
{function}
</function_under_test>

You solely are responsible for implementing the suggestion. Do NOTHING else.
Make sure the unit test class will be in the "Enveritus2.Test" namespace.

<system_under_test>
{sut}
</system_under_test>

You solely are responsible for implementing the suggestion. Do NOTHING else.
Make sure the unit test class will be in the "Enveritus2.Test" namespace.

<test_file_path>
{test_file_path}
</test_file_path>


You solely are responsible for implementing the suggestion. Do NOTHING else.
Make sure the unit test class will be in the "Enveritus2.Test" namespace.

<additional_info>
{additional_information}
</additional_info>

You solely are responsible for implementing the suggestion. Do NOTHING else.
Make sure the unit test class will be in the "Enveritus2.Test" namespace.

<knowledge_base>
{knowledge_base_content}
</knowledge_base>

You solely are responsible for implementing the suggestion. Do NOTHING else.
Make sure the unit test class will be in the "Enveritus2.Test" namespace.


Now, analyze the situation and plan any necessary changes. Wrap your analysis inside <test_code_analysis> tags:

<test_code_analysis>
1. Examine the developer's suggestion:
   - Extract the specific changes requested by the developer
   - Map each requested change to the corresponding code location
   - Identify any constraints or requirements in the suggestion
   - Validate that the suggestion aligns with approval testing principles

2. Review the function under test and its relationship to the unit test code:
   - Map each unit test to the corresponding part of the function under test.
   - Count the total number of tests.
   - Check for any inconsistencies between the test code and the function under test.

3. Determine if changes are necessary in the unit testing code:
   - Identify specific lines or sections that may need modification.
   - Review naming conventions and ensure they follow C# best practices.

4. Identify potential namespace conflicts:
   - List places where fully qualified names might resolve issues.

5. Review relevant files for context:
   - Note any information from these files that could help resolve the issues.

6. Plan necessary changes to make all tests pass:
   - Outline specific modifications needed for each identified issue.

7. Relate each line of code to the knowledge base:
   - For each planned change, reference the relevant part of the knowledge base.

8. Confirm that the entire code will be provided:
    - Even if no changes are necessary, prepare to output the full code.
</test_code_analysis>

Based on your analysis, implement the necessary changes to the unit test code. Follow these important guidelines:

1. Only modify the unit testing code, not the test project file.
2. Provide the entire unit test code file, even if there are no changes.
3. Format the output code with 4-space indentation and use new lines to separate method declarations, block statements, and logical sections of code.
4. Comment on each line of code, referencing the knowledge base or explaining why it doesn't apply.

Present your final unit test code in the following format:

```csharp
// Entire unit test code file goes here, with comments for each line.
// Include ALL code, even unchanged sections.
// Format: 4-space indentation, new lines for readability.
// Each line should have a comment referencing the knowledge base or explaining why it doesn't apply.
// After each message signature in the same line, write "DO NOT REMOVE THIS METHOD EVER" as a comment.
```

Remember to rigorously follow the program logic and the knowledge base. Ensure that you provide the complete code.

You solely are responsible for implementing the suggestion. Do NOTHING else.
Make sure the unit test class will be in the "Enveritus2.Test" namespace.
    """.format(
        knowledge_base_content=knowledge_base_content,
        test_file_path=test_file_path,
        function=function,
        sut=sut,
        additional_information=additional_information,
        formatted_file_contents=formatted_file_contents,
        unit_testing_engine=unit_testing_engine,
        suggestion_from_developer=suggestion_from_developer,
        test_cases_code=test_cases_code
    )
    if not build_errors.strip():
        return [
            ell.user("Build and Tests Executed Successfully")
        ]
    return [
        ell.user(user_prompt)
    ]

def main():
    parser = argparse.ArgumentParser(description='Refine unit tests based on developer suggestion and validate implementation')
    
    # Required arguments
    parser.add_argument('--csproj', required=True, help='Directory containing the test project')
    parser.add_argument('--namespace-classname', required=True, help='Namespace and class name in format Namespace.ClassName')
    parser.add_argument('--test_file', required=True, help='Path to the test file')
    parser.add_argument('--developer-suggestion', required=True, help='Suggestion from senior developer')
    parser.add_argument('--sut', required=True, help='The path to the system under test file')
    parser.add_argument('--unit-testing-engine', required=True, default='NUnit', help='Unit testing framework being used')
    parser.add_argument('--root-directory', required=True, help='Root directory of the project')
    parser.add_argument('--function', required=True, help='Name of the function being tested')
    # Optional arguments
    parser.add_argument('--additional-info', help='Additional context information')
    parser.add_argument('--knowledge', help='Path to knowledge base content')
    parser.add_argument('--files', help='Relevant Files')
    
    args = parser.parse_args()

    # Load knowledge base content if provided
    knowledge_base_content = ""
    if args.knowledge and Path(args.knowledge).exists():
        with open(args.knowledge, 'r') as f:
            knowledge_base_content = f.read()

    sut_content = ""
    if args.sut and Path(args.sut).exists():
        with open(args.sut, 'r') as f:
            sut_content = f.read()

    # Load current test file content
    with open(args.test_file, 'r') as f:
        current_test_content = f.read()

    # Collect file contents
    file_contents = {}
    if args.files:
        for file_path in args.files:
            with open(file_path, 'r') as file:
                file_contents[file_path] = file.read()

    try:
        # Stage 1: Apply developer's suggestion
        print("Stage 1: Implementing developer's suggestion...")
        suggestion_result = refine_code_based_on_suggestion(
            test_cases_code=current_test_content,
            function=args.function or "",
            additional_information=args.additional_info or "",
            knowledge_base_content=knowledge_base_content or "",
            test_file_path=args.test_file_path,
            unit_testing_engine=args.unit_testing_engine,
            file_contents=file_contents or [],
            suggestion_from_developer=args.developer_suggestion,
            sut=sut_content
        )

        # Parse the suggestion implementation result
        toolsparsed = parse_function_calls(suggestion_result, args.test_file_path)
        
        # Apply the suggested changes
        for tool_call in toolsparsed.tool_calls:
            tool_call()

        # Read the updated test content
        with open(args.test_file_path, 'r') as f:
            updated_test_content = f.read()

        # Stage 2: Validate and refine implementation
        print("Stage 2: Validating and refining implementation...")
        execute_until_build_succeeds(
            testprojectdirectory=args.test_project_dir,
            namespace_and_classname=args.namespace_classname,
            sut_content=sut_content,
            unit_tests_first=updated_test_content,
            test_file_path=args.test_file_path,
            unit_testing_engine=args.unit_testing_engine,
            additional_information=args.additional_info,
            knowledge_base_content=knowledge_base_content,
            file_contents=file_contents,
            function_name=args.function or ""
            root_directory=args.root_directory,
            csproj_path=args.csproj
        )
