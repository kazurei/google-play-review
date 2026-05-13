import streamlit as st
import pandas as pd
from google_play_scraper import reviews, Sort
import time

st.set_page_config(
    page_title="Google Play Review Scraper",
    layout="wide"
)

st.title("Google Play レビュー取得ツール")

st.write(
    "Google Play Store のレビューを取得してCSV保存できます。"
)

# 入力欄
app_id = st.text_input(
    "アプリID",
    value="net.wrightflyer.anothereden"
)

review_count = st.number_input(
    "取得件数",
    min_value=1000,
    max_value=100000,
    value=10000,
    step=1000
)

score_filter = st.selectbox(
    "評価フィルタ",
    ["すべて", "★1", "★2", "★3", "★4", "★5"]
)

# 実行ボタン
if st.button("レビュー取得開始"):

    all_reviews = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:

        # 星ごとの取得設定
        if score_filter == "すべて":
            score_list = [1, 2, 3, 4, 5]
        else:
            score_list = [
                int(score_filter.replace("★", ""))
            ]

        # 星ごとにループ
        for score in score_list:

            continuation_token = None

            status_text.text(f"★{score} 取得中...")

            while len(all_reviews) < review_count:

                result, continuation_token = reviews(
                    app_id,
                    sort=Sort.NEWEST,
                    filter_score_with=score,
                    count=200,
                    continuation_token=continuation_token
                )

                if not result:
                    break

                all_reviews.extend(result)

                progress = min(
                    len(all_reviews) / review_count,
                    1.0
                )

                progress_bar.progress(progress)

                status_text.text(
                    f"★{score} | "
                    f"{len(all_reviews)} 件取得"
                )

                time.sleep(1)

                if continuation_token is None:
                    break

        # DataFrame化
        df = pd.DataFrame([{
            "score": r["score"],
            "date": r["at"],
            "content": r["content"],
            "thumbsUp": r["thumbsUpCount"],
            "replyContent": r["replyContent"],
            "appVersion": r["appVersion"]
        } for r in all_reviews])

        # 重複削除
        df = df.drop_duplicates(
            subset=["date", "content"]
        )

        st.success(
            f"{len(df)} 件取得完了"
        )

        st.dataframe(df)

        # CSVダウンロード
        csv = df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="CSVダウンロード",
            data=csv,
            file_name="reviews.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"エラー: {e}")