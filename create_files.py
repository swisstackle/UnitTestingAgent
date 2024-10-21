def create_test_file(test_cases: str, test_project_file: str):
    """
    This method createsa test file and inserts the code in test_cases into it.
    If the file already exists, it will be overwritten.
    We will use try catch to handle the file creation.
    The code in test_cases is between ```csharo tags (markdown formatting).
    This function first extracts the code between the ```csharp tags and then writes it to the test project file.
    """
    try:
        # Extract the code between the ```csharp tags
        with open(test_project_file, 'w') as file:
            file.write(test_cases)
    except Exception as e:
        print(f"Failed to create test file '{test_project_file}': {str(e)}")

def create_DTO_file(content, base_path):
    dto_file_path = f"{base_path}_DTO.cs"
    with open(dto_file_path, 'w') as file:
        file.write(content)
    return f"{base_path}_DTO.cs"

def create_factory_file(content, base_path):
    factory_file_path = f"{base_path}_Factory.cs"
    with open(factory_file_path, 'w') as file:
        file.write(content)
    return f"{base_path}_Factory.cs"