import os
from openai import Client
from anthropic import Anthropic

ell_key = os.getenv("MODALBOX_KEY")
openai_client = Client(
  api_key=ell_key,
  base_url="https://api.model.box/v1",
)

topology_client = Client(
  api_key="bcb2d9f897e68944aa4db0c94154dde281d45de9ee29150228c47492894b57cf9edf2110e15931f9efcd84894ec9576287a697ba4406ed4d3b54983fee0226fd",
  base_url="https://topologychat.com/api",
)

anthropic_client = Anthropic(
  api_key=ell_key,
  base_url="https://api.model.box/v1",
)
