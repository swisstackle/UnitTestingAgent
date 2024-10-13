# import all libraries that are necessary to install a nuget package
import os
import sys
import subprocess

def install_nuget_package(package_name, test_project_file_path):
    subprocess.run(["nuget", "locals", "all", "-clear"])
    try:
        subprocess.run(["dotnet", "add", "package", package_name], cwd=os.path.dirname(test_project_file_path), check=True)
        return f"Successfully installed nuget package {package_name}"
    except Exception as e:
        return f"Error in install_nuget_package: {str(e)}"

