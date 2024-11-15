import ell
from llm_clients import openai_client
from refined_unit_tests import refined_unit_tests
from pydantic import BaseModel, Field
from typing import List

class NeedsHuman(BaseModel):
    needs_human: bool = Field(description="Denotes whether the past_actions indicate the a human senior software developer needs to be evolved. Usually that is the case when there ae a lot of repeated actions (infinite loop) and the agents are stuck resolving it.")

@ell.complex(model="openai/gpt-4o", temperature=0.0, client=openai_client, response_format=NeedsHuman, seed=42)
def check_actions(past_actions: list[str]) -> NeedsHuman:
    """
   You are an agent part of a software development multi agent system that creates unit tests.
   Your sole responsibility is to determine whether human envolvement is necessary.
   The way you determine that is by looking at the actions that the software development agent took.
   If the list of actions indicate that the software development agent is in an infinite loop and can't resolve the error on its own, you would make "needs_human" true, otherwise false. 

   Example of infinite loop:
   ['Added using reference for the error Severity Error CS0246	The type or namespace name 'IPendingTransactionService' could not be found',
   'Removed IPendingTransactionService as a whole because it is not needed for the tests',
   'Added using reference for IPendingTransactionsService to resolve for Error: CS7036	There is no argument given that corresponds to the required parameter 'optionsService' of 'RebalanceService.RebalanceService',
   'Removed IPendingTransactionService as a whole because it is not needed for the tests',
   'Added a new using reference for IPendingTransactionsService to resolve for Error: CS7036	There is no argument given that corresponds to the required parameter 'optionsService' of 'RebalanceService.RebalanceService']

   Example of good loop that means that the system is not stuck:
   ['Added using reference for the error Severity Error CS0246	The type or namespace name 'IPendingTransactionService' could not be found',
   'Removed IPendingTransactionService as a whole because it is not needed for the tests. Added "null" to the Constructor call to make sure that no arguments are missing.']
    """
    return f"""
<past_actions that are seperated by <, > and commas> 
    {past_actions}
</past_actions that are seperated by <, > and commas> 
    """