import base64
import json
from app.config import settings
from app import schemas
from groq import AsyncGroq

api_key = settings.groq_key
model = settings.model

if not api_key:
    print("Api Key not found")

client = AsyncGroq(api_key=api_key)


def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


async def extract_receipt_data(image_bytes: bytes) -> schemas.ReceiptCreate:
    base64_image = encode_image(image_bytes)
    task = """
    You are a receipt parser API. Analyze the image and extract data.
    OUTPUT FORMAT (Strict JSON):
{
  "store_name": "string or null",
  "purchase_date": "YYYY-MM-DD or null",
  "currency_symbol": "string (extract the symbol used, e.g. $, ₹, €, £. Default to $ if unsure)"
  "total_amount": float or null,
  "tax_amount": float or null,
  "scan_confidence": "float (0.0 to 1.0) - Lower this value if text is blurry or hard to read", 
  "items": [
    {
      "item_name": "string",
      "price": float or null,
      "category": "string (should be generic like:Food, Electronics, Utility, etc)"
    }
  ]
}
RULES:
- Return ONLY raw JSON. No markdown.
- If a value is missing/unreadable, use null.
"""

    # task = """You are a receipt parser API.
    #                 Analyze the image and extract data in JSON format, if a value is not present, use null'
    #                 The keys should be:
    #                 - store_name:name of the store or merchant
    #                 - purchase_date:convert Purchase Date  in ISO format 'YYYY-MM-DD'
    #                 - total_amount(float): the final amount paid
    #                 - tax_amount(float): tax amount paid
    #                 - scan_confidence(float): range in between "0.0 to 0.1".This field identifies how sure you are about
    #                 your values inserted in keys after scanning the receipt
    #                 -items(list): A list of objects with 'item_name', 'price' and 'category' keys.
    #                 RULES:
    #                 - Return ONLY JSON. No markdown formatting(```json),no conversational text.
    #                 - Category Should be generic (eg., "Food","Electronics","Utility",etc)
    #                 """
    response = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": task},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
    )
    raw_response = response.choices[0].message.content

    if raw_response is not None:
        clean_json_string = (
            raw_response.replace("```json", "").replace("```", "").strip()
        )

        try:
            data_dict = json.loads(clean_json_string)

            validated_data = schemas.ReceiptCreate(**data_dict)

            return validated_data

        except json.JSONDecodeError:
            print(f"Failed JSON: {raw_response}")
            raise ValueError("AI returned invalid JSON, Try scanning again")
        except Exception as e:
            print(f"Error {e}")
            raise ValueError(f"Data Extraction Failed {str(e)}")

    else:
        raise ValueError("AI returned an empty response")
