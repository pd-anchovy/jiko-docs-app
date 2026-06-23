import copy
import schema


def find_row_index(rows, vehicle, date):
    for i, row in enumerate(rows):
        if row.get("車両番号", "") == vehicle and row.get("発生日", "") == date:
            return i
    return None


def _blank_row():
    return {c: "" for c in schema.COLUMNS}


def apply_record(rows, doc_type, record, now):
    rows = copy.deepcopy(rows)
    vehicle = record.get("車両番号", "")
    date = record.get("発生日", "")
    idx = find_row_index(rows, vehicle, date)

    if idx is None:
        row = _blank_row()
        action = "appended"
    else:
        row = rows[idx]
        action = "updated"

    if doc_type == "reception":
        row["車両番号"] = vehicle
        row["発生日"] = date
        row["補償の種類"] = record.get("補償の種類", "")
        row["運転者名"] = record.get("運転者名", "")
        row["受付登録日時"] = now
    elif doc_type == "payment":
        row["車両番号"] = vehicle
        row["発生日"] = date
        row["支払完了"] = record.get("支払完了", "")
        row["支払登録日時"] = now
    else:
        raise ValueError(f"unknown doc_type: {doc_type}")

    if idx is None:
        rows.append(row)

    return rows, action
