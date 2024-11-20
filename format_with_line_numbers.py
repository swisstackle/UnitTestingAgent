def format_code_with_line_numbers(file_content: str, file_path: str = None) -> str:
    # Split content into lines
    lines = file_content.splitlines()
    
    # Format with line numbers
    numbered_content = "\n".join(f"{i+1:4d} │ {line}" for i, line in enumerate(lines))
    
    # Create markdown block with file path (if provided) and numbered content
    header = f"# {file_path}\n" if file_path else ""
    return f"{header}```csharp\n{numbered_content}\n```"



if __name__ == "__main__":
    # Read the content of the specified file
    file_path = "C:\\Users\\aschaerer\\Documents\\BPAS-Enveritus2\\Enveritus2\\Services\\SessionService.cs"
    with open(file_path, 'r', encoding='utf-8') as file:
        code_content = file.read()
    

    formatted = format_code_with_line_numbers(code_content, "TestClass.cs")
    print(formatted)