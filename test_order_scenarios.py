"""
오더 시나리오 테스트 스크립트
단일시술, 단일시술 복수, 그룹시술, 그룹시술 복수를 모두 테스트합니다.
"""
import requests
import json
import time

# API 기본 설정
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/v1/orders/create"

# 테스트용 병원 및 사용자 ID (시드 데이터 기준)
HOSPITAL_ID = 1
USER_ID = 1

def test_order_scenario(scenario_name: str, order_text: str):
    """개별 오더 시나리오를 테스트하는 함수"""
    print(f"\n{'='*60}")
    print(f"🧪 테스트 시나리오: {scenario_name}")
    print(f"📝 오더 텍스트: {order_text}")
    print(f"{'='*60}")
    
    # API 요청 데이터
    payload = {
        "hospital_id": HOSPITAL_ID,
        "user_id": USER_ID,
        "order_text": order_text
    }
    
    try:
        # API 호출
        print("🚀 API 요청 중...")
        response = requests.post(API_ENDPOINT, json=payload)
        
        # 응답 확인
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API 성공!")
            print(f"   - 오더 ID: {result['order_id']}")
            print(f"   - 메시지: {result['message']}")
            return result['order_id']
        else:
            print(f"❌ API 실패: {response.status_code}")
            print(f"   - 응답: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ API 호출 중 오류: {e}")
        return None

def wait_for_worker_processing():
    """Worker가 메시지를 처리할 시간을 기다리는 함수"""
    print("⏳ Worker 처리 대기 중... (3초)")
    time.sleep(3)

def main():
    """모든 시나리오를 순차적으로 테스트"""
    print("🎯 오더 시나리오 테스트 시작")
    print(f"🏥 병원 ID: {HOSPITAL_ID}")
    print(f"👨‍⚕️ 사용자 ID: {USER_ID}")
    
    # 테스트 시나리오들
    scenarios = [
        {
            "name": "단일 시술",
            "order_text": "김환자 / 12345 / 보톡스 5u / 1번실"
        },
        {
            "name": "단일 시술 복수 (쉼표로 구분)",
            "order_text": "이환자 / 23456 / 보톡스 5u, 울쎄라 300 / 2번실"
        },
        {
            "name": "단일 시술 복수 (플러스로 구분)",
            "order_text": "박환자 / 34567 / 보톡스 5u + 필러 1cc / 3번실"
        },
        {
            "name": "그룹 시술",
            "order_text": "최환자 / 45678 / 패키지A / 4번실"
        },
        {
            "name": "그룹 시술 복수",
            "order_text": "정환자 / 56789 / 패키지A + 패키지B / 5번실"
        },
        {
            "name": "복합 시술 (단일 + 그룹)",
            "order_text": "한환자 / 67890 / 보톡스 5u + 패키지A / 6번실"
        },
        {
            "name": "횟수가 포함된 시술",
            "order_text": "윤환자 / 78901 / 보톡스 5u 2회 / 7번실"
        },
        {
            "name": "회차 정보가 포함된 시술",
            "order_text": "임환자 / 89012 / 울쎄라 300 (1-3) / 8번실"
        }
    ]
    
    # 각 시나리오 테스트
    order_ids = []
    for scenario in scenarios:
        order_id = test_order_scenario(scenario["name"], scenario["order_text"])
        if order_id:
            order_ids.append(order_id)
        
        # Worker 처리 대기
        wait_for_worker_processing()
    
    # 테스트 결과 요약
    print(f"\n{'='*60}")
    print("📊 테스트 결과 요약")
    print(f"{'='*60}")
    print(f"✅ 성공한 테스트: {len(order_ids)}개")
    print(f"❌ 실패한 테스트: {len(scenarios) - len(order_ids)}개")
    
    if order_ids:
        print(f"\n📋 생성된 오더 ID들:")
        for i, order_id in enumerate(order_ids, 1):
            print(f"   {i}. 오더 ID: {order_id}")
    
    print(f"\n🎉 테스트 완료!")

if __name__ == "__main__":
    main() 