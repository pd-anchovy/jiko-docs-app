import extract


def test_build_prompt_contains_fields():
    p = extract.build_prompt("reception")
    for field in ["車両番号", "発生日", "補償の種類", "運転者名"]:
        assert field in p


def test_parse_response_valid_json():
    text = '{"車両番号": "品川500あ1234", "発生日": "2026-06-01", "補償の種類": "対物", "運転者名": "山田太郎"}'
    result = extract.parse_response(text, "reception")
    assert result == {
        "車両番号": "品川500あ1234", "発生日": "2026-06-01",
        "補償の種類": "対物", "運転者名": "山田太郎",
    }


def test_parse_response_missing_keys_filled_blank():
    text = '{"車両番号": "A1"}'
    result = extract.parse_response(text, "payment")
    assert result == {"車両番号": "A1", "発生日": "", "支払完了": ""}


def test_parse_response_invalid_json_all_blank():
    result = extract.parse_response("これはJSONではない", "reception")
    assert result == {"車両番号": "", "発生日": "", "補償の種類": "", "運転者名": ""}


def test_parse_response_strips_code_fence():
    text = '```json\n{"車両番号": "A1", "発生日": "2026-06-01", "支払完了": "はい"}\n```'
    result = extract.parse_response(text, "payment")
    assert result["車両番号"] == "A1"
    assert result["支払完了"] == "はい"
