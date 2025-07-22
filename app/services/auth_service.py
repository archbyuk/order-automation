"""
인증 관련 서비스 로직
"""
from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.schemas import LoginRequest, LoginResponse
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(db: Session, email: str, password: str) -> User:
    """사용자 인증"""
    # 이메일로 사용자 찾기
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return None
    
    # 비밀번호 검증
    if not verify_password(password, user.hashed_password):
        return None
    
    # 계정 활성화 상태 확인
    if not user.is_active:
        return None
    
    return user

def login_user(db: Session, login_data: LoginRequest) -> LoginResponse:
    """사용자 로그인"""
    try:
        # 사용자 인증
        user = authenticate_user(db, login_data.email, login_data.password)
        
        if not user:
            return LoginResponse(
                success=False,
                message="이메일 또는 비밀번호가 올바르지 않습니다."
            )
        
        # 로그인 성공
        return LoginResponse(
            success=True,
            user_id=user.user_id,
            hospital_id=user.hospital_id,
            name=user.name,
            role=user.role,
            is_doctor=user.is_doctor,
            message="로그인에 성공했습니다."
        )
        
    except Exception as e:
        return LoginResponse(
            success=False,
            message=f"로그인 중 오류가 발생했습니다: {str(e)}"
        ) 