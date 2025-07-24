from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import os
import datetime

load_dotenv()

app = FastAPI()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

class NotionRequest(BaseModel):
    question: str
    answer: str

@app.post("/save")
async def save_to_notion(data: NotionRequest):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    notion_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "질문": {
                "title": [{"text": {"content": data.question}}]
            },
            "답변": {
                "rich_text": [{"text": {"content": data.answer}}]
            },
            "날짜": {
                "date": {"start": datetime.datetime.utcnow().isoformat()}
            }
        }
    }
    res = requests.post(url, headers=headers, json=notion_data)
    return {"status": res.status_code, "response": res.json()}