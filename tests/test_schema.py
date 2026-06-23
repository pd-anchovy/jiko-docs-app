import schema


def test_columns_order():
    assert schema.COLUMNS == [
        "車両番号", "発生日", "補償の種類", "運転者名",
        "受付登録日時", "支払完了", "支払登録日時",
    ]


def test_doc_types_fields():
    assert schema.DOC_TYPES["reception"] == ["車両番号", "発生日", "補償の種類", "運転者名"]
    assert schema.DOC_TYPES["payment"] == ["車両番号", "発生日", "支払完了"]
