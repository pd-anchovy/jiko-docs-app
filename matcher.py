import copy
import unicodedata

import schema


def normalize_plate(value):
    """車両番号を正規化する。

    全角英数字・スペースを半角化(NFKC)し、カタカナはひらがなに変換する
    (例: 横浜４８２レ２７２８ → 横浜482れ2728)。
    """
    s = unicodedata.normalize("NFKC", str(value or "")).strip()
    return "".join(
        chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s
    )


def _plate_key(value):
    """突合用キー。正規化に加えスペースの有無も無視する。"""
    return normalize_plate(value).replace(" ", "")


def find_row_index(rows, vehicle, date):
    key = _plate_key(vehicle)
    date = str(date or "").strip()
    for i, row in enumerate(rows):
        if (_plate_key(row.get("車両番号", "")) == key
                and str(row.get("発生日", "")).strip() == date):
            return i
    return None


def _blank_row():
    return {c: "" for c in schema.COLUMNS}


def _merge_notice(current, label):
    """既存の通知種類にラベルを追加(重複なし・固定順で「・」区切り)。"""
    parts = [p for p in (current or "").split("・") if p]
    if label not in parts:
        parts.append(label)
    order = list(schema.NOTICE_LABELS.values())
    parts.sort(key=lambda p: order.index(p) if p in order else len(order))
    return "・".join(parts)


def apply_record(rows, doc_type, record):
    rows = copy.deepcopy(rows)
    vehicle = normalize_plate(record.get("車両番号", ""))
    date = str(record.get("発生日", "") or "").strip()
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
    elif doc_type == "payment":
        row["車両番号"] = vehicle
        row["発生日"] = date
        row["支払完了"] = record.get("支払完了", "")
        # 完了はがきの被保険者名。空なら受付側の運転者名を保持
        name = record.get("運転者名", "")
        if name:
            row["運転者名"] = name
    else:
        raise ValueError(f"unknown doc_type: {doc_type}")

    row["通知種類"] = _merge_notice(row.get("通知種類", ""),
                                    schema.NOTICE_LABELS[doc_type])

    if idx is None:
        rows.append(row)

    return rows, action
