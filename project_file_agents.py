import ell
from tools import rewrite_test_project_file
#from llm_clients import openai_client_for_openrouter, openai_client, anthropic_client
import os
from openai import Client
openai_client_for_openrouter = Client(
    api_key="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",
    base_url="https://openrouter.ai/api/v1",
)
# Custom API endpoint for model.box service
openai_client = Client(
    api_key="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",
)

@ell.complex(client=openai_client, model="gpt-4o", temperature=0.0, tools=[rewrite_test_project_file])
def add_project_references(test_project_file_path: str, project_paths_to_add_to_references: list[str]):
    """
    Your only responsibility is to add project references to the csproj test project file that are given to you.
    You are not allowed to add any other project references or remove any project references.
    Use the rewrite_project_file tool to rewrite the test project file.
    Don't insert any weird BOM characters.
    """
    if not os.path.exists(test_project_file_path):
        raise FileNotFoundError(f"Test project file not found: {test_project_file_path}")

    try:
        with open(test_project_file_path, 'r') as file:
            test_project_file_content = file.read()
    except IOError as e:
        raise IOError(f"Failed to read test project file: {e}")
    return f"""
        Rewrite the test project file to add the following project references: {project_paths_to_add_to_references}

        # test_project_file_path:
        ```
        {test_project_file_path}
        ```

        # Test project file content:
        ```
        {test_project_file_content}
        ```

    """


if __name__ == "__main__":
    print(add_project_references(test_project_file_path="/home/alains/Work/BPAS-Enveritus2/Enveritus2.Test/Enveritus2.Test.csproj", project_paths_to_add_to_references=["..\test.csproj"]).text)
    # tools = [
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "rewrite_test_project_file",
    #         "parameters": {
    #             "type": "object",
    #             "required": [
    #                 "test_project_file_path",
    #                 "test_project_file_content"
    #             ],
    #             "properties": {
    #                 "test_project_file_path": {
    #                     "type": "string",
    #                     "description": "The path to the test project file (csproj). The variable is called test_project_file_path. Do not include anything else but the path. Make sure the file path is in the right format: for example: C:\\Users\\user\\Documents\\test.csproj Note how the backslashes are escaped only once."
    #                 },
    #                 "test_project_file_content": {
    #                     "type": "string",
    #                     "description": "The content of the test project file (csproj). The variable is called test_project_file. Do not include anything else but the content."
    #                 }
    #             },
    #             "additionalProperties": False
    #         }
    #     }
    # }
    # ]


    # systemprompt = """
    # Your only responsibility is to add project references to the csproj test project file that are given to you.
    # You are not allowed to add any other project references or remove any project references.
    # Use the rewrite_project_file tool to rewrite the test project file.
    # Don't insert any weird BOM characters.
    # """

    # test_project_file_path = "/home/alains/Work/BPAS-Enveritus2/Enveritus2.Test/Enveritus2.Test.csproj"
    # project_paths_to_add_to_references = "../test.csproj"

    # with open(test_project_file_path, 'r') as file:
    #     test_project_file_content = file.read()


    # prompt = """
    #     Rewrite the test project file to add the following project references: {project_paths_to_add_to_references}

    #     # test_project_file_path:
    #     ```
    #     {test_project_file_path}
    #     ```

    #     # Test project file content:
    #     ```
    #     {test_project_file_content}
    #     ```
    # """.format(test_project_file_path=test_project_file_path, test_project_file_content=test_project_file_content, project_paths_to_add_to_references=project_paths_to_add_to_references)
    # print(prompt)
    # completion = openai_client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{"role":"system", "content": systemprompt},
    #         {"role": "user", "content": prompt}],
    #     tools=tools,
    # )

    # print(completion.choices[0].message)
