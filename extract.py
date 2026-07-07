import json

import schema


def build_prompt():
    keys = "、".join(schema.EXTRACT_FIELDS)
    return (
        "この事故関連書類の画像から、まず書類の種類を判定し、"
        "次の項目を読み取ってJSONで返してください。\n"
        f"項目キー: {keys}\n"
        "「書類種別」: 受付連絡の書類(例:「受付のご連絡」)なら \"受付\"、"
        "保険金支払いに関する書類(例:「保険金お支払い完了のご案内」のはがき)"
        "なら \"支払\" を入れてください。\n"
        "「車両番号」: 「車両登録番号」または「損害対象物」欄のナンバーを"
        "入れてください。カタカナのかな文字はひらがなに変換してください"
        "(例: 横浜482レ2728 → 横浜482れ2728)。\n"
        "「運転者名」: 受付書類では「運転者様」欄の氏名、"
        "支払書類では「被保険者名」欄の名義を入れてください。\n"
        "「補償の種類」: 受付書類のみ。支払書類では空文字 \"\"。\n"
        "「支払完了」: 支払書類で支払いが完了済みなら \"はい\"、"
        "未完了なら \"いいえ\"。受付書類では空文字 \"\"。\n"
        "値が読み取れない項目は空文字 \"\" にしてください。\n"
        "発生日は YYYY-MM-DD 形式に正規化し、"
        "和暦(令和◯年など)は西暦に変換してください。\n"
        "JSONオブジェクトだけを返し、余計な説明は付けないでください。"
    )


def parse_response(text):
    fields = schema.EXTRACT_FIELDS
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


def extract_fields(image_bytes, mime_type, api_key,
                   model_name="gemini-2.5-flash"):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=[
            build_prompt(),
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ],
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return parse_response(response.text)
