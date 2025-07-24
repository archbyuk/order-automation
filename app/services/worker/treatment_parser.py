"""
    시술 내용 파싱 규칙

    오더 양식: {환자이름} / {차트번호} / {시술내용} / {시술위치}

    시술내용 부분의 유연한 양식:
    1. 단일 시술: 시술명 : 횟수 : 회차 : (메모) - 순서 자유
    예: 보톡스 5u : 1회 : 5-1 : (이마 주의)
    예: 미드워크2 : 5-1 (튠페이스 40kj + 튠라이너)  # 횟수 없음
    예: 종아리 보톡스 50u : 2회  # 회차 없음

    2. 복수 시술: 시술명1 : 횟수1 : 회차1 : (메모1) + 시술명2 : 횟수2 : 회차2 : (메모2)
    예: 보톡스 5u : 1회 : 5-1 : (이마 주의) + 울쎄라 300샷 : 1회 : 5-1 : (턱 라인)

    3. 메모 없는 경우: 시술명 : 횟수 : 회차
    예: 보톡스 5u : 1회 : 5-1

    파싱 규칙:
    - '+' 로 시술 분리
    - ':' 로 각 시술의 구성요소 분리
    - 순서 자유: 시술명은 첫 번째, 나머지는 패턴으로 인식
"""

import re
from typing import List
from app.schemas.schemas import ParsedTreatment

class TreatmentParser:
    """시술 텍스트를 파싱하는 클래스"""
    
    def __init__(self):
        # 정규표현식 패턴: 새로운 양식에 맞춰 수정
        self.count_pattern = re.compile(r'(\d+)[\s]*회')  # "1회", "2회" 형태
        self.round_pattern = re.compile(r'(\d+-\d+)')  # "5-1", "1-3" 형태
        self.area_pattern = re.compile(r'\((.*?)\)')  # "(메모)" 형태
    
    # 1. 시술 항목 분리
    def split_treatment_items(self, text: str) -> List[str]:
        """ + 로 시술 항목을 분리 """
        return [item.strip() for item in text.split('+') if item.strip()]
    
    # 2. 단일 시술 항목 파싱 (수정된 버전)
    def parse_single_treatment(self, text: str) -> ParsedTreatment:
        """ 단일 시술 항목을 파싱하여 ParsedTreatment 구조로 반환 (순서 자유) """
        raw = text.strip()
        count = 1
        round_info = None
        area_note = None

        # 괄호 안의 메모 먼저 추출하고 제거
        area_match = self.area_pattern.search(raw)
        if area_match:
            area_note = area_match.group(1)
            # 메모 부분 제거
            raw = self.area_pattern.sub('', raw).strip()

        # ':' 로 구성요소 분리
        parts = [part.strip() for part in raw.split(':') if part.strip()]
        
        if len(parts) >= 1:
            # 첫 번째 부분은 항상 시술명
            name = parts[0].strip()
            
            # 나머지 부분들을 패턴으로 인식하여 파싱
            for part in parts[1:]:
                part = part.strip()
                
                # 횟수 패턴 확인
                count_match = self.count_pattern.search(part)
                if count_match:
                    count = int(count_match.group(1))
                    continue
                
                # 회차 패턴 확인
                round_match = self.round_pattern.search(part)
                if round_match:
                    round_info = round_match.group(1)
                    continue
                
                # 메모가 괄호 없이 남아있는 경우 (예: "튠페이스 40kj + 튠라이너")
                if part and not count_match and not round_match:
                    # 추가 메모로 처리
                    if area_note:
                        area_note += f" {part}"
                    else:
                        area_note = part

        # 파싱된 시술 내용을 ParsedTreatment 모델로 반환
        return ParsedTreatment(
            raw_text=text,
            name=name,
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

