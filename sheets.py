import schema
import matcher


def load_rows(worksheet):
    records = worksheet.get_all_records()
    rows = []
    for rec in records:
        row = {c: str(rec.get(c, "") or "") for c in schema.COLUMNS}
        rows.append(row)
    return rows


def _row_to_values(row):
    return [row.get(c, "") for c in schema.COLUMNS]


def save_record(worksheet, doc_type, record):
    rows = load_rows(worksheet)
    vehicle = record.get("車両番号", "")
    date = record.get("発生日", "")
    idx = matcher.find_row_index(rows, vehicle, date)

    new_rows, action = matcher.apply_record(rows, doc_type, record)

    if action == "appended":
        worksheet.append_row(_row_to_values(new_rows[-1]))
    else:  # updated
        sheet_row = idx + 2  # ヘッダ1行 + 0始まりindex
        last_col = chr(ord("A") + len(schema.COLUMNS) - 1)  # 6列 → "F"
        range_name = f"A{sheet_row}:{last_col}{sheet_row}"
        worksheet.update(range_name, [_row_to_values(new_rows[idx])])

    return action


def open_worksheet(sheet_id, service_account_info):
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).sheet1
