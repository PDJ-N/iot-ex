"""침입 이벤트를 CSV 파일에 기록한다."""

import csv
from datetime import datetime

import config


CSV_HEADER = ["timestamp", "event_type", "message", "confidence"]


def write_event(event_type, message, confidence):
    """logs/event_log.csv가 없으면 헤더를 만들고 이벤트 한 줄을 추가한다."""
    log_path = config.LOG_FILE_PATH
    log_path.parent.mkdir(parents=True, exist_ok=True)

    needs_header = not log_path.exists() or log_path.stat().st_size == 0
    with log_path.open("a", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file)
        if needs_header:
            writer.writerow(CSV_HEADER)

        timestamp = datetime.now().isoformat(timespec="seconds")
        writer.writerow([timestamp, event_type, message, f"{confidence:.4f}"])

    print(f"[로그 저장] {log_path}")
