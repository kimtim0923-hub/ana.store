import httpx
import os
from datetime import datetime

BIZINFO_API_URL = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"
BIZINFO_API_KEY = os.getenv("BIZINFO_API_KEY", "")

# 업종 → 기업마당 분야코드 + 해시태그 매핑
BUSINESS_HASHTAGS = {
    "편의점": "소상공인,유통",
    "카페·커피숍": "소상공인,외식",
    "음식점(한식)": "소상공인,외식",
    "음식점(중식·일식·양식)": "소상공인,외식",
    "치킨·분식·패스트푸드": "소상공인,외식",
    "미용실·네일샵": "소상공인,서비스",
    "옷가게·잡화": "소상공인,패션",
    "학원·교습소": "소상공인,교육",
    "세탁소·수선": "소상공인,서비스",
    "마트·슈퍼": "소상공인,유통",
    "약국": "소상공인,의료",
    "인테리어·건설": "소상공인,건설",
    "온라인쇼핑몰": "소상공인,온라인",
    "기타": "소상공인",
}


async def fetch_subsidies(business_type: str) -> list[dict]:
    """
    기업마당 공공 API에서 업종에 맞는 지원사업 실시간 조회.
    API 키 없거나 실패 시 빈 리스트 반환.
    """
    if not BIZINFO_API_KEY:
        return []

    hashtags = BUSINESS_HASHTAGS.get(business_type, "소상공인")

    params = {
        "crtfcKey": BIZINFO_API_KEY,
        "dataType": "json",
        "searchCnt": "10",
        "hashtags": hashtags,
        "pageUnit": "10",
        "pageIndex": "1",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(BIZINFO_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        items = data.get("jsonArray", [])

        results = []
        for item in items:
            results.append({
                "title": item.get("title", ""),
                "agency": item.get("jrsdInsttNm", item.get("author", "")),
                "description": item.get("bsnsSumryCn", item.get("description", "")),
                "url": item.get("link", ""),
                "period": item.get("reqstBeginEndDe", ""),
                "target": item.get("trgetNm", ""),
                "category": item.get("pldirSportRealmLclasCodeNm", item.get("lcategory", "")),
                "tags": item.get("hashTags", ""),
            })

        return results

    except Exception:
        return []
