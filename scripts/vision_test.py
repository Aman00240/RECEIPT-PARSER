import base64
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_KEY")
model = os.getenv("MODEL")

if not api_key:
    print("Error: key not found")
    exit()

client = Groq(api_key=api_key)


def encode_image(image_path):
    with open(image_path, "rb") as image:
        return base64.b64encode(image.read()).decode("utf-8")


image_path = r"F:\Ai Enginner Projects\Receipt Parser\scripts\download.jpg"
if not os.path.exists(image_path):
    print("Image Not Found")
    exit()

base64_image = encode_image(image_path)
print(f"Scanning {image_path}..")


try:
    completion = client.chat.completions.create(
        model=model,  # type: ignore
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Extract the following details from this recipt image
                        as Strictly valid JSON: store_name,date,total_amount,tax_amount,
                        items(list of {name,price}).""",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw_json = completion.choices[0].message.content
    parsed_data = json.loads(raw_json)  # type: ignore
    print(f"PArsed data:{parsed_data}")

    print("SUCCESS! Extracted Data:")
    print(json.dumps(parsed_data, indent=2))

except Exception as e:
    print(f"\n Failed: {e}")
