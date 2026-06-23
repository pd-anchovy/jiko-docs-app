import json

import schema


def build_prompt(doc_type):
    fields = schema.DOC_TYPES[doc_type]
    if doc_type == "payment":
        extra = (
            "「支払完了」は、この書類が支払い完了済みの書類なら \"はい\"、"
            "そうでなければ \"いいえ\" を入れてください。"
        )
    else:
        extra = ""
    keys = "、".join(fields)
    return (
        "この事故関連書類の画像から、次の項目を読み取ってJSONで返してください。\n"
        f"項目キー: {keys}\n"
        "値が読み取れない項目は空文字 \"\" にしてください。\n"
        "発生日は YYYY-MM-DD 形式に正規化してください。\n"
        f"{extra}\n"
        "JSONオブジェクトだけを返し、余計な説明は付けないでください。"
    )


def parse_response(text, doc_type):
    fields = schema.DOC_TYPES[doc_type]
    blank = {f: "" for f in fields}

    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except (ValueError, TypeError):
        return blank

    if not isinstance(data, dict):
        return blank

    return {f: str(data.get(f, "") or "") for f in fields}


def extract_fields(image_bytes, mime_type, doc_type, api_key,
                   model_name="gemini-2.0-flash"):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=[
            build_prompt(doc_type),
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ],
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return parse_response(response.text, doc_type)
