"""
전역 예외 핸들러
커스텀 예외들을 HTTP 응답으로 변환
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions import OrderProcessingError

async def order_processing_error_handler(request: Request, exc: OrderProcessingError):
    """오더 처리 관련 예외 핸들러"""
    
    # 에러 타입 매핑
    error_type_map = {
        400: "PARSING_ERROR",
        404: "TREATMENT_MAPPING_ERROR", 
        503: "DOCTOR_ASSIGNMENT_ERROR",
        409: "SPECIFIED_DOCTOR_ASSIGNMENT_ERROR",
        500: "DATABASE_SAVE_ERROR",
        422: "TREATMENT_PARSING_ERROR"
    }
    
    # 해결 방법 제안
    suggestion_map = {
        400: "환자명/차트번호/시술내용/방번호 형식으로 입력해주세요",
        404: "병원에서 사용하는 시술명으로 입력해주세요",
        503: "현재 배정 가능한 의사가 없습니다. 잠시 후 다시 시도해주세요",
        409: "지명된 의사가 휴무시간이거나 해당 시술을 할 수 없습니다",
        500: "시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요",
        422: "시술 내용을 명확하게 입력해주세요"
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_type": error_type_map.get(exc.status_code, "UNKNOWN_ERROR"),
            "error_message": exc.message,
            "suggestion": suggestion_map.get(exc.status_code, "다시 시도해주세요"),
            "order_id": None
        }
    ) 