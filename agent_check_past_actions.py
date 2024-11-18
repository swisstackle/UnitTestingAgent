import ell
from llm_clients import openai_client
from refined_unit_tests import refined_unit_tests
from pydantic import BaseModel, Field
from typing import List

class NeedsHuman(BaseModel):
    needs_human: bool = Field(description="Denotes whether the past_actions indicate the a human senior software developer needs to be evolved. Usually that is the case when there ae a lot of repeated actions (infinite loop) and the agents are stuck resolving it.")

@ell.complex(model="openai/gpt-4o", temperature=0.0, client=openai_client, response_format=NeedsHuman, seed=42)
def check_actions(diffs: list[str]) -> NeedsHuman:
    """
   You are an agent part of a software development multi agent system that creates unit tests.
   Your sole responsibility is to determine whether human envolvement is necessary.
   The way you determine that is by looking at the 10 git diffs that the software development agent made.
   If the list of diffs indicate that the software development agent is in an infinite loop and can't resolve the error on its own, you would make "needs_human" true, otherwise false.
   The diffs don't have to be exactly the same to consider the agent to be in a loop. If they are conceptually the same, you should request human involvement, otherwise you should not.
   
   Each diff is numbered and starts with a markdown title. For example:

   # Diff 10:
    ```
    diff --git a/build_unit_tests.py b/build_unit_tests.py
    index bc7efd2..b340952 100644
    --- a/build_unit_tests.py
    +++ b/build_unit_tests.py
    @@ -1,7 +1,7 @@
    import ell
    -from llm_clients import topology_client
    +from llm_clients import openai_client
    """
    return f"""
    {diffs}
    """