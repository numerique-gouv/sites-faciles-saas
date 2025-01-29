import base64


def encode_secrets(secrets):
    return base64.b64encode(secrets.encode()).decode()


def decode_secrets(encoded_secrets: str):
    return base64.b64decode(encoded_secrets).decode()
