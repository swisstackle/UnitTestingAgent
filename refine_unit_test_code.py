#add all imports here
import ell
# add importds for rewrite_unit_test_file and rewrite_test_project_file
from tools import rewrite_unit_test_file

@ell.simple(model="openai/o1-mini", temperature=0.0, seed=42)
def refine_code_based_on_errors(sut: str, test_cases: str, function: str, build_errors: str, additional_information: str, knowledge_base_content: str, test_file_path: str, unit_testing_engine: str, file_contents: list = None, tool_outputs: str = None):
    # I want to format all entries in file_contants in markdown code blocks
    # It should be a formatted string in markdown
    formatted_file_contents = ""
    for file_path, file_content in file_contents.items():
        formatted_file_contents += f"# {file_path}\n```\n{file_content}\n```\n"

    user_prompt = """
You are an expert C# developer specializing in unit testing. Your task is to analyze and potentially modify unit test code to resolve build errors or test failures. Please review the following information carefully:

<relevant_files>
{{formatted_file_contents}}
</relevant_files>

<unit_test_code>
{{test_cases}}
</unit_test_code>

<build_errors>
{{build_errors}}
</build_errors>

<function_under_test>
{{function}}
</function_under_test>

<system_under_test>
{{sut}}
</system_under_test>

<test_file_path>
{{test_file_path}}
</test_file_path>

<additional_info>
{{additional_information}}
</additional_info>

<knowledge_base>
{{knowledge_base_content}}
</knowledge_base>

<past_actions>
{{tool_outputs}}
</past_actions>

Now, analyze the situation and plan any necessary changes. Wrap your analysis inside <test_code_analysis> tags:

<test_code_analysis>
1. Examine the build errors and unit test code:
   - List each build error and its potential cause.
   - Categorize errors (e.g., syntax, reference, compilation).
   - Identify any patterns or similarities in the errors.
   - Count the total number of errors.

2. Review the function under test and its relationship to the unit test code:
   - Map each unit test to the corresponding part of the function under test.
   - Count the total number of tests.
   - Check for any inconsistencies between the test code and the function under test.

3. Determine if changes are necessary in the unit testing code:
   - Identify specific lines or sections that may need modification.
   - Review naming conventions and ensure they follow C# best practices.

4. Check using statements and object references:
   - List any missing or incorrect using statements.
   - Note any objects that are not recognized.

5. Identify potential namespace conflicts:
   - List places where fully qualified names might resolve issues.

6. Review relevant files for context:
   - Note any information from these files that could help resolve the issues.

7. Ensure no repetition of past actions:
   - Cross-check your planned changes against the past actions.

8. Plan necessary changes to make all tests pass:
   - Outline specific modifications needed for each identified issue.

9. Relate each line of code to the knowledge base:
   - For each planned change, reference the relevant part of the knowledge base.

10. Confirm that the entire code will be provided:
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
```

Remember to rigorously follow the program logic and the knowledge base, and avoid repeating any past actions listed above. Ensure that you provide the complete code, not just the modified sections.
    """.format(
        knowledge_base_content=knowledge_base_content,
        test_file_path=test_file_path,
        build_errors=build_errors,
        function=function,
        sut=sut,
        test_cases=test_cases,
        additional_information=additional_information,
        formatted_file_contents=formatted_file_contents,
        tool_outputs=tool_outputs,
        unit_testing_engine=unit_testing_engine
    )
    if not build_errors.strip():
        return [
            ell.user(user_prompt)
        ]
    return [
        ell.user(user_prompt_with_errors)
    ]


@ell.complex(model="openai/gpt-4o-mini", temperature=0.0, tools=[rewrite_unit_test_file])
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
