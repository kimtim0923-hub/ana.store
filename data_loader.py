import json
import os

HONEY_INFO_OUTPUT = os.path.join(
    os.path.dirname(__file__), "..", "honey-info", "output", "latest_keywords.json"
)
FALLBACK_DATA = []


def load_latest_keywords() -> list[dict]:
    """
    honey-info가 오늘 수집한 최신 지원금 키워드 로드.
    파일 없으면 빈 리스트 반환 (도구는 항상 동작해야 함).
    """
    try:
        if not os.path.exists(HONEY_INFO_OUTPUT):
            return FALLBACK_DATA

        with open(HONEY_INFO_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)

        high_value = [d for d in data if d.get("action_value") == "high"]
        return high_value[:10] if high_value else data[:10]

    except Exception:
        return FALLBACK_DATA
