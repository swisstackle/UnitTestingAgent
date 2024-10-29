import ell

@ell.simple(model="openai/o1-mini", seed=42, temperature=0.0)
def build_unit_tests(
    function: str,
    sut: str,
    test_cases: str,
    test_project_file: str,
    additional_information: str,
    knowledge_base_content: str,
    unit_testing_engine: str,
    file_contents: dict = None,
):
    """
    This method sends the system prompt and the user prompt to the LLM.
    The system prompt is used to guide the LLM in building the unit test cases.
    The user prompt is used to provide the LLM with the necessary information to build the unit test cases.
    The goal is to create code without errors and exceptions.
    To avoid namespace conflicts, you HAVE TO use namespaces directly instead of using the using statement.
    For example if you wanted to call the method "classname.foo" that resides in the namespace "thenamespace", you have to call it like this: "thenamespace.classname.foo".
    """
    # I want to format all entries in file_contants in markdown code blocks
    # It should be a formatted string in markdown
    formatted_file_contents = ""
    for file_path, file_content in file_contents.items():
        formatted_file_contents += f"# {file_path}\n```\n{file_content}\n```\n"
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
        {{formatted_file_contents}}
        ```
    """.format(knowledge_base_content=knowledge_base_content, unit_testing_engine=unit_testing_engine, function=function, sut=sut, test_cases=test_cases, test_project_file=test_project_file, additional_information=additional_information, formatted_file_contents=formatted_file_contents)

    return [
        ell.user(user_prompt)
    ]