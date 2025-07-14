import re
from typing import List, Optional
from pydantic import BaseModel

# 파싱된 '시술 내용'을 담는 데이터 모델: 원본 오더, 시술 이름, 횟수, 회차, 부위 메모
class ParsedTreatment(BaseModel):
    raw_text: str
    name: str
    count: int = 1
    round_info: Optional[str] = None
    area_note: Optional[str] = None

# 정규표현식 패턴: 회차나 부위가 포함된 시술 텍스트를 처리
COUNT_PATTERN = re.compile(r'(\d+)[\s]*회')
ROUND_PATTERN = re.compile(r'\((\d+-\d+)\)')
AREA_PATTERN = re.compile(r'\((.*?)\)$')

def split_treatment_items(text: str) -> List[str]:
    """ + 또는 , 로 시술 항목을 분리 """
    return [item.strip() for item in re.split(r'[+,]', text) if item.strip()]

def parse_single_treatment(text: str) -> ParsedTreatment:
    """ 단일 시술 항목을 파싱하여 ParsedTreatment 구조로 반환 """
    raw = text.strip()
    count = 1
    round_info = None
    area_note = None

    # 회차 정보 추출
    round_match = ROUND_PATTERN.search(raw)
    if round_match:
        round_info = round_match.group(1)
        raw = ROUND_PATTERN.sub('', raw)

    # 부위 메모 추출
    area_match = AREA_PATTERN.search(raw)
    if area_match:
        area_note = area_match.group(1)
        raw = AREA_PATTERN.sub('', raw)

    # 횟수 추출
    count_match = COUNT_PATTERN.search(raw)
    if count_match:
        count = int(count_match.group(1))
        raw = COUNT_PATTERN.sub('', raw)

    # 파싱된 시술 내용을 ParsedTreatment 모델로 반환
    return ParsedTreatment(
        raw_text=text,
        name=raw.strip(),
        count=count,
        round_info=round_info,
        area_note=area_note
    )

def parse_treatment_text(raw_text: str) -> List[ParsedTreatment]:
    """ 전체 시술 텍스트를 분리 및 파싱하여 리스트 반환 """
    items = split_treatment_items(raw_text)
    
    return [parse_single_treatment(item) for item in items]