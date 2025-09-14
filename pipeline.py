import feedparser
import requests
import os
from azure.storage.blob import BlobServiceClient
from datetime import datetime

# -------------------------------
# CONFIG (edit these in GitHub Secrets)
# -------------------------------
DASH_RSS_FEED = "https://dash.harvard.edu/feed/rss_1.0/site"  # DASH site-wide RSS feed
DOWNLOAD_DIR = "downloads"  # temporary storage folder

AZURE_CONNECTION_STRING = os.environ.get("AZURE_CONNECTION_STRING")
CONTAINER_NAME = "law-dropzone"

# -------------------------------
# Step 1: Ensure download folder exists
# -------------------------------
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# -------------------------------
# Step 2: Connect to Azure Blob
# -------------------------------
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# -------------------------------
# Step 3: Fetch DASH RSS feed
# -------------------------------
feed = feedparser.parse(DASH_RSS_FEED)

print(f"[{datetime.now()}] Found {len(feed.entries)} entries in DASH feed...")

for entry in feed.entries:
    title = entry.title.replace(" ", "_").replace("/", "_")
    link = entry.link

    if not link.endswith(".pdf"):
        continue

    pdf_filename = f"{title}.pdf"
    pdf_path = os.path.join(DOWNLOAD_DIR, pdf_filename)

    # -------------------------------
    # Step 4: Download PDF
    # -------------------------------
    if not os.path.exists(pdf_path):
        print(f"Downloading: {title}")
        r = requests.get(link)
        with open(pdf_path, "wb") as f:
            f.write(r.content)
    else:
        print(f"Already downloaded: {title}")

    # -------------------------------
    # Step 5: Upload to Azure Blob
    # -------------------------------
    blob_client = container_client.get_blob_client(pdf_filename)

    with open(pdf_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
        print(f"Uploaded {pdf_filename} → Blob container '{CONTAINER_NAME}'")

print("✅ Pipeline run complete. Harvard papers now in law-dropzone.")
