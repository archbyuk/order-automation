from typing import Optional, Tuple, List
from pydantic import BaseModel, validator
import re
import logging
from app.exceptions import OrderParsingError, ValidationError

# 로깅 설정: 로그를 체계적으로 기록하기 위함
logger = logging.getLogger(__name__)

# 1. 파싱할 템플릿 패턴 정의 (환자이름 / 차트번호 / 시술내용 / 방번호 / 의사이름(선택적))
TEMPLATE_PATTERNS: List[re.Pattern] = [
    re.compile(r'^(.+?)\s*/\s*(\d+)\s*/\s*(.+?)\s*/\s*(.+?)\s*/\s*(.+)$'),  # 5개 필드 (지명 의사)
    re.compile(r'^(.+?)\s*/\s*(\d+)\s*/\s*(.+?)\s*/\s*(.+)$'),              # 4개 필드 (자동 배정)
]

# 2. 파싱된 오더 정보를 담는 데이터 모델 정의: 7번에서 사용
class ParsedOrder(BaseModel):
    """파싱된 오더 정보를 담는 모델"""
    patient_name: str
    chart_number: str
    treatment: str
    room: str
    raw_text: str
    doctor_name: Optional[str] = None  # 지명 의사 (선택적)

    # 환자 이름 검증 (최소 2글자 이상)
    @validator('patient_name')
    def validate_patient_name(cls, v):
        if len(v) < 2:
            raise ValidationError("환자 이름이 너무 짧습니다")
        return v

    # 차트 번호 검증 (숫자만 허용)
    @validator('chart_number')
    def validate_chart_number(cls, v):
        if not v.isdigit():
            raise ValidationError("차트 번호는 숫자만 입력 가능합니다")
        return v

    # 시술 내용 검증 (최소 2글자 이상)
    @validator('treatment')
    def validate_treatment(cls, v):
        if len(v) < 2:
            raise ValidationError("시술 내용이 너무 짧습니다")
        return v

    # 방 번호 검증 (최소 2글자 이상)
    @validator('room')
    def validate_room(cls, v):
        if len(v) < 2:
            raise ValidationError("방 번호가 너무 짧습니다")
        return v

    # 지명 의사 이름 검증 (선택적, 있으면 최소 2글자 이상)
    @validator('doctor_name')
    def validate_doctor_name(cls, v):
        if v is not None and len(v) < 2:
            raise ValidationError("의사 이름이 너무 짧습니다")
        return v

# 3. 오더 텍스트를 파싱하는 메인 클래스
class OrderParser:
    """오더 텍스트를 파싱하는 클래스"""

    # 메인 파싱 함수
    def parse(self, raw_text: str) -> Optional[ParsedOrder]:
        try:
            # 4. 입력 텍스트 정규화 (앞뒤 공백 제거)
            normalized_text = raw_text.strip()
            
            # 5. 텍스트에서 필드 추출
            fields = self._extract_fields(normalized_text)
            
            if not fields:
                raise OrderParsingError(f"오더 형식이 올바르지 않습니다. 입력: {raw_text}")

            # 6. 추출된 필드들을 개별 변수로 할당
            if len(fields) == 5:
                # 5개 필드: 지명 의사가 있는 경우
                patient_name, chart_number, treatment, room, doctor_name = fields
            else:
                # 4개 필드: 자동 배정인 경우
            patient_name, chart_number, treatment, room = fields
                doctor_name = None

            # 7. ParsedOrder 객체 생성 (검증 포함)
            parsed = ParsedOrder(
                patient_name=patient_name,
                chart_number=chart_number,
                treatment=treatment,
                room=room,
                raw_text=raw_text,
                doctor_name=doctor_name
            )
            return parsed
        
        # 3-1. 파싱 중 오류 발생 시 예외 발생
        except (OrderParsingError, ValidationError):
            # 커스텀 예외는 그대로 재발생
            raise
        except Exception as e:
            logger.warning(f"파싱 중 예상치 못한 오류 발생: {e}, 입력: {raw_text}")
            raise OrderParsingError(f"오더 파싱 중 오류가 발생했습니다: {str(e)}")

    # 8. 정규표현식을 사용하여 텍스트에서 필드 추출하는 내부 함수
    def _extract_fields(self, text: str) -> Optional[Tuple[str, ...]]:
        # 순차적으로 패턴 매칭 시도: 시간 복잡도 O(n)
        for pattern in TEMPLATE_PATTERNS:
            match = pattern.match(text)
            
            if match:
                # 매칭된 그룹들을 공백 제거 후 튜플로 반환
                return tuple(group.strip() for group in match.groups())
        
        return None

    # 9. 파싱과 검증을 함께 수행하는 통합 함수
    def parse_with_validation(self, raw_text: str) -> Tuple[bool, Optional[ParsedOrder], str]:
        # 파싱 실행
        try:
        parsed = self.parse(raw_text)
        return True, parsed, ""
        except (OrderParsingError, ValidationError) as e:
            return False, None, str(e)

# 전역 인스턴스 생성 (다른 모듈에서 import하여 사용)
order_parser = OrderParser()