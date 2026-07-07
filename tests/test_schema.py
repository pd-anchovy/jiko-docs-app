import schema


def test_columns_order():
    assert schema.COLUMNS == [
        "車両番号", "発生日", "補償の種類", "運転者名",
        "支払完了", "通知種類",
    ]


def test_extract_fields():
    assert schema.EXTRACT_FIELDS == [
        "書類種別", "車両番号", "発生日", "補償の種類", "運転者名", "支払完了",
    ]


def test_doc_labels():
    assert schema.DOC_LABELS == {"受付": "reception", "支払": "payment"}


def test_notice_labels():
    assert schema.NOTICE_LABELS == {
        "reception": "受付連絡",
        "payment": "支払完了通知",
    }
