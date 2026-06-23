COLUMNS = [
    "車両番号", "発生日", "補償の種類", "運転者名",
    "受付登録日時", "支払完了", "支払登録日時",
]

RECEPTION_FIELDS = ["車両番号", "発生日", "補償の種類", "運転者名"]
PAYMENT_FIELDS = ["車両番号", "発生日", "支払完了"]

DOC_TYPES = {
    "reception": RECEPTION_FIELDS,
    "payment": PAYMENT_FIELDS,
}
