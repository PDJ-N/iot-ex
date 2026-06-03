"""AI 방 침입 감지 시스템의 설정값을 한곳에서 관리한다."""

import os
from pathlib import Path


def _env_bool(name, default):
    """환경변수를 True/False 값으로 읽는다."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name, default):
    """환경변수를 정수로 읽고, 없으면 기본값을 사용한다."""
    return int(os.getenv(name, str(default)))


def _env_float(name, default):
    """환경변수를 실수로 읽고, 없으면 기본값을 사용한다."""
    return float(os.getenv(name, str(default)))


def _env_path(name, default):
    """상대 경로를 프로젝트 폴더 기준 절대 경로로 바꾼다."""
    raw_path = os.getenv(name)
    path = Path(raw_path).expanduser() if raw_path else Path(default)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


# 이 파일이 있는 폴더를 프로젝트 기준 경로로 사용한다.
BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# GPIO 핀 설정
# gpiozero는 BCM GPIO 번호를 사용한다.
# ---------------------------------------------------------------------------
PIR_SENSOR_PIN = 16

# 2핀 능동부저: + 핀을 GPIO18, - 핀을 GND에 연결한다.
# 3핀 능동부저 모듈: S 핀을 GPIO18, + 핀을 3.3V, - 핀을 GND에 연결한다.
# 사용자가 보유한 S/- 표시 3핀 모듈은 두 번째 방식으로 연결한다.
BUZZER_PIN = 18

# ---------------------------------------------------------------------------
# OpenCV DNN MobileNet SSD 모델 설정
# Section 16 수업 자료의 모델 파일명을 기본값으로 사용한다.
# ---------------------------------------------------------------------------
MODEL_WEIGHTS_PATH = _env_path(
    "AIOT_MODEL_WEIGHTS_PATH",
    BASE_DIR / "models" / "frozen_inference_graph.pb",
)
MODEL_CONFIG_PATH = _env_path(
    "AIOT_MODEL_CONFIG_PATH",
    BASE_DIR / "models" / "ssd_mobilenet_v2_coco_2018_03_29.pbtxt",
)
PERSON_CLASS_ID = 1
PERSON_CONFIDENCE_THRESHOLD = _env_float("AIOT_PERSON_CONFIDENCE", 0.50)

# USB 웹캠 설정이다. Raspberry Pi에서 보통 0번으로 열리지만 환경에 따라 -1이 맞을 수 있다.
CAMERA_INDEX = _env_int("AIOT_CAMERA_INDEX", 0)
CAMERA_WIDTH = _env_int("AIOT_CAMERA_WIDTH", 640)
CAMERA_HEIGHT = _env_int("AIOT_CAMERA_HEIGHT", 480)

# ---------------------------------------------------------------------------
# 저장 경로 설정
# ---------------------------------------------------------------------------
CAPTURE_DIR = _env_path("AIOT_CAPTURE_DIR", BASE_DIR / "captures")
LOG_FILE_PATH = _env_path("AIOT_LOG_FILE_PATH", BASE_DIR / "logs" / "event_log.csv")

# ---------------------------------------------------------------------------
# 텔레그램 설정
# 실제 token/chat_id는 GitHub에 올리지 말고 환경변수로 넣는 것을 권장한다.
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
TELEGRAM_REQUEST_TIMEOUT_SECONDS = _env_float("AIOT_TELEGRAM_TIMEOUT", 8.0)

# ---------------------------------------------------------------------------
# 경고음, 반복 확인, 중복 알림 방지 설정
# ---------------------------------------------------------------------------
PIR_POLL_INTERVAL_SECONDS = _env_float("AIOT_PIR_POLL_INTERVAL", 0.5)
BUZZER_BEEP_SECONDS = _env_float("AIOT_BUZZER_BEEP_SECONDS", 2.0)
ALERT_COOLDOWN_SECONDS = _env_float("AIOT_ALERT_COOLDOWN", 10.0)

# ---------------------------------------------------------------------------
# 하드웨어 없이 테스트하기 위한 MOCK 설정
# ---------------------------------------------------------------------------
MOCK_MODE = _env_bool("AIOT_MOCK_MODE", True)

# MOCK_CONSOLE_INPUT=True이면 터미널에서 y/n을 입력해 PIR 감지를 흉내 낼 수 있다.
MOCK_CONSOLE_INPUT = _env_bool("AIOT_MOCK_CONSOLE_INPUT", False)
MOCK_MOTION = _env_bool("AIOT_MOCK_MOTION", False)
MOCK_PERSON_DETECTED = _env_bool("AIOT_MOCK_PERSON_DETECTED", True)
MOCK_PERSON_CONFIDENCE = _env_float("AIOT_MOCK_PERSON_CONFIDENCE", 0.95)

# 자동 테스트용이다. 0이면 무한 반복한다.
MAX_LOOP_COUNT = _env_int("AIOT_MAX_LOOP_COUNT", 0)
