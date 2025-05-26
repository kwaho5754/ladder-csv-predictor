import csv
import os
import requests
import time

CSV_PATH = "ladder_results.csv"
CHECK_INTERVAL = 60  # 초 단위: 60초 = 1분

def get_existing_rounds():
    rounds = set()
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # 헤더 건너뜀
            for row in reader:
                if len(row) > 1 and row[1].isdigit():
                    rounds.add(row[1])
    return rounds

def fetch_latest_round():
    try:
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        latest = response.json()[0]
        return {
            "reg_date": latest["reg_date"],
            "date_round": str(latest["date_round"]),
            "start_point": latest["start_point"],
            "line_count": latest["line_count"],
            "odd_even": latest["odd_even"]
        }
    except Exception as e:
        print("❌ 데이터 불러오기 실패:", e)
        return None

def append_if_new(latest_data):
    if not latest_data:
        return

    existing = get_existing_rounds()
    if latest_data["date_round"] in existing:
        print(f"⏳ 이미 존재하는 회차: {latest_data['date_round']}")
        return

    row = [
        latest_data["reg_date"],
        latest_data["date_round"],
        latest_data["start_point"],
        latest_data["line_count"],
        latest_data["odd_even"]
    ]

    # 새로 저장
    file_exists = os.path.exists(CSV_PATH)
    with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["날짜", "회차", "좌우", "줄수", "홀짝"])
        writer.writerow(row)
    print(f"✅ 새 회차 저장 완료: {latest_data['date_round']}회차")

def run_loop():
    print("🔁 실시간 회차 감지 시작 (1분마다 확인)")
    while True:
        latest = fetch_latest_round()
        append_if_new(latest)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_loop()
