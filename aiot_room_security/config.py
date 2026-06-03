"""AI 기반 개인 방 침입 감지 시스템의 설정값을 한곳에서 관리한다."""

import os
from pathlib import Path


def _env_bool(name, default):
    """환경변수의 1/true/yes/on 값을 True로 해석한다."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name, default):
    """환경변수가 없으면 기본 정수값을 사용한다."""
    return int(os.getenv(name, str(default)))


def _env_float(name, default):
    """환경변수가 없으면 기본 실수값을 사용한다."""
    return float(os.getenv(name, str(default)))


def _env_path(name, default):
    """상대 경로를 프로젝트 폴더 기준의 절대 경로로 변환한다."""
    raw_path = os.getenv(name)
    path = Path(raw_path).expanduser() if raw_path else Path(default)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


# 이 파일이 들어 있는 aiot_room_security 폴더를 기준 경로로 사용한다.
BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# GPIO 핀 설정
# 수업 자료와 동일하게 BCM GPIO 번호를 사용한다.
# ---------------------------------------------------------------------------
PIR_SENSOR_PIN = 16
RED_LED_PIN = 21

# 3핀 능동부저 모듈을 쓰는 경우 S 또는 Signal 핀을 GPIO 18에 연결한다.
# + 또는 VCC 핀은 3.3V, - 또는 GND 핀은 GND에 연결한다.
ACTIVE_BUZZER_PIN = 18

# ---------------------------------------------------------------------------
# OpenCV DNN MobileNet SSD 설정
# Section 16 수업 자료에서 사용한 모델 파일명을 기본값으로 지정한다.
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

# 수업 자료의 cv2.VideoCapture(-1) 설정을 기본값으로 사용한다.
# 카메라가 열리지 않으면 실행 전에 AIOT_CAMERA_INDEX=0도 시험해 본다.
CAMERA_INDEX = _env_int("AIOT_CAMERA_INDEX", -1)
CAMERA_WIDTH = _env_int("AIOT_CAMERA_WIDTH", 640)
CAMERA_HEIGHT = _env_int("AIOT_CAMERA_HEIGHT", 480)

# 탐지된 사람의 박스가 표시된 이미지를 captures 폴더에 저장한다.
SAVE_CAPTURE_IMAGES = _env_bool("AIOT_SAVE_CAPTURE_IMAGES", True)
SHOW_DETECTION_WINDOW = _env_bool("AIOT_SHOW_DETECTION_WINDOW", False)
CAPTURE_DIR = _env_path("AIOT_CAPTURE_DIR", BASE_DIR / "captures")

# ---------------------------------------------------------------------------
# 텔레그램 설정
# 직접 문자열을 입력해도 되고, 실행 전에 환경변수로 전달해도 된다.
# GitHub에 올릴 코드에는 실제 토큰을 저장하지 않는 것이 안전하다.
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
TELEGRAM_REQUEST_TIMEOUT_SECONDS = _env_float("AIOT_TELEGRAM_TIMEOUT", 5.0)

# ---------------------------------------------------------------------------
# 반복 확인, 경고 출력, 중복 알림 방지 설정
# ---------------------------------------------------------------------------
PIR_POLL_INTERVAL_SECONDS = _env_float("AIOT_PIR_POLL_INTERVAL", 0.5)
ALERT_COOLDOWN_SECONDS = _env_float("AIOT_ALERT_COOLDOWN", 30.0)
WARNING_DURATION_SECONDS = _env_float("AIOT_WARNING_DURATION", 3.0)
WARNING_BLINK_INTERVAL_SECONDS = _env_float("AIOT_WARNING_BLINK_INTERVAL", 0.25)
LOG_FILE_PATH = _env_path("AIOT_LOG_FILE_PATH", BASE_DIR / "logs" / "event_log.csv")

# ---------------------------------------------------------------------------
# 라즈베리파이 없이 프로그램 흐름을 확인하기 위한 MOCK 설정
# 실제 라즈베리파이에서는 MOCK_MODE를 False로 바꾸거나
# 실행 전에 export AIOT_MOCK_MODE=0 명령을 입력한다.
# ---------------------------------------------------------------------------
MOCK_MODE = _env_bool("AIOT_MOCK_MODE", True)
MOCK_PIR_MOTION = _env_bool("AIOT_MOCK_PIR_MOTION", False)
MOCK_PERSON_DETECTED = _env_bool("AIOT_MOCK_PERSON_DETECTED", True)
MOCK_PERSON_CONFIDENCE = _env_float("AIOT_MOCK_PERSON_CONFIDENCE", 0.95)

# 0이면 무한 반복한다. 자동 검증에서는 1 이상의 값을 사용한다.
MAX_LOOP_COUNT = _env_int("AIOT_MAX_LOOP_COUNT", 0)
