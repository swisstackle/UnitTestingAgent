from enum import Enum
from openai import Client

class ClientType(Enum):
    OPENROUTER = 0,
    HUGGINGFACE = 1

class LlmClientFactory:
    @staticmethod
    def get_client (client_type: ClientType):
        if client_type == ClientType.OPENROUTER:
            return Client( api_key="",
                base_url="https://openrouter.ai/api/v1")

        elif client_type == ClientType.HUGGINGFACE:
            return Client(
	            base_url="https://l96ve6nvokl6h2mo.us-east-1.aws.endpoints.huggingface.cloud/v1", 
	            api_key="hf_XXXXX" 
            )

        else:
            raise ValueError(f"Client type {client_type} not supported")


