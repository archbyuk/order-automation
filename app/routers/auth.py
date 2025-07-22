"""
인증 관련 API 라우터
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import LoginRequest, LoginResponse
from app.services.auth_service import login_user

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """사용자 로그인"""
    try:
        result = login_user(db, login_data)
        
        if not result.success:
            raise HTTPException(status_code=401, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 처리 중 오류가 발생했습니다: {str(e)}")

@router.get("/me")
def get_current_user_info(user_id: int, hospital_id: int, db: Session = Depends(get_db)):
    """현재 사용자 정보 조회"""
    try:
        from app.models.users import User
        user = db.query(User).filter(User.user_id == user_id, User.hospital_id == hospital_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        return {
            "user_id": user.user_id,
            "hospital_id": user.hospital_id,
            "name": user.name,
            "role": user.role,
            "is_doctor": user.is_doctor,
            "email": user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 정보 조회 중 오류가 발생했습니다: {str(e)}") 