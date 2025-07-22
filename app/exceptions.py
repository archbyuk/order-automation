"""
    오더 처리 실패 원인별 커스텀 예외 클래스들
    600번대 상태 코드로 실패 원인을 구분
"""

class OrderProcessingError(Exception):
    """오더 처리 관련 기본 예외 클래스"""
    def __init__(self, message: str, status_code: int = 600):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class OrderParsingError(OrderProcessingError):
    """오더 파싱 실패 (600)"""
    def __init__(self, message: str = "오더 형식이 올바르지 않습니다"):
        super().__init__(message, 600)

class TreatmentParsingError(OrderProcessingError):
    """시술 파싱 실패 (605)"""
    def __init__(self, message: str = "시술 내용을 파싱할 수 없습니다"):
        super().__init__(message, 605)

class TreatmentMappingError(OrderProcessingError):
    """시술 매핑 실패 (601)"""
    def __init__(self, message: str = "입력한 시술을 찾을 수 없습니다"):
        super().__init__(message, 601)

class DoctorAssignmentError(OrderProcessingError):
    """자동 의사 배정 실패 (602)"""
    def __init__(self, message: str = "적절한 의사를 배정할 수 없습니다"):
        super().__init__(message, 602)

class SpecifiedDoctorAssignmentError(OrderProcessingError):
    """지명 의사 배정 실패 (603)"""
    def __init__(self, message: str = "지명된 의사에게 배정할 수 없습니다"):
        super().__init__(message, 603)

class DatabaseSaveError(OrderProcessingError):
    """DB 저장 실패 (604)"""
    def __init__(self, message: str = "데이터베이스 저장에 실패했습니다"):
        super().__init__(message, 604)

class ValidationError(OrderProcessingError):
    """검증 실패 (606)"""
    def __init__(self, message: str = "입력 데이터 검증에 실패했습니다"):
        super().__init__(message, 606) 