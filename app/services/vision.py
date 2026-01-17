import base64
import io
import json
from PIL import Image
from app.config import settings
from app import schemas
from groq import AsyncGroq

api_key = settings.groq_key
model = settings.model

if not api_key:
    print("Api Key not found")

client = AsyncGroq(api_key=api_key)


def resize_image(image_byte: bytes, max_width: int = 1024) -> bytes:
    try:
        with Image.open(io.BytesIO(image_byte)) as img:
            if img.width > max_width:
                ratio = max_width / float(img.width)
                new_height = int(float(img.height) * ratio)

                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            output = io.BytesIO()

            if img.mode in ("RGBA", "p"):
                img = img.convert("RGB")

            img.save(output, format="JPEG", quality=85)
            return output.getvalue()

    except Exception as e:
        print(f"Error in resizeing the image {e}")
        return image_byte


def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


async def extract_receipt_data(image_bytes: bytes) -> schemas.ReceiptCreate:
    base64_image = encode_image(image_bytes)

    task = """You are a receipt parser API.
                    Analyze the image and extract data in JSON format, if a value is not present enter exactly 'None'
                    The keys should be:
                    - store_name:name of the store or merchant
                    - purchase_date:convert Purchase Date  in ISO format 'YYYY-MM-DD'
                    - total_amount(float): the final amount paid 
                    - tax_amount(float): tax amount paid
                    - scan_confidence(float): range in between "0.0 to 0.1".This field identifies how sure you are about 
                    your values inserted in keys after scanning the receipt
                    -items(list): A list of objects with 'item_name', 'price' and 'category' keys.
                    RULES:
                    - Return ONLY JSON. No markdown formatting(```json),no conversational text.
                    - Category Should be generic (eg., "Food","Electronics","Utility",etc)
                    """
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
