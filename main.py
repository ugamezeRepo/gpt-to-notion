from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import os
import datetime

load_dotenv()

app = FastAPI()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

class StockEntry(BaseModel):
    종목명: str
    진입가: float
    진입일시: str  # ISO 문자열 권장
    현재가: float = None
    수익률: float = None
    전략구분: str
    상태: str
    추천사유: str
    긍정시나리오: str
    부정시나리오: str
    중립기타시나리오: str
    확률평가: str
    매도전략: str
    테마분류: str
    단기이벤트일정: str = ""
    공매도비율: float = None
    기관보유율: float = None
    메모기타: str

@app.get("/")
def read_root():
    return {"message": "GPT-to-Notion API is working!"}

@app.post("/save")
async def save_to_notion(data: StockEntry):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    notion_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "종목명": {"title": [{"text": {"content": data.종목명}}]},
            "진입가": {"number": data.진입가},
            "진입 일시": {"date": {"start": data.진입일시}},
            "현재가": {"number": data.현재가} if data.현재가 else None,
            "수익률 (%)": {"number": data.수익률} if data.수익률 else None,
            "전략 구분": {"rich_text": [{"text": {"content": data.전략구분}}]},
            "상태": {"rich_text": [{"text": {"content": data.상태}}]},
            "추천 사유": {"rich_text": [{"text": {"content": data.추천사유}}]},
            "긍정 시나리오": {"rich_text": [{"text": {"content": data.긍정시나리오}}]},
            "부정 시나리오": {"rich_text": [{"text": {"content": data.부정시나리오}}]},
            "중립/기타 시나리오": {"rich_text": [{"text": {"content": data.중립기타시나리오}}]},
            "확률 평가": {"rich_text": [{"text": {"content": data.확률평가}}]},
            "매도 전략": {"rich_text": [{"text": {"content": data.매도전략}}]},
            "테마 분류": {"rich_text": [{"text": {"content": data.테마분류}}]},
            "단기 이벤트 일정": {"rich_text": [{"text": {"content": data.단기이벤트일정}}]},
            "공매도 비율": {"number": data.공매도비율} if data.공매도비율 else None,
            "기관 보유율": {"number": data.기관보유율} if data.기관보유율 else None,
            "메모 / 기타": {"rich_text": [{"text": {"content": data.메모기타}}]}
        }
    }

    # 필드가 None일 경우 제거
    notion_data["properties"] = {
        k: v for k, v in notion_data["properties"].items() if v is not None
    }

    res = requests.post(url, headers=headers, json=notion_data)
    return {"status": res.status_code, "response": res.json()}
