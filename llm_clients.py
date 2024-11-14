import os
from openai import Client
from anthropic import Anthropic

MODALBOX_API_KEY = os.getenv("MODALBOX_KEY")
if not MODALBOX_API_KEY:
    raise ValueError("MODALBOX_KEY environment variable is not set")

# Custom API endpoint for model.box service
openai_client = Client(
    api_key=MODALBOX_API_KEY,
    base_url="https://api.model.box/v1",
)

topology_client = Client(
  api_key="",
  base_url="https://topologychat.com/api",
)

anthropic_client = Anthropic(
  api_key="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"
)
