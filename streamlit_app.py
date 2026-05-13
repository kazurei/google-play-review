import streamlit as st
import pandas as pd
from google_play_scraper import reviews
import time

st.set_page_config(page_title="Google Play Review Scraper", layout="wide")

st.title("Google Play レビュー取得ツール")

st.write("Google Play Store のレビューを取得してCSV保存できます。")

# 入力欄
app_id = st.text_input(
    "アプリID",
    value="jp.co.ponos.battlecats"
)

review_count = st.number_input(
    "取得件数",
    min_value=1000,
    max_value=100000,
    value=10000,
    step=1000
)

lang = st.selectbox(
    "言語",
    ["ja", "en", "ko"],
    index=0
)

country = st.selectbox(
    "国",
    ["jp", "us", "kr"],
    index=0
)

score_filter = st.selectbox(
    "評価フィルタ",
    ["すべて", "★1", "★2", "★3", "★4", "★5"]
)

# 実行ボタン
if st.button("レビュー取得開始"):

    all_reviews = []
    continuation_token = None

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        while len(all_reviews) < review_count:

            result, continuation_token = reviews(
                app_id,
                lang=lang,
                country=country,
                count=200,
                continuation_token=continuation_token
            )

            if not result:
                break

            all_reviews.extend(result)

            progress = min(len(all_reviews) / review_count, 1.0)
            progress_bar.progress(progress)

            status_text.text(f"{len(all_reviews)} 件取得")

            time.sleep(1)

        # DataFrame化
        df = pd.DataFrame([{
            "score": r["score"],
            "date": r["at"],
            "content": r["content"],
            "thumbsUp": r["thumbsUpCount"],
            "replyContent": r["replyContent"],
            "appVersion": r["appVersion"]
        } for r in all_reviews])

        # 評価フィルタ
        if score_filter != "すべて":
            score_num = int(score_filter.replace("★", ""))
            df = df[df["score"] == score_num]

        st.success(f"{len(df)} 件取得完了")

        st.dataframe(df)

        # CSVダウンロード
        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="CSVダウンロード",
            data=csv,
            file_name="reviews.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"エラー: {e}")