# import all libraries that are necessary to install a nuget package
import os
import sys
import subprocess

def install_nuget_package(package_name, test_project_file_path):
    #subprocess.run(["nuget", "locals", "all", "-clear"])
    test_project_file_directory = os.path.dirname(test_project_file_path)
    try:
        # check if the nuget package is already installed
        result = subprocess.run(f"dotnet list package | findstr {package_name}", cwd=test_project_file_directory, check=True, capture_output=True, text=True, shell=True)
        # if the package is not installed, install it
        if package_name not in result.stdout:
            subprocess.run(["dotnet", "add", "package", package_name], cwd=test_project_file_directory, check=True)
        return f"Successfully installed nuget package {package_name}"
    except Exception as e:
        return f"Error in install_nuget_package: {str(e)}"

