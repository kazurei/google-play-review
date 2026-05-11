from google_play_scraper import reviews

result, _ = reviews(
    'com.YostarJP.BlueArchive',
    lang='ja',
    country='jp',
    count=100
)

for r in result:
    print(r['score'], r['content'])