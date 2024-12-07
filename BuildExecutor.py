import subprocess
from pathlib import Path
import shutil
import os

class BuildExecutor:

    @staticmethod
    def execute_build_and_tests(test_project_directory: str, test_namespace_and_classname: str):
        test_project_directory = str(Path(test_project_directory).resolve())
        bin_directory = os.path.join(test_project_directory, "bin")
        obj_directory = os.path.join(test_project_directory, "obj")

        if os.path.exists(bin_directory):
            shutil.rmtree(bin_directory)

        if os.path.exists(obj_directory):
            shutil.rmtree(obj_directory)
        try:
            # Navigate to the test project directory and execute build
            clean_process = subprocess.run(
                ["dotnet", "clean"],
                cwd=test_project_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

            build_process = subprocess.run(
                ["dotnet", "build", "Enveritus2.Test.csproj", "-consoleloggerparameters:ErrorsOnly", "--no-incremental"],
                cwd=test_project_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
        
            # Only include build output if there were errors
            build_output = ""
            if build_process.stderr:
                build_output = f"Build Errors:\n{build_process.stderr}\n"

            # Get list of all tests
            list_tests_process = subprocess.run(
                ["dotnet", "test", "--list-tests"],
                cwd=test_project_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
        
            # Filter tests that belong to our target class
            test_methods = []
            for line in list_tests_process.stdout.splitlines():
                if test_namespace_and_classname in line:
                    test_methods.append(line.strip())

            if not test_methods:
                return f"No tests found in {test_namespace_and_classname}"

            # Execute each test method and accumulate results
            all_test_output = []
            passed_tests = 0
            failed_tests = []
        
            for test_method in test_methods:
                command = [
                    "dotnet", "test",
                    "--filter", f"FullyQualifiedName={test_method}",
                    "--no-build",
                    "--verbosity", "normal",
                    "--logger", "console;verbosity=normal"
                ]
            
                test_process = subprocess.run(
                    command,
                    cwd=test_project_directory,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False  # Don't raise exception on test failure
                )
            
                # Process the output to extract relevant information
                output = test_process.stdout
                if "Failed" in output:
                    failed_tests.append(test_method)
                    # Extract and format failure information
                    for line in output.splitlines():
                        all_test_output.append(line)
                else:
                    passed_tests += 1

            # Format the final output
            result = []
            if build_output:
                result.append(build_output)
        
            result.append(f"Total Tests: {len(test_methods)}")
            result.append(f"Passed: {passed_tests}")
            result.append(f"Failed: {len(failed_tests)}")
        
            if failed_tests:
                result.append("\nFailed Tests:")
                for failed_test in failed_tests:
                    result.append(f"  • {failed_test.split('.')[-1]}")
                result.append("\nFailure Details:")
                result.extend(all_test_output)
            
                return "\n".join(result)
            else:
                return f"""
                    All tests passed successfully!
                    Total Tests: {len(test_methods)}
                    Passed: {passed_tests}
                    Failed: 0
                """

        except subprocess.CalledProcessError as e:
            error_message = e.stderr if e.stderr else e.stdout
            return f"Error during execution:\n{error_message}"
