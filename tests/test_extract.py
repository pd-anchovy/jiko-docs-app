import extract


def test_build_prompt_contains_fields():
    p = extract.build_prompt()
    for field in ["書類種別", "車両番号", "発生日", "補償の種類", "運転者名", "支払完了"]:
        assert field in p
    assert "受付" in p
    assert "支払" in p
    assert "被保険者名" in p
    assert "和暦" in p


def test_parse_response_valid_json():
    text = ('{"書類種別": "受付", "車両番号": "練馬481り6562", "発生日": "2026-05-18", '
            '"補償の種類": "対人賠償 対物賠償", "運転者名": "関佑斗"}')
    result = extract.parse_response(text)
    assert result == {
        "書類種別": "受付", "車両番号": "練馬481り6562", "発生日": "2026-05-18",
        "補償の種類": "対人賠償 対物賠償", "運転者名": "関佑斗", "支払完了": "",
    }


def test_parse_response_payment_doc():
    text = ('{"書類種別": "支払", "車両番号": "横浜482レ2728", "発生日": "2026-05-04", '
            '"運転者名": "カ)ユアルート", "支払完了": "はい"}')
    result = extract.parse_response(text)
    assert result["書類種別"] == "支払"
    assert result["運転者名"] == "カ)ユアルート"
    assert result["支払完了"] == "はい"
    assert result["補償の種類"] == ""


def test_parse_response_missing_keys_filled_blank():
    result = extract.parse_response('{"車両番号": "A1"}')
    assert result["車両番号"] == "A1"
    assert result["書類種別"] == ""
    assert result["支払完了"] == ""


def test_parse_response_invalid_json_all_blank():
    result = extract.parse_response("これはJSONではない")
    assert all(v == "" for v in result.values())


def test_parse_response_strips_code_fence():
    text = '```json\n{"書類種別": "支払", "車両番号": "A1", "支払完了": "はい"}\n```'
    result = extract.parse_response(text)
    assert result["書類種別"] == "支払"
    assert result["支払完了"] == "はい"
