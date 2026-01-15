import base64
import json
from app.config import settings
from groq import Groq

api_key = settings.groq_key
model = settings.model

if not api_key:
    print("Api Key not found")
    exit()

client = Groq(api_key=api_key)


def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")
