import pymsteams
import os


if __name__ == "__main__":
    card = pymsteams.connectorcard("")
    # Create an adaptive card payload
    card.payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "This message was sent with python"
                        }
                    ]
                }
            }
        ]
    }
    assert card.send()

