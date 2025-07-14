# 오더에 대한 요청/응답 스키마 정의
from pydantic import BaseModel
from typing import Optional

# 사용자가 오더 요청을 보낼 때 사용하는 스키마
class OrderCreateRequest(BaseModel):
    hospital_id: str    # hospital_id
    user_id: int        # user_id
    order_text: str     # row_order_text
    created_by: Optional[int] = None

# 오더 요쳥에 따른 클라이언트 응답용 스키마
class OrderCreateResponse(BaseModel):
    order_id: int
    message: str