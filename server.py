from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import anthropic
import json
import os
from dotenv import load_dotenv
from data_loader import load_latest_keywords
from subsidy_api import fetch_subsidies
from prompt_builder import build_prompt

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@app.get("/")
async def serve_index():
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "index.html"),
        media_type="text/html",
    )


@app.post("/api/diagnose")
async def diagnose(user_input: dict):
    # 1순위: honey-info 크롤링 데이터
    keywords = load_latest_keywords()
    # 2순위: 기업마당 공공 API 실시간 조회
    subsidies = []
    if not keywords:
        subsidies = await fetch_subsidies(user_input.get("business_type", ""))
    prompt = build_prompt(user_input, keywords, subsidies)

    def stream():
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        ) as resp:
            for text in resp.text_stream:
                yield f"data: {json.dumps({'text': text}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/cpa-links")
async def cpa_links():
    return {
        "loan": os.getenv("CPA_URL_LOAN", ""),
        "tax": os.getenv("CPA_URL_TAX", ""),
    }


@app.get("/api/health")
async def health():
    keywords = load_latest_keywords()
    subsidies = await fetch_subsidies("편의점") if not keywords else []
    if keywords:
        source = "honey-info 연동"
    elif subsidies:
        source = "기업마당 API 연동"
    else:
        source = "fallback"
    return {
        "status": "ok",
        "keywords_loaded": len(keywords),
        "subsidies_loaded": len(subsidies),
        "data_source": source,
    }
