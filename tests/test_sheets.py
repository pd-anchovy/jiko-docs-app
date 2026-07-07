import schema
import sheets


class FakeWorksheet:
    """gspreadの必要メソッドだけ模倣する。1行目=ヘッダ。"""
    def __init__(self, header=None, data_rows=None):
        self.header = header or list(schema.COLUMNS)
        self.data_rows = data_rows or []  # 各行は値のリスト(ヘッダ順)
        self.appended = []
        self.updates = []

    def get_all_records(self):
        records = []
        for r in self.data_rows:
            records.append({self.header[i]: r[i] for i in range(len(self.header))})
        return records

    def append_row(self, values):
        self.appended.append(values)
        self.data_rows.append(values)

    def update(self, range_name, values):
        self.updates.append((range_name, values))


def test_load_rows_normalizes():
    ws = FakeWorksheet(data_rows=[["A1", "2026-06-01", "対物", "山田", "", ""]])
    rows = sheets.load_rows(ws)
    assert rows[0]["車両番号"] == "A1"
    assert rows[0]["支払完了"] == ""


def test_save_record_appends_new_reception():
    ws = FakeWorksheet()
    rec = {"車両番号": "A1", "発生日": "2026-06-01", "補償の種類": "対物", "運転者名": "山田"}
    action = sheets.save_record(ws, "reception", rec)
    assert action == "appended"
    assert len(ws.appended) == 1
    row = ws.appended[0]
    assert row[0] == "A1"        # 車両番号
    assert row[5] == "受付連絡"  # 通知種類


def test_save_record_updates_matching_row():
    ws = FakeWorksheet(data_rows=[["A1", "2026-06-01", "対物", "山田", "", "受付連絡"]])
    pay = {"車両番号": "A1", "発生日": "2026-06-01", "運転者名": "", "支払完了": "はい"}
    action = sheets.save_record(ws, "payment", pay)
    assert action == "updated"
    assert len(ws.updates) == 1
    range_name, values = ws.updates[0]
    # データ1行目 → シート2行目、6列 → F
    assert range_name == "A2:F2"
    assert values[0][4] == "はい"                    # 支払完了
    assert values[0][5] == "受付連絡・支払完了通知"  # 通知種類
    assert values[0][3] == "山田"                    # 運転者名は保持
