
import ell
from tools import rewrite_unit_test_file
from LlmClientFactory import LlmClientFactory, ClientType
from format_with_line_numbers import format_code_with_line_numbers
from VectorStore import VectorStore
from pydantic import BaseModel, Field, ValidationError

client = LlmClientFactory.get_client(ClientType.OPENROUTER)

class BuildErrors(BaseModel):
    builderrors: list[str] = Field(description="the list of build errors with their error code and description. Do not include the stacktrace.")

class CodeRefiner:
    
    @ell.complex(model="openai/gpt-4o-mini", max_tokens=8000, client=client, temperature=0.0, response_format=BuildErrors)
    def split_up_build_errors(self, build_errors: str) -> BuildErrors:
        """
        You are an agent who's responsibility it is to take in a string of build errors and split them up into their respective error codes and descriptions.
        """

        return f"""
            Here are the build errors:
            {build_errors}
        """

    @ell.simple(model="qwen/qwen-2.5-coder-32b-instruct", max_tokens=8000, client=client, temperature=0.0)
    def refine_code_based_on_errors(self, sut: str, test_cases: str, function: str, build_errors: str, additional_information: str, knowledge_base_content: str, test_file_path: str, unit_testing_engine: str, file_contents: list = None, tool_outputs: str = None):
        # I want to format all entries in file_contants in markdown code blocks
        # It should be a formatted string in markdown

        formatted_file_contents = ""
        for file_path, file_content in file_contents.items():
            formatted_file_contents += f"# {file_path}\n\n{format_code_with_line_numbers(file_content)}\n\n"
        sut = format_code_with_line_numbers(sut)
        test_cases = format_code_with_line_numbers(test_cases)

        vector_store = VectorStore.from_dict_json_file("memories.json")

        build_error_list = self.split_up_build_errors(build_errors).parsed.builderrors
        memories = ""
        for error in build_error_list:
            results = vector_store.search_dict(error)
            for result in results:
                if(result["relevan"] > 0.5):
                    memories += f"# {error}:\n  Possible Solution: " + str(result["Value"]) + "\n\n"

        repeated = "\n\nYou solely are responsible for eliminating build errors and test failures. Make sure to review past actions. Use the line numbers to locate errors and reference the line number where the error occurs. Make sure the unit test class will be in the \"Enveritus2.Test\" namespace. Make sure to output the entire code\n\n"

        user_prompt = """
        You are a senior C# developer with expertise in unit approval testing. Your task is to analyze, modify, and improve unit approval test code to resolve build errors and test failures.
        However, adding or removing test cases is not in the scope. You solely are responsible for eliminating build errors and test failures.
        You are a test after development developer, which means that you have to adjust the unit test code so that the tests pass. This is also called "approval testing."
        Make sure the unit test class will be in the "Enveritus2.Test" namespace.
        Please review the following information carefully:

        <relevant_files>
        {formatted_file_contents}
        </relevant_files>

        <unit_test_code>
        {test_cases}
        </unit_test_code>

        <failed_tests or build_errors>
        {build_errors}
        </failed_tests or build_errors>

        {repeated}

        <function_under_test>
        {function}
        </function_under_test>

        {repeated}

        <system_under_test>
        {sut}
        </system_under_test>

        {repeated}

        <test_file_path>
        {test_file_path}
        </test_file_path>

        {repeated}

        <additional_info>
        {additional_information}
        </additional_info>

        {repeated}

        <knowledge_base>

        <general knowledge passed by the senior software developer>
        {knowledge_base_content}
        </general knowledge passed by the senior software developer>

        <your own memories from the vector database on how to potentially solve the errors>
        {memories}
        </your own memories from the vector database on how to potentially solve the errors>

        </knowledge_base>

        {repeated}

        <past_actions> 
        {tool_outputs}
        </past_actions>

        {repeated}

        Now, analyze the situation and plan any necessary changes. Wrap your analysis inside <test_code_analysis> tags:

        <test_code_analysis>
        1. Examine the build errors and unit test code:
           - List each build error and its potential cause.
           - Categorize errors (e.g., syntax, reference, compilation).
           - Identify any patterns or similarities in the errors.
           - Count the total number of errors.
           - List the file and line number where the error occurs.

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
            unit_testing_engine=unit_testing_engine,
            repeated=repeated,
            memories=memories
        )
        # Append user prompt to file "promptlog.txt"
        with open("promptlog.txt", "a") as f:
            f.write(user_prompt + "\n\n\n")
        if not build_errors.strip():
            return [
                ell.user("Build and Tests Executed Successfully")
            ]
        return [
            ell.user(user_prompt)
        ]

    @ell.complex(model="openai/gpt-4o-mini-2024-07-18", temperature=0.0, client=client, tools=[rewrite_unit_test_file])
    def parse_function_calls(self, reasoningoutput: str, unit_test_path: str):
        """
        Your only responsibility is to parse the reasoning output of the LLM and return the function calls that are needed.
        If there are no function calls, return an empty list.
        """
        return f"""A
        {reasoningoutput}
        # Unit Test Path:
        {unit_test_path}
        """

    def parse_function_calls_until_success(self, reasoningoutput: str, unit_test_path: str, max_retries=5):
        for attempt in range(max_retries):
            try:
                parsed = self.parse_function_calls(reasoningoutput, unit_test_path)
                return parsed
            except ValidationError as e:
                print(f"Attempt {attempt + 1} failed due to validation error: {str(e)}")
                if attempt >= max_retries - 1:
                    raise


    @ell.simple(model="qwen/qwen-2.5-coder-32b-instruct", max_tokens=8000, client=client, temperature=0.0)
    def refine_code_based_on_suggestion(self, sut: str, function: str, additional_information: str, knowledge_base_content: str, test_file_path: str, unit_testing_engine: str, file_contents: list[str], suggestion_from_developer: str, test_cases_code: str, build_errors: str):
        # Format all entries in file_contants in markdown code blocks
        formatted_file_contents = ""
        for file_path, file_content in file_contents.items():
            formatted_file_contents += f"# {file_path}\n```\n{file_content}\n```\n"

        repeated = "You solely are responsible for implementing the suggestion. Change NOTHING else. Don't remove any test cases unless explicitly told to. Don't remove any setup unless specifically told to, Make sure the unit test class will be in the \"Enveritus2.Test\" namespace." 

        user_prompt = """
You are a senior C# developer with expertise in unit approval testing. Your task is to implement a suggestion from a real human senior software developer.
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

<function_under_test>
{function}
</function_under_test>

{repeated}

<system_under_test>
{sut}
</system_under_test>

{repeated}

<test_file_path>
{test_file_path}
</test_file_path>

{repeated}

<additional_info>
{additional_information}
</additional_info>

{repeated}

<knowledge_base>
{knowledge_base_content}
</knowledge_base>

{repeated}

<failed_tests or build_errors>
{build_errors}
</failed_tests or build_errors>

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
Remember to rigorously follow the program logic and the knowledge base. Ensure that you provide the complete code.
{repeated}
    """.format(
        knowledge_base_content=knowledge_base_content,
        test_file_path=test_file_path,
        function=function,
        sut=sut,
        additional_information=additional_information,
        formatted_file_contents=formatted_file_contents,
        unit_testing_engine=unit_testing_engine,
        suggestion_from_developer=suggestion_from_developer,
        test_cases_code=test_cases_code,
        repeated=repeated,
        build_errors=build_errors
    )
        return [ell.user(user_prompt)]
