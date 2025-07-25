import os
import json
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 🔧 환경변수 또는 직접 설정
NOTION_API_URL = "https://gpt-to-notion.onrender.com/save"
WATCH_FOLDER = "./pending_notion"
UPLOADED_FOLDER = "./uploaded_notion"
FAILED_FOLDER = "./failed_notion"

class NotionUploader(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".json"):
            time.sleep(0.5)  # 파일 완전히 저장되기까지 대기
            try:
                with open(event.src_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"📤 Sending to Notion: {os.path.basename(event.src_path)}")

                res = requests.post(NOTION_API_URL, json=data)

                if res.status_code == 200:
                    print("✅ Successfully uploaded to Notion!")
                    self._move_file(event.src_path, UPLOADED_FOLDER)
                else:
                    print(f"❌ Failed to upload. Status: {res.status_code}, Response: {res.text}")
                    self._move_file(event.src_path, FAILED_FOLDER)
            except Exception as e:
                print(f"⚠️ Error processing file {event.src_path}: {e}")
                self._move_file(event.src_path, FAILED_FOLDER)

    def _move_file(self, src, dst_folder):
        os.makedirs(dst_folder, exist_ok=True)
        dst_path = os.path.join(dst_folder, os.path.basename(src))
        os.rename(src, dst_path)
        print(f"📦 Moved file to {dst_folder}/")

if __name__ == "__main__":
    for folder in [WATCH_FOLDER, UPLOADED_FOLDER, FAILED_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    print(f"👀 Watching folder: {WATCH_FOLDER} for new JSON files...")
    event_handler = NotionUploader()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_FOLDER, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("🛑 Stopped watching.")

    observer.join()
