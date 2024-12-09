# Main components

## main.py

Main entry point of the program. Takes in various arguments.

## GitHubManager.py

This is a file with methods to make git commits, push code to the repository and create PR's.

## install_libs.py

This file contains methods to install nuget packages.

## TestCaseGenerator.py

This agent creates the test cases themselves but not the code yet.

## Initial_Code_Creator.py

The resulting string from the test case generator is fed into the initial code creator. The initial code creator creates the initial code for the unit test file.

## CodeRefiner.py

Contains 2 agents:

1. CodeRefiner based on code errors: Refines unit testing code to eliminate building errors and exceptions.
2. CodeRefiner based on suggestion: Refines unit testing code based on suggestion from human developer.

Also includes agents to parse the outputs of the refiner ant convert it into function calls.

## update_project_file.py

Contains the method to update the project file based on dependencies.

## VextorStore.py

Contains methods to create memories and search them.

## BuildExecutor.py

Contains methods to execute the build and tests.