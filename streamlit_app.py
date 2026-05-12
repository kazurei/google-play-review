import streamlit as st
import pandas as pd
from google_play_scraper import reviews
import time
import os

st.set_page_config(page_title="大量レビュー収集", layout="wide")

st.title("Google Play 大量レビュー収集")

app_id = st.text_input(
    value="input"
)

target_count = st.number_input(
    "取得件数",
    min_value=1000,
    max_value=500000,
    value=100000,
    step=1000
)

lang = st.selectbox("言語", ["ja", "en"], index=0)
country = st.selectbox("国", ["jp", "us"], index=0)

if st.button("収集開始"):

    progress = st.progress(0)
    status = st.empty()

    continuation_token = None
    total_reviews = 0

    output_file = "reviews_large.csv"

    # 既存ファイル削除
    if os.path.exists(output_file):
        os.remove(output_file)

    header_written = False

    try:

        while total_reviews < target_count:

            result, continuation_token = reviews(
                app_id,
                lang=lang,
                country=country,
                count=200,
                continuation_token=continuation_token
            )

            if not result:
                st.warning("これ以上レビューがありません")
                break

            rows = []

            for r in result:
                rows.append({
                    "score": r["score"],
                    "date": r["at"],
                    "content": r["content"],
                    "thumbsUp": r["thumbsUpCount"],
                    "replyContent": r["replyContent"],
                    "appVersion": r["appVersion"]
                })

            df = pd.DataFrame(rows)

            # CSV追記保存
            df.to_csv(
                output_file,
                mode="a",
                index=False,
                header=not header_written,
                encoding="utf-8-sig"
            )

            header_written = True

            total_reviews += len(df)

            progress.progress(
                min(total_reviews / target_count, 1.0)
            )

            status.text(f"{total_reviews} 件取得")

            # アクセス制限対策
            time.sleep(1)

        st.success(f"{total_reviews} 件保存完了")

        with open(output_file, "rb") as f:
            st.download_button(
                "CSVダウンロード",
                data=f,
                file_name=output_file,
                mime="text/csv"
            )

    except Exception as e:
        st.error(str(e))