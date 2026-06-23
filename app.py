from datetime import datetime

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


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    st.title("📄 事故書類整理")

    if not check_password():
        return

    doc_label = st.radio("書類の種類", ["①受付", "②支払"], horizontal=True)
    doc_type = "reception" if doc_label == "①受付" else "payment"
    fields = schema.DOC_TYPES[doc_type]

    files = st.file_uploader(
        "書類画像をドラッグ&ドロップ(複数可)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    if not files:
        return

    if st.button("読み取り", type="primary"):
        results = []
        for f in files:
            data = f.getvalue()
            rec = extract.extract_fields(
                data, f.type, doc_type, st.secrets["gemini_api_key"]
            )
            results.append(rec)
        st.session_state["results"] = results
        st.session_state["result_doc_type"] = doc_type

    if "results" not in st.session_state:
        return

    st.subheader("読み取り結果(確認・修正)")
    edited = st.data_editor(
        st.session_state["results"],
        column_order=fields,
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
            st.error(f"スプレッドシート接続に失敗: {e}")
            return

        now = now_str()
        appended = updated = 0
        for rec in edited:
            action = sheets.save_record(
                ws, st.session_state["result_doc_type"], dict(rec), now
            )
            if action == "appended":
                appended += 1
            else:
                updated += 1
        st.success(f"送信完了: 新規 {appended} 件 / 更新 {updated} 件")
        del st.session_state["results"]


if __name__ == "__main__":
    main()
