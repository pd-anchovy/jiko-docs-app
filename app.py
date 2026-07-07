import streamlit as st

import schema
import extract
import sheets

st.set_page_config(page_title="事故書類整理", page_icon="📄")


def check_password():
    if st.session_state.get("authed"):
        return True
    pw = st.text_input("パスワード", type="password")
    if pw and pw == st.secrets["app_password"]:
        st.session_state["authed"] = True
        st.rerun()
    elif pw:
        st.error("パスワードが違います")
    return False


def err_detail(e):
    """例外チェーンを辿って中身のあるメッセージを返す。

    gspread は本当のAPIエラーを中身が空の PermissionError に包み直すため、
    str(e) が空のときは __cause__ 側の実メッセージを拾う。
    """
    cur = e
    while cur is not None:
        msg = str(cur).strip()
        if msg:
            return f"{type(cur).__name__}: {msg}"
        cur = cur.__cause__ or cur.__context__
    return f"{type(e).__name__}（詳細メッセージなし）"


def main():
    st.title("📄 事故書類整理")

    if not check_password():
        return

    st.caption("受付連絡・支払完了はがきを混ぜてアップロードできます。種類は自動判定されます。")

    files = st.file_uploader(
        "書類画像をドラッグ&ドロップ(複数可)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    if not files:
        return

    if st.button("読み取り", type="primary"):
        results = []
        try:
            for f in files:
                data = f.getvalue()
                rec = extract.extract_fields(
                    data, f.type, st.secrets["gemini_api_key"]
                )
                results.append(rec)
        except Exception as e:  # noqa: BLE001
            st.error(f"画像の読み取りに失敗: {err_detail(e)}")
            return
        st.session_state["results"] = results

    if "results" not in st.session_state:
        return

    st.subheader("読み取り結果(確認・修正)")
    st.caption("「書類種別」は 受付 / 支払 のどちらかです。誤判定はここで修正してください。")
    edited = st.data_editor(
        st.session_state["results"],
        column_order=schema.EXTRACT_FIELDS,
        num_rows="fixed",
        use_container_width=True,
        key="editor",
    )

    if st.button("スプレッドシートに送信"):
        try:
            ws = sheets.open_worksheet(
                st.secrets["sheet_id"],
                dict(st.secrets["gcp_service_account"]),
            )
        except Exception as e:  # noqa: BLE001
            st.error(f"スプレッドシート接続に失敗: {err_detail(e)}")
            return

        appended = updated = 0
        skipped = []
        try:
            for i, rec in enumerate(edited, start=1):
                label = str(rec.get("書類種別", "")).strip()
                doc_type = schema.DOC_LABELS.get(label)
                if doc_type is None:
                    skipped.append(i)
                    continue
                action = sheets.save_record(ws, doc_type, dict(rec))
                if action == "appended":
                    appended += 1
                else:
                    updated += 1
        except Exception as e:  # noqa: BLE001
            st.error(f"スプレッドシートへの書き込みに失敗: {err_detail(e)}")
            return

        st.success(f"送信完了: 新規 {appended} 件 / 更新 {updated} 件")
        if skipped:
            st.warning(
                f"書類種別が不明のため送信しなかった行: {', '.join(map(str, skipped))} 行目。"
                "「受付」か「支払」を入力して再送信してください(送信済みの行は重複しません)。"
            )
        else:
            del st.session_state["results"]


if __name__ == "__main__":
    main()
