import subprocess

def execute_build_and_tests(test_project_directory: str, test_namespace_and_classname:str):
    try:
        # Navigate to the test project directory and execute build
        build_process = subprocess.run(
            ["dotnet", "build", "-consoleloggerparameters:ErrorsOnly"],
            cwd=test_project_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        build_output = build_process.stdout

        # Execute the tests only if build was successful
        command = f"dotnet test --filter \"FullyQualifiedName={test_namespace_and_classname}\" --no-restore --no-build"
        test_process = subprocess.run(
            command,
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
            ```n
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