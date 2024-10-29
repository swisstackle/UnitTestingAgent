import ell

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

