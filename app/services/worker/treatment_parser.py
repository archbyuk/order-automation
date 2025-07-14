import re
from typing import List
from app.schemas.schemas import ParsedTreatment

class TreatmentParser:
    """시술 텍스트를 파싱하는 클래스"""
    
    def __init__(self):
        # 정규표현식 패턴: 회차나 부위가 포함된 시술 텍스트를 처리
        self.count_pattern = re.compile(r'(\d+)[\s]*회')
        self.round_pattern = re.compile(r'\((\d+-\d+)\)')
        self.area_pattern = re.compile(r'\((.*?)\)$')
    
    # 1. 시술 항목 분리
    def split_treatment_items(self, text: str) -> List[str]:
        """ + 또는 , 로 시술 항목을 분리 """
        return [item.strip() for item in re.split(r'[+,]', text) if item.strip()]
    
    # 2. 단일 시술 항목 파싱
    def parse_single_treatment(self, text: str) -> ParsedTreatment:
        """ 단일 시술 항목을 파싱하여 ParsedTreatment 구조로 반환 """
        raw = text.strip()
        count = 1
        round_info = None
        area_note = None

        # 회차 정보 추출
        round_match = self.round_pattern.search(raw)
        if round_match:
            round_info = round_match.group(1)
            raw = self.round_pattern.sub('', raw)

        # 부위 메모 추출
        area_match = self.area_pattern.search(raw)
        if area_match:
            area_note = area_match.group(1)
            raw = self.area_pattern.sub('', raw)

        # 횟수 추출
        count_match = self.count_pattern.search(raw)
        if count_match:
            count = int(count_match.group(1))
            raw = self.count_pattern.sub('', raw)

        # 파싱된 시술 내용을 ParsedTreatment 모델로 반환 (List 형태. 예: [ParsedTreatment, ParsedTreatment, ...])
        return ParsedTreatment(
            raw_text=text,
            name=raw.strip(),
            count=count,
            round_info=round_info,
            area_note=area_note
        )
    
    # 3. 전체 시술 텍스트 파싱
    def parse_treatment_text(self, raw_text: str) -> List[ParsedTreatment]:
        """ 전체 시술 텍스트를 분리 및 파싱하여 리스트 반환 """
        items = self.split_treatment_items(raw_text)
        
        return [self.parse_single_treatment(item) for item in items]


# 전역 인스턴스 생성 (다른 모듈에서 import하여 사용)
treatment_parser = TreatmentParser()

