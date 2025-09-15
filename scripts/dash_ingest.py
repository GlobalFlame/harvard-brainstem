import os, requests, feedparser
from azure.storage.blob import BlobServiceClient

# Harvard DASH Law feed (example collection)
DASH_FEED_URL = "https://dash.harvard.edu/feed/rss_2.0/1741.1/34902198"

conn_str = os.environ["AZURE_STORAGE_CONN_STRING"]
container_name = "law-dropzone"

blob_service = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service.get_container_client(container_name)

feed = feedparser.parse(DASH_FEED_URL)

for entry in feed.entries:
    for link in entry.links:
        if link.type == "application/pdf":
            pdf_url = link.href
            pdf_name = pdf_url.split("/")[-1]

            if any(b.name == pdf_name for b in container_client.list_blobs()):
                print(f"⏭️ Skipping {pdf_name}")
                continue

            print(f"📥 Downloading {pdf_name}")
            r = requests.get(pdf_url)
            if r.status_code == 200:
                container_client.upload_blob(pdf_name, r.content)
                print(f"✅ Uploaded {pdf_name} to Azure law-dropzone")
            else:
                print(f"❌ Failed {pdf_url}")
