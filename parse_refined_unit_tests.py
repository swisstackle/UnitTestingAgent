import ell
from llm_clients import openai_client, openai_client_for_openrouter
from refined_unit_tests import refined_unit_tests

@ell.complex(model="openai/gpt-4o-mini-2024-07-18", temperature=0.0, client=openai_client_for_openrouter, response_format=refined_unit_tests, seed=42)
def parse_refined_unit_tests(output: str):
    """
    You are responsivle for parsing the output of the refine_code_based_on_errors agent into RefinedUnitTests format.
    Don't insert any weird BOM characters.
    """
    return f"""
    {output}
    """