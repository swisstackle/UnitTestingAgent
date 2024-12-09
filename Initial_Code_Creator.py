import ell
from LlmClientFactory import LlmClientFactory, ClientType

client = LlmClientFactory.get_client(ClientType.OPENROUTER)

class Initial_Code_Creator:
    @ell.simple(model="qwen/qwen-2.5-coder-32b-instruct", max_tokens=8000, client=client, temperature=0.0)
    def build_unit_tests(
        self,
        function: str,
        sut: str,
        test_cases: str,
        test_project_file: str,
        additional_information: str,
        knowledge_base_content: str,
        unit_testing_engine: str,
        file_contents: dict = None,
    ):
        formatted_file_contents = ""
        for file_path, file_content in file_contents.items():
            formatted_file_contents += f"# {file_path}\n```\n{file_content}\n```\n"
        user_prompt = f"""
        You are an expert C# and .NET developer, specializing in creating unit approval tests for .NET applications. Your task is to create unit tests for a specific function based on the provided information and knowledge base. It is crucial that you strictly adhere to the provided knowledge base at all times.
        Very IMPORTANT: In the code that you generate, for every line that you make, you have to write a comment where in the knowledgebase you found similar code that you used. If you have to write code that you didnt find in the knowledge base, just write "couldnt find" as a comment.
        Make sure that the classes in the unit test file reside within the namespace of the test project, not where the SUT is.
        Make sure the unit test class will be in the "Enveritus2.Test" namespace.

        Here is the file containing the function under test:
        <function_file>
        {{sut}}
        </function_file>

        Here is the unit testing system you should use:
        <unit_testing_system>
        {{unit_testing_engine}}
        </unit_testing_system>

        The name of the function under test is:
        <function_name>
        {{function}}
        </function_name>

        Here are the provided unit test cases:
        <unit_test_cases>
        {{test_cases}}
        </unit_test_cases>

        Additional important information:
        <additional_info>
        {{additional_information}}
        </additional_info>

        Potentially Relevant Files:
        <relevantfiles>
        {{relevant_files}}
        </relevantfiles>

        The knowledge base you must adhere to is:
        <knowledge_base>
        {{knowledge_base_content}}
        </knowledge_base>

        Before creating the unit tests, please analyze the function and plan your approach. Wrap your analysis inside <analysis> tags to show your thought process. In your analysis, make sure to:
        1. Break down the function under test and list all its dependencies.
        2. Identify the input parameters and return type of the function.
        3. Consider potential edge cases and error scenarios, listing at least three of each.
        4. Plan the structure of your unit tests, including:
            a. A list of test methods you'll create
            b. Any setup or teardown steps needed
            c. Any mocking or stubbing required for dependencies
        5. Explicitly reference and adhere to the provided knowledge base, ensuring that all tests are in line with the information given there.
        6. Create a step-by-step plan for implementing the unit tests.

        After your analysis, create the unit tests using the specified unit testing system. Your output should include:
        1. The complete unit testing code, including any necessary DTOs and Factory classes.
        2. All code should be in the same namespace.
        3. The entire code output should be wrapped in a single set of ```csharp tags.

        Remember:
        - Strictly adhere to the knowledge base at all times.
        - Show your thought process in the <analysis> tags.
        - Ensure all code is well-organized and properly structured.
        - Include any necessary DTOs and Factory classes in your output.
        - Make sure the unit test class will be in the "Enveritus2.Test" namespace.

        Please begin your analysis now.
        ```
    """.format(knowledge_base_content=knowledge_base_content, unit_testing_engine=unit_testing_engine, function=function, sut=sut, test_cases=test_cases, additional_information=additional_information, relevant_files=formatted_file_contents)
        with open("user_prompt.txt", "w") as f:
            f.write(user_prompt)
        return [
            ell.user(user_prompt)
        ]