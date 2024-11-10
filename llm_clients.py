import os
from openai import Client
from anthropic import Anthropic

ell_key = os.getenv("MODALBOX_KEY")
openai_client = Client(
  api_key=ell_key,
  base_url="https://api.model.box/v1",
)

topology_client = Client(
  api_key="",
  base_url="https://topologychat.com/api",
)

anthropic_client = Anthropic(
  api_key=ell_key,
  base_url="https://api.model.box/v1",
)
