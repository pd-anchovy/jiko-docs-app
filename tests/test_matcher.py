import schema
import matcher

NOW = "2026-06-22 10:00:00"


def _blank_row(**kw):
    row = {c: "" for c in schema.COLUMNS}
    row.update(kw)
    return row


def test_find_row_index_match():
    rows = [_blank_row(車両番号="A1", 発生日="2026-06-01")]
    assert matcher.find_row_index(rows, "A1", "2026-06-01") == 0


def test_find_row_index_none():
    rows = [_blank_row(車両番号="A1", 発生日="2026-06-01")]
    assert matcher.find_row_index(rows, "A1", "2026-06-02") is None


def test_reception_appends_new_row():
    rows = []
    rec = {"車両番号": "A1", "発生日": "2026-06-01", "補償の種類": "対物", "運転者名": "山田太郎"}
    new_rows, action = matcher.apply_record(rows, "reception", rec, NOW)
    assert action == "appended"
    assert len(new_rows) == 1
    assert new_rows[0]["補償の種類"] == "対物"
    assert new_rows[0]["運転者名"] == "山田太郎"
    assert new_rows[0]["受付登録日時"] == NOW
    assert new_rows[0]["支払完了"] == ""
    # 元のrowsは不変
    assert rows == []


def test_payment_matches_existing_reception_row():
    rows = [_blank_row(車両番号="A1", 発生日="2026-06-01",
                       補償の種類="対物", 運転者名="山田太郎", 受付登録日時=NOW)]
    pay = {"車両番号": "A1", "発生日": "2026-06-01", "支払完了": "はい"}
    new_rows, action = matcher.apply_record(rows, "payment", pay, "2026-06-22 11:00:00")
    assert action == "updated"
    assert len(new_rows) == 1
    assert new_rows[0]["支払完了"] == "はい"
    assert new_rows[0]["支払登録日時"] == "2026-06-22 11:00:00"
    assert new_rows[0]["運転者名"] == "山田太郎"  # 受付情報は保持


def test_payment_without_match_appends_row():
    rows = []
    pay = {"車両番号": "B2", "発生日": "2026-06-05", "支払完了": "いいえ"}
    new_rows, action = matcher.apply_record(rows, "payment", pay, NOW)
    assert action == "appended"
    assert new_rows[0]["車両番号"] == "B2"
    assert new_rows[0]["支払完了"] == "いいえ"
    assert new_rows[0]["支払登録日時"] == NOW
    assert new_rows[0]["補償の種類"] == ""  # 受付情報は空


def test_reception_updates_existing_row():
    rows = [_blank_row(車両番号="A1", 発生日="2026-06-01",
                       支払完了="はい", 支払登録日時=NOW)]
    rec = {"車両番号": "A1", "発生日": "2026-06-01", "補償の種類": "人身", "運転者名": "佐藤花子"}
    new_rows, action = matcher.apply_record(rows, "reception", rec, "2026-06-22 12:00:00")
    assert action == "updated"
    assert new_rows[0]["補償の種類"] == "人身"
    assert new_rows[0]["受付登録日時"] == "2026-06-22 12:00:00"
    assert new_rows[0]["支払完了"] == "はい"  # 支払情報は保持
