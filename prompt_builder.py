def build_prompt(user_input: dict, keywords: list[dict], subsidies: list[dict] = None) -> str:
    """
    사용자 입력 + 지원금 데이터를 조합하여 Claude 프롬프트 생성.
    데이터 우선순위: honey-info > 기업마당 API > 없음
    """
    if subsidies is None:
        subsidies = []

    # 1순위: honey-info 크롤링 데이터
    if keywords:
        subsidy_context = "\n".join(
            [
                f"- [{item.get('agency', '')}] {item.get('keyword', '')} "
                f"(출처: {item.get('source_url', '')})"
                for item in keywords
            ]
        )
        data_source = "honey-info 크롤링"
    # 2순위: 기업마당 공공 API 실시간 데이터
    elif subsidies:
        subsidy_context = "\n".join(
            [
                f"- [{item.get('agency', '')}] {item.get('title', '')}\n"
                f"  설명: {item.get('description', '')}\n"
                f"  신청기간: {item.get('period', '확인필요')}\n"
                f"  대상: {item.get('target', '')}\n"
                f"  상세페이지: {item.get('url', '')}"
                for item in subsidies
            ]
        )
        data_source = "기업마당 공공API 실시간 조회"
    else:
        subsidy_context = "오늘 수집된 신규 지원금 데이터 없음 (기존 지식 기반으로 진단)"
        data_source = "없음"

    return f"""당신은 소상공인 전문 경영 컨설턴트입니다.
아래 가게 정보와 오늘 공공포털에서 수집된 실제 지원금 데이터를 바탕으로
이 가게만을 위한 맞춤 진단 리포트를 작성하세요.

## 가게 정보
- 업종: {user_input['business_type']}
- 월 매출: 약 {user_input['monthly_revenue']}만 원
- 영업 연수: {user_input['years_open']}년
- 직원 수: {user_input['employees']}명
- 주요 고민: {user_input['main_concern']}

## 오늘 지원금 데이터 (출처: {data_source})
{subsidy_context}

## 리포트 작성 규칙
1. 전문 용어 없이 사장님 눈높이로 작성 (중학생도 이해 가능한 언어)
2. "이 업종" "이 매출 규모"에 딱 맞는 이야기만 (일반론 금지)
3. 수치가 있으면 반드시 포함 (지원금액, 절약 가능 금액 등)
4. 위의 데이터 중 이 가게에 해당되는 것은 반드시 언급
5. 총 400~600자 이내로 간결하게
6. **모든 지원금·정책을 언급할 때 반드시 출처 링크를 마크다운 링크로 포함**
   - 위 데이터에 상세페이지 URL이 있으면 그대로 사용: [지원사업명](상세페이지URL)
   - URL이 없는 정책은 절대 언급하지 마세요. 출처 없는 정책 언급 금지.

## 리포트 구조 (이 순서 반드시 준수)
### 현재 상황 진단
(가게 상황을 1~2문장으로 요약. "이 매출 규모에서 가장 큰 리스크는 ~입니다" 형식)

### 지금 당장 받을 수 있는 지원금
(위 데이터 기반으로만 작성. 각 항목에 반드시 [지원사업명](URL) 클릭 링크 포함)

### 이 가게가 놓치고 있는 것
(고민과 매출 기반으로 1~2가지. 구체적 절약 금액 포함)

### 다음 단계 추천
(오늘 당장 할 수 있는 행동 1가지만. 명확하게)"""
