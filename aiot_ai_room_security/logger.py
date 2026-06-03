"""침입 이벤트를 CSV 로그로 저장한다."""

import csv
from datetime import datetime

import config


CSV_HEADER = ["timestamp", "event_type", "message", "confidence", "image_path"]


def write_event(event_type, message, confidence, image_path):
    """logs/event_log.csv에 이벤트 한 줄을 추가한다."""
    log_path = config.LOG_FILE_PATH
    log_path.parent.mkdir(parents=True, exist_ok=True)

    needs_header = not log_path.exists() or log_path.stat().st_size == 0
    with log_path.open("a", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file)
        if needs_header:
            writer.writerow(CSV_HEADER)

        timestamp = datetime.now().isoformat(timespec="seconds")
        writer.writerow([
            timestamp,
            event_type,
            message,
            f"{confidence:.4f}",
            image_path,
        ])

    print(f"[로그 저장] {log_path}")
