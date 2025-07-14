#!/usr/bin/env python3
"""
시드 데이터 생성 스크립트
같은 병원에 여러 의사가 있는 환경을 구성
"""
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    Hospital, User, TreatmentCategory, HospitalTreatment,
    TreatmentGroup, TreatmentGroupItem, DoctorProfile
)
import json

def create_seed_data():
    """시드 데이터 생성"""
    db = next(get_db())
    
    try:
        print("🌱 시드 데이터 생성 시작...")
        
        # 1. 기존 병원 확인 또는 새 병원 생성
        print("🏥 병원 확인/생성 중...")
        existing_hospital = db.query(Hospital).filter(Hospital.name == "서울성형외과").first()
        
        if existing_hospital:
            hospital = existing_hospital
            print(f"✅ 기존 병원 사용: {hospital.name} (ID: {hospital.hospital_id})")
        else:
            hospital = Hospital(
                name="서울성형외과",
                address="서울시 강남구 테헤란로 123",
                is_active=True
            )
            db.add(hospital)
            db.flush()
            print(f"✅ 새 병원 생성: {hospital.name} (ID: {hospital.hospital_id})")
        
        # 2. 기존 시술 카테고리 확인 또는 생성
        print("📋 시술 카테고리 확인/생성 중...")
        category_map = {}
        categories = [
            {"name": "보톡스", "description": "보톡스 시술"},
            {"name": "필러", "description": "필러 시술"},
            {"name": "레이저", "description": "레이저 시술"},
            {"name": "울쎄라", "description": "울쎄라 시술"}
        ]
        
        for cat_data in categories:
            existing_category = db.query(TreatmentCategory).filter(
                TreatmentCategory.name == cat_data["name"]
            ).first()
            
            if existing_category:
                category_map[cat_data["name"]] = existing_category
                print(f"   - 기존 카테고리 사용: {existing_category.name}")
            else:
                category = TreatmentCategory(
                    name=cat_data["name"],
                    description=cat_data["description"],
                    is_active=True
                )
                db.add(category)
                db.flush()
                category_map[cat_data["name"]] = category
                print(f"   - 새 카테고리 생성: {category.name}")
        
        # 3. 기존 시술 확인 또는 생성
        print("💉 병원별 시술 확인/생성 중...")
        treatment_map = {}
        treatments = [
            {"name": "보톡스 5u", "category_name": "보톡스", "duration": 30},
            {"name": "보톡스 10u", "category_name": "보톡스", "duration": 45},
            {"name": "필러 1cc", "category_name": "필러", "duration": 60},
            {"name": "필러 2cc", "category_name": "필러", "duration": 90},
            {"name": "울쎄라 300", "category_name": "울쎄라", "duration": 120},
            {"name": "울쎄라 600", "category_name": "울쎄라", "duration": 180},
            {"name": "레이저 토닝", "category_name": "레이저", "duration": 45},
            {"name": "레이저 리프팅", "category_name": "레이저", "duration": 90}
        ]
        
        for treatment_data in treatments:
            existing_treatment = db.query(HospitalTreatment).filter(
                HospitalTreatment.hospital_id == hospital.hospital_id,
                HospitalTreatment.name == treatment_data["name"]
            ).first()
            
            if existing_treatment:
                treatment_map[treatment_data["name"]] = existing_treatment
                print(f"   - 기존 시술 사용: {existing_treatment.name}")
            else:
                category = category_map[treatment_data["category_name"]]
                treatment = HospitalTreatment(
                    hospital_id=hospital.hospital_id,
                    category_id=category.category_id,
                    name=treatment_data["name"],
                    duration_minutes=treatment_data["duration"],
                    description=f"{treatment_data['name']} 시술",
                    is_active=True
                )
                db.add(treatment)
                db.flush()
                treatment_map[treatment_data["name"]] = treatment
                print(f"   - 새 시술 생성: {treatment.name}")
        
        # 4. 기존 의사 확인
        print("👨‍⚕️ 기존 의사 확인 중...")
        existing_doctors = db.query(User).filter(
            User.hospital_id == hospital.hospital_id,
            User.is_doctor == True
        ).all()
        
        if existing_doctors:
            print(f"   - 기존 의사 {len(existing_doctors)}명 발견")
            for doctor in existing_doctors:
                print(f"     * {doctor.name} (ID: {doctor.user_id})")
        
        # 5. 새로운 의사 추가 (기존 의사가 4명 미만인 경우)
        if len(existing_doctors) < 4:
            print("👨‍⚕️ 추가 의사 생성 중...")
            new_doctors = [
                {
                    "name": "김성형",
                    "email": "kim@hospital.com",
                    "role": "doctor",
                    "is_doctor": True,
                    "hashed_password": "hashed_password_123"
                },
                {
                    "name": "이피부",
                    "email": "lee@hospital.com", 
                    "role": "doctor",
                    "is_doctor": True,
                    "hashed_password": "hashed_password_123"
                },
                {
                    "name": "박레이저",
                    "email": "park@hospital.com",
                    "role": "doctor", 
                    "is_doctor": True,
                    "hashed_password": "hashed_password_123"
                },
                {
                    "name": "최필러",
                    "email": "choi@hospital.com",
                    "role": "doctor",
                    "is_doctor": True, 
                    "hashed_password": "hashed_password_123"
                }
            ]
            
            # 기존 의사 이름 확인
            existing_names = [d.name for d in existing_doctors]
            
            for doctor_data in new_doctors:
                if doctor_data["name"] not in existing_names:
                    user = User(
                        hospital_id=hospital.hospital_id,
                        name=doctor_data["name"],
                        role=doctor_data["role"],
                        email=doctor_data["email"],
                        hashed_password=doctor_data["hashed_password"],
                        is_doctor=doctor_data["is_doctor"],
                        is_active=True
                    )
                    db.add(user)
                    print(f"   - 새 의사 생성: {user.name}")
            
            db.flush()
        
        # 6. 모든 의사 조회
        all_doctors = db.query(User).filter(
            User.hospital_id == hospital.hospital_id,
            User.is_doctor == True
        ).all()
        
        print(f"✅ 총 의사 수: {len(all_doctors)}명")
        
        # 7. 의사 프로필 생성/업데이트
        print("👨‍⚕️ 의사 프로필 생성/업데이트 중...")
        
        # 시술 ID 매핑 (실제 DB ID 사용)
        treatment_ids = {
            "보톡스 5u": treatment_map["보톡스 5u"].treatment_id,
            "보톡스 10u": treatment_map["보톡스 10u"].treatment_id,
            "필러 1cc": treatment_map["필러 1cc"].treatment_id,
            "필러 2cc": treatment_map["필러 2cc"].treatment_id,
            "울쎄라 300": treatment_map["울쎄라 300"].treatment_id,
            "울쎄라 600": treatment_map["울쎄라 600"].treatment_id,
            "레이저 토닝": treatment_map["레이저 토닝"].treatment_id,
            "레이저 리프팅": treatment_map["레이저 리프팅"].treatment_id
        }
        
        doctor_profiles = [
            {
                "name": "김성형",
                "total_minutes": 50,  # 적은 업무량 (높은 점수)
                "qualified_treatments": [
                    treatment_ids["보톡스 5u"], treatment_ids["보톡스 10u"],
                    treatment_ids["필러 1cc"], treatment_ids["필러 2cc"]
                ]
            },
            {
                "name": "이피부", 
                "total_minutes": 120,  # 중간 업무량
                "qualified_treatments": [
                    treatment_ids["보톡스 5u"], treatment_ids["보톡스 10u"],
                    treatment_ids["울쎄라 300"], treatment_ids["울쎄라 600"]
                ]
            },
            {
                "name": "박레이저",
                "total_minutes": 200,  # 많은 업무량 (낮은 점수)
                "qualified_treatments": [
                    treatment_ids["울쎄라 300"], treatment_ids["울쎄라 600"],
                    treatment_ids["레이저 토닝"], treatment_ids["레이저 리프팅"]
                ]
            },
            {
                "name": "최필러",
                "total_minutes": 80,  # 적당한 업무량
                "qualified_treatments": [
                    treatment_ids["필러 1cc"], treatment_ids["필러 2cc"],
                    treatment_ids["레이저 토닝"], treatment_ids["레이저 리프팅"]
                ]
            }
        ]
        
        for profile_data in doctor_profiles:
            # 해당 이름의 의사 찾기
            doctor_user = next((d for d in all_doctors if d.name == profile_data["name"]), None)
            
            if doctor_user:
                # 기존 프로필 확인
                existing_profile = db.query(DoctorProfile).filter(
                    DoctorProfile.user_id == doctor_user.user_id
                ).first()
                
                if existing_profile:
                    # 기존 프로필 업데이트
                    existing_profile.total_minutes = profile_data["total_minutes"]
                    existing_profile.qualified_treatment_ids = json.dumps(profile_data["qualified_treatments"])
                    print(f"   - 프로필 업데이트: {existing_profile.name}")
                else:
                    # 새 프로필 생성
                    profile = DoctorProfile(
                        user_id=doctor_user.user_id,
                        hospital_id=hospital.hospital_id,
                        name=profile_data["name"],
                        is_active=True,
                        total_minutes=profile_data["total_minutes"],
                        break_start=None,
                        break_end=None,
                        qualified_treatment_ids=json.dumps(profile_data["qualified_treatments"])
                    )
                    db.add(profile)
                    print(f"   - 새 프로필 생성: {profile.name}")
        
        db.commit()
        print("✅ 의사 프로필 생성/업데이트 완료!")

        # =========================
        # hospital_id=8 테스트 데이터 추가
        # =========================
        print("\n[테스트용 hospital_id=8 데이터 시드]")
        test_hospital = db.query(Hospital).filter(Hospital.hospital_id == 8).first()
        if not test_hospital:
            test_hospital = Hospital(
                hospital_id=8,  # 명시적 id
                name="테스트병원8",
                address="테스트 주소",
                is_active=True
            )
            db.add(test_hospital)
            db.flush()
            print(f"✅ 테스트 병원 생성: {test_hospital.name} (ID: {test_hospital.hospital_id})")
        else:
            print(f"✅ 테스트 병원 존재: {test_hospital.name} (ID: {test_hospital.hospital_id})")

        # 시술 카테고리 준비
        test_categories = [
            {"name": "보톡스", "description": "보톡스 시술"},
            {"name": "필러", "description": "필러 시술"},
            {"name": "레이저", "description": "레이저 시술"},
            {"name": "울쎄라", "description": "울쎄라 시술"}
        ]
        test_category_map = {}
        for cat in test_categories:
            c = db.query(TreatmentCategory).filter(TreatmentCategory.name == cat["name"]).first()
            if not c:
                c = TreatmentCategory(name=cat["name"], description=cat["description"], is_active=True)
                db.add(c)
                db.flush()
            test_category_map[cat["name"]] = c

        # hospital_id=8 시술 10개 이상 추가
        test_treatments = [
            {"name": "테스트 보톡스 1", "category_name": "보톡스", "duration": 20},
            {"name": "테스트 보톡스 2", "category_name": "보톡스", "duration": 25},
            {"name": "테스트 필러 1", "category_name": "필러", "duration": 30},
            {"name": "테스트 필러 2", "category_name": "필러", "duration": 35},
            {"name": "테스트 레이저 1", "category_name": "레이저", "duration": 40},
            {"name": "테스트 레이저 2", "category_name": "레이저", "duration": 45},
            {"name": "테스트 울쎄라 1", "category_name": "울쎄라", "duration": 50},
            {"name": "테스트 울쎄라 2", "category_name": "울쎄라", "duration": 55},
            {"name": "테스트 스페셜 1", "category_name": "보톡스", "duration": 60},
            {"name": "테스트 스페셜 2", "category_name": "필러", "duration": 65},
        ]
        test_treatment_map = {}
        for t in test_treatments:
            existing = db.query(HospitalTreatment).filter(
                HospitalTreatment.hospital_id == test_hospital.hospital_id,
                HospitalTreatment.name == t["name"]
            ).first()
            if not existing:
                cat = test_category_map[t["category_name"]]
                new_t = HospitalTreatment(
                    hospital_id=test_hospital.hospital_id,
                    category_id=cat.category_id,
                    name=t["name"],
                    duration_minutes=t["duration"],
                    description=f"{t['name']} 시술",
                    is_active=True
                )
                db.add(new_t)
                db.flush()
                test_treatment_map[t["name"]] = new_t
                print(f"   - 시술 생성: {new_t.name}")
            else:
                test_treatment_map[t["name"]] = existing
                print(f"   - 시술 존재: {existing.name}")

        # 그룹 시술 3개 추가 (각 그룹에 3~4개 시술 포함)
        test_groups = [
            {
                "group_name": "테스트 패키지 1",
                "description": "보톡스+필러 패키지",
                "items": [
                    ("테스트 보톡스 1", 1),
                    ("테스트 필러 1", 2),
                    ("테스트 스페셜 1", 1)
                ]
            },
            {
                "group_name": "테스트 패키지 2",
                "description": "레이저+울쎄라 패키지",
                "items": [
                    ("테스트 레이저 1", 1),
                    ("테스트 울쎄라 1", 1),
                    ("테스트 울쎄라 2", 1)
                ]
            },
            {
                "group_name": "테스트 스페셜 패키지",
                "description": "스페셜 시술 모음",
                "items": [
                    ("테스트 스페셜 1", 1),
                    ("테스트 스페셜 2", 1),
                    ("테스트 보톡스 2", 1),
                    ("테스트 필러 2", 1)
                ]
            }
        ]
        for group in test_groups:
            existing_group = db.query(TreatmentGroup).filter(
                TreatmentGroup.hospital_id == test_hospital.hospital_id,
                TreatmentGroup.group_name == group["group_name"]
            ).first()
            if not existing_group:
                new_group = TreatmentGroup(
                    hospital_id=test_hospital.hospital_id,
                    group_name=group["group_name"],
                    description=group["description"],
                    is_active=True
                )
                db.add(new_group)
                db.flush()
                print(f"   - 그룹 시술 생성: {new_group.group_name}")
            else:
                new_group = existing_group
                print(f"   - 그룹 시술 존재: {new_group.group_name}")
            # 그룹 아이템 추가
            for t_name, count in group["items"]:
                t_obj = test_treatment_map[t_name]
                existing_item = db.query(TreatmentGroupItem).filter(
                    TreatmentGroupItem.group_id == new_group.group_id,
                    TreatmentGroupItem.treatment_id == t_obj.treatment_id
                ).first()
                if not existing_item:
                    item = TreatmentGroupItem(
                        group_id=new_group.group_id,
                        treatment_id=t_obj.treatment_id,
                        count=count
                    )
                    db.add(item)
                    print(f"      * 그룹 구성 추가: {t_name} x{count}")
                else:
                    print(f"      * 그룹 구성 존재: {t_name} x{existing_item.count}")
        db.commit()
        print("✅ hospital_id=8 테스트용 시술/그룹시술 시드 완료!")
        
        # =========================
        # hospital_id=8 의사들에게 테스트 시술 자격 추가
        # =========================
        print("\n[hospital_id=8 의사 테스트 시술 자격 추가]")
        
        # 테스트 시술 ID 매핑
        test_treatment_ids = {
            "테스트 보톡스 1": test_treatment_map["테스트 보톡스 1"].treatment_id,
            "테스트 보톡스 2": test_treatment_map["테스트 보톡스 2"].treatment_id,
            "테스트 필러 1": test_treatment_map["테스트 필러 1"].treatment_id,
            "테스트 필러 2": test_treatment_map["테스트 필러 2"].treatment_id,
            "테스트 레이저 1": test_treatment_map["테스트 레이저 1"].treatment_id,
            "테스트 레이저 2": test_treatment_map["테스트 레이저 2"].treatment_id,
            "테스트 울쎄라 1": test_treatment_map["테스트 울쎄라 1"].treatment_id,
            "테스트 울쎄라 2": test_treatment_map["테스트 울쎄라 2"].treatment_id,
            "테스트 스페셜 1": test_treatment_map["테스트 스페셜 1"].treatment_id,
            "테스트 스페셜 2": test_treatment_map["테스트 스페셜 2"].treatment_id,
        }
        
        # 의사별 테스트 시술 자격 추가
        doctor_test_qualifications = [
            {
                "name": "김성형",
                "additional_treatments": [
                    test_treatment_ids["테스트 보톡스 1"], test_treatment_ids["테스트 보톡스 2"],
                    test_treatment_ids["테스트 필러 1"], test_treatment_ids["테스트 필러 2"],
                    test_treatment_ids["테스트 스페셜 1"], test_treatment_ids["테스트 스페셜 2"]
                ]
            },
            {
                "name": "이피부",
                "additional_treatments": [
                    test_treatment_ids["테스트 보톡스 1"], test_treatment_ids["테스트 보톡스 2"],
                    test_treatment_ids["테스트 울쎄라 1"], test_treatment_ids["테스트 울쎄라 2"],
                    test_treatment_ids["테스트 스페셜 1"]
                ]
            },
            {
                "name": "박레이저",
                "additional_treatments": [
                    test_treatment_ids["테스트 레이저 1"], test_treatment_ids["테스트 레이저 2"],
                    test_treatment_ids["테스트 울쎄라 1"], test_treatment_ids["테스트 울쎄라 2"],
                    test_treatment_ids["테스트 스페셜 2"]
                ]
            },
            {
                "name": "최필러",
                "additional_treatments": [
                    test_treatment_ids["테스트 필러 1"], test_treatment_ids["테스트 필러 2"],
                    test_treatment_ids["테스트 레이저 1"], test_treatment_ids["테스트 레이저 2"],
                    test_treatment_ids["테스트 스페셜 1"], test_treatment_ids["테스트 스페셜 2"]
                ]
            }
        ]
        
        # 의사 프로필 업데이트
        for qualification in doctor_test_qualifications:
            doctor_user = next((d for d in all_doctors if d.name == qualification["name"]), None)
            
            if doctor_user:
                existing_profile = db.query(DoctorProfile).filter(
                    DoctorProfile.user_id == doctor_user.user_id
                ).first()
                
                if existing_profile:
                    # 기존 자격에 테스트 시술 추가
                    current_qualifications = json.loads(existing_profile.qualified_treatment_ids or "[]")
                    new_qualifications = current_qualifications + qualification["additional_treatments"]
                    
                    existing_profile.qualified_treatment_ids = json.dumps(new_qualifications)
                    print(f"   - {existing_profile.name} 자격 추가: {len(qualification['additional_treatments'])}개 테스트 시술")
                else:
                    print(f"   - {qualification['name']} 프로필이 없습니다")
        
        db.commit()
        print("✅ hospital_id=8 의사 테스트 시술 자격 추가 완료!")
        
        # =========================
        # 페이스필터 병원 추가 (hospital_id=9)
        # =========================
        print("\n[페이스필터 병원 데이터 시드]")
        
        # 페이스필터 병원 생성
        facefilter_hospital = db.query(Hospital).filter(Hospital.name == "페이스필터").first()
        if not facefilter_hospital:
            facefilter_hospital = Hospital(
                name="페이스필터",
                address="서울시 강남구 테헤란로 123",
                is_active=True
            )
            db.add(facefilter_hospital)
            db.flush()
            print(f"✅ 페이스필터 병원 생성: ID {facefilter_hospital.hospital_id}")
        else:
            print(f"✅ 페이스필터 병원 존재: ID {facefilter_hospital.hospital_id}")
        
        # 페이스필터 의사 4명 생성
        facefilter_doctors = [
            {"name": "권오성", "email": "kwon@facefilter.com", "role": "doctor", "total_minutes": 120},
            {"name": "황기현", "email": "hwang@facefilter.com", "role": "doctor", "total_minutes": 90},
            {"name": "최원하", "email": "choi@facefilter.com", "role": "doctor", "total_minutes": 150},
            {"name": "정진욱", "email": "jung@facefilter.com", "role": "doctor", "total_minutes": 80}
        ]
        
        facefilter_doctor_users = []
        for doctor_data in facefilter_doctors:
            existing_user = db.query(User).filter(User.email == doctor_data["email"]).first()
            if not existing_user:
                new_doctor = User(
                    hospital_id=facefilter_hospital.hospital_id,
                    name=doctor_data["name"],
                    role=doctor_data["role"],
                    email=doctor_data["email"],
                    hashed_password="hashed_password_123",  # 실제로는 해시된 비밀번호
                    is_doctor=True,
                    is_active=True
                )
                db.add(new_doctor)
                db.flush()
                facefilter_doctor_users.append(new_doctor)
                print(f"   - 의사 생성: {new_doctor.name}")
            else:
                facefilter_doctor_users.append(existing_user)
                print(f"   - 의사 존재: {existing_user.name}")
        
        # 페이스필터 의사 프로필 생성
        for i, doctor_user in enumerate(facefilter_doctor_users):
            existing_profile = db.query(DoctorProfile).filter(
                DoctorProfile.user_id == doctor_user.user_id
            ).first()
            
            if not existing_profile:
                profile = DoctorProfile(
                    user_id=doctor_user.user_id,
                    hospital_id=facefilter_hospital.hospital_id,
                    name=doctor_user.name,
                    is_active=True,
                    total_minutes=facefilter_doctors[i]["total_minutes"],
                    qualified_treatment_ids="[]"  # 나중에 시술 자격 추가
                )
                db.add(profile)
                print(f"   - 의사 프로필 생성: {profile.name}")
            else:
                print(f"   - 의사 프로필 존재: {existing_profile.name}")
        
        db.commit()
        
        # =========================
        # 페이스필터 시술 10개 추가
        # =========================
        print("\n[페이스필터 시술 추가]")
        
        facefilter_treatments = [
            {"name": "페이스필터 보톡스 A", "category_name": "보톡스", "duration": 25},
            {"name": "페이스필터 보톡스 B", "category_name": "보톡스", "duration": 30},
            {"name": "페이스필터 필러 X", "category_name": "필러", "duration": 35},
            {"name": "페이스필터 필러 Y", "category_name": "필러", "duration": 40},
            {"name": "페이스필터 레이저 1", "category_name": "레이저", "duration": 45},
            {"name": "페이스필터 레이저 2", "category_name": "레이저", "duration": 50},
            {"name": "페이스필터 울쎄라 P", "category_name": "울쎄라", "duration": 55},
            {"name": "페이스필터 울쎄라 Q", "category_name": "울쎄라", "duration": 60},
            {"name": "페이스필터 스페셜 1", "category_name": "보톡스", "duration": 65},
            {"name": "페이스필터 스페셜 2", "category_name": "필러", "duration": 70},
        ]
        
        facefilter_treatment_map = {}
        for t in facefilter_treatments:
            existing = db.query(HospitalTreatment).filter(
                HospitalTreatment.hospital_id == facefilter_hospital.hospital_id,
                HospitalTreatment.name == t["name"]
            ).first()
            if not existing:
                cat = category_map[t["category_name"]]
                new_t = HospitalTreatment(
                    hospital_id=facefilter_hospital.hospital_id,
                    category_id=cat.category_id,
                    name=t["name"],
                    duration_minutes=t["duration"],
                    description=f"{t['name']} 시술",
                    is_active=True
                )
                db.add(new_t)
                db.flush()
                facefilter_treatment_map[t["name"]] = new_t
                print(f"   - 시술 생성: {new_t.name}")
            else:
                facefilter_treatment_map[t["name"]] = existing
                print(f"   - 시술 존재: {existing.name}")
        
        # 페이스필터 그룹 시술 4개 추가
        facefilter_groups = [
            {
                "group_name": "페이스필터 패키지 1",
                "description": "보톡스+필러 기본 패키지",
                "items": [
                    ("페이스필터 보톡스 A", 1),
                    ("페이스필터 필러 X", 1),
                    ("페이스필터 스페셜 1", 1)
                ]
            },
            {
                "group_name": "페이스필터 패키지 2",
                "description": "레이저+울쎄라 프리미엄 패키지",
                "items": [
                    ("페이스필터 레이저 1", 1),
                    ("페이스필터 울쎄라 P", 1),
                    ("페이스필터 스페셜 2", 1)
                ]
            },
            {
                "group_name": "페이스필터 VIP 패키지",
                "description": "VIP 전용 프리미엄 패키지",
                "items": [
                    ("페이스필터 보톡스 B", 1),
                    ("페이스필터 필러 Y", 1),
                    ("페이스필터 레이저 2", 1),
                    ("페이스필터 울쎄라 Q", 1)
                ]
            },
            {
                "group_name": "페이스필터 스페셜 패키지",
                "description": "스페셜 시술 모음",
                "items": [
                    ("페이스필터 스페셜 1", 1),
                    ("페이스필터 스페셜 2", 1),
                    ("페이스필터 보톡스 A", 1),
                    ("페이스필터 필러 X", 1)
                ]
            }
        ]
        
        for group in facefilter_groups:
            existing_group = db.query(TreatmentGroup).filter(
                TreatmentGroup.hospital_id == facefilter_hospital.hospital_id,
                TreatmentGroup.group_name == group["group_name"]
            ).first()
            if not existing_group:
                new_group = TreatmentGroup(
                    hospital_id=facefilter_hospital.hospital_id,
                    group_name=group["group_name"],
                    description=group["description"],
                    is_active=True
                )
                db.add(new_group)
                db.flush()
                print(f"   - 그룹 시술 생성: {new_group.group_name}")
            else:
                new_group = existing_group
                print(f"   - 그룹 시술 존재: {new_group.group_name}")
            
            # 그룹 아이템 추가
            for t_name, count in group["items"]:
                t_obj = facefilter_treatment_map[t_name]
                existing_item = db.query(TreatmentGroupItem).filter(
                    TreatmentGroupItem.group_id == new_group.group_id,
                    TreatmentGroupItem.treatment_id == t_obj.treatment_id
                ).first()
                if not existing_item:
                    item = TreatmentGroupItem(
                        group_id=new_group.group_id,
                        treatment_id=t_obj.treatment_id,
                        count=count
                    )
                    db.add(item)
                    print(f"      * 그룹 구성 추가: {t_name} x{count}")
                else:
                    print(f"      * 그룹 구성 존재: {t_name} x{existing_item.count}")
        
        db.commit()
        print("✅ 페이스필터 시술/그룹시술 시드 완료!")
        
        # =========================
        # 페이스필터 의사들에게 시술 자격 추가
        # =========================
        print("\n[페이스필터 의사 시술 자격 추가]")
        
        # 페이스필터 시술 ID 매핑
        facefilter_treatment_ids = {
            "페이스필터 보톡스 A": facefilter_treatment_map["페이스필터 보톡스 A"].treatment_id,
            "페이스필터 보톡스 B": facefilter_treatment_map["페이스필터 보톡스 B"].treatment_id,
            "페이스필터 필러 X": facefilter_treatment_map["페이스필터 필러 X"].treatment_id,
            "페이스필터 필러 Y": facefilter_treatment_map["페이스필터 필러 Y"].treatment_id,
            "페이스필터 레이저 1": facefilter_treatment_map["페이스필터 레이저 1"].treatment_id,
            "페이스필터 레이저 2": facefilter_treatment_map["페이스필터 레이저 2"].treatment_id,
            "페이스필터 울쎄라 P": facefilter_treatment_map["페이스필터 울쎄라 P"].treatment_id,
            "페이스필터 울쎄라 Q": facefilter_treatment_map["페이스필터 울쎄라 Q"].treatment_id,
            "페이스필터 스페셜 1": facefilter_treatment_map["페이스필터 스페셜 1"].treatment_id,
            "페이스필터 스페셜 2": facefilter_treatment_map["페이스필터 스페셜 2"].treatment_id,
        }
        
        # 모든 시술 ID 리스트 (권오성 제외하고 모두 동일)
        all_facefilter_treatments = list(facefilter_treatment_ids.values())
        
        # 의사별 시술 자격 추가 (권오성은 제외, 나머지는 모두 동일)
        facefilter_doctor_qualifications = [
            {
                "name": "권오성",
                "treatments": [
                    facefilter_treatment_ids["페이스필터 보톡스 A"],
                    facefilter_treatment_ids["페이스필터 필러 X"],
                    facefilter_treatment_ids["페이스필터 레이저 1"]
                ]
            },
            {
                "name": "황기현",
                "treatments": all_facefilter_treatments
            },
            {
                "name": "최원하", 
                "treatments": all_facefilter_treatments
            },
            {
                "name": "정진욱",
                "treatments": all_facefilter_treatments
            }
        ]
        
        # 의사 프로필 업데이트
        for qualification in facefilter_doctor_qualifications:
            doctor_user = next((d for d in facefilter_doctor_users if d.name == qualification["name"]), None)
            
            if doctor_user:
                existing_profile = db.query(DoctorProfile).filter(
                    DoctorProfile.user_id == doctor_user.user_id
                ).first()
                
                if existing_profile:
                    existing_profile.qualified_treatment_ids = json.dumps(qualification["treatments"])
                    print(f"   - {existing_profile.name} 자격 설정: {len(qualification['treatments'])}개 시술")
                else:
                    print(f"   - {qualification['name']} 프로필이 없습니다")
        
        db.commit()
        print("✅ 페이스필터 의사 시술 자격 추가 완료!")
        
        print("\n🎉 시드 데이터 생성 완료!")
        print("\n📊 생성된 데이터 요약:")
        print(f"   - 병원: {hospital.name}, {facefilter_hospital.name}")
        print(f"   - 의사: {len(all_doctors)}명 + {len(facefilter_doctor_users)}명")
        print(f"   - 시술 카테고리: {len(category_map)}개")
        print(f"   - 병원별 시술: {len(treatment_map)}개 + {len(facefilter_treatment_map)}개")
        
        print("\n👨‍⚕️ 의사별 특성:")
        for profile_data in doctor_profiles:
            print(f"   - {profile_data['name']}: {profile_data['total_minutes']}분 업무량")
        for i, doctor_data in enumerate(facefilter_doctors):
            print(f"   - {doctor_data['name']}: {doctor_data['total_minutes']}분 업무량")
        
        print("\n🧪 테스트 시나리오:")
        print("   - 보톡스 5u: 김성형, 이피부 가능")
        print("   - 울쎄라 300: 이피부, 박레이저 가능") 
        print("   - 필러 1cc: 김성형, 최필러 가능")
        print("   - 레이저 토닝: 박레이저, 최필러 가능")
        print("\n   - 페이스필터 보톡스 A: 권오성, 황기현, 최원하, 정진욱 가능")
        print("   - 페이스필터 패키지 1: 황기현, 최원하, 정진욱 가능")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 시드 데이터 생성 실패: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data() 