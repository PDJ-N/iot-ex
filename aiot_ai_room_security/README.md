# PIR 센서와 OpenCV AI를 활용한 방 침입 감지 및 텔레그램 알림 시스템

## 1. 프로젝트 개요

이 프로젝트는 Raspberry Pi, PIR 인체감지 센서, USB 웹캠, 능동 부저, 텔레그램 봇 API를 이용한 AIoT 방 침입 감지 시스템이다.

회로를 단순화하기 위해 LED는 사용하지 않는다. PIR 센서가 움직임을 감지하면 USB 웹캠으로 현재 프레임을 가져오고, OpenCV DNN MobileNet SSD 모델로 사람이 있는지 확인한다. 사람이 감지되면 부저를 울리고, 사진을 저장하고, 텔레그램 메시지와 사진을 전송하며, CSV 로그를 남긴다.

## 2. 사용한 수업 내용

| 수업 내용 | 프로젝트 반영 |
| --- | --- |
| PIR 인체감지 센서 | 움직임 감지 트리거 |
| USB 웹캠 영상 입력 | 침입 순간 프레임 캡처 |
| OpenCV DNN MobileNet SSD | `person` 객체 AI 탐지 |
| gpiozero GPIO 제어 | PIR 입력과 부저 출력 제어 |
| 능동 부저 | 침입 감지 시 경고음 출력 |
| 텔레그램 봇 API | 실시간 원격 알림 |
| CSV 로그 파일 | 감지 시간, 이벤트, confidence, 이미지 경로 기록 |

## 3. 프로젝트 폴더 구조

```text
aiot_ai_room_security/
├── main.py
├── config.py
├── sensor.py
├── buzzer.py
├── vision_ai.py
├── telegram_notifier.py
├── logger.py
├── requirements.txt
├── README.md
├── captures/
└── logs/
    └── event_log.csv
```

## 4. 하드웨어 구성

| 부품 | 역할 |
| --- | --- |
| Raspberry Pi 5 | 전체 프로그램 실행 |
| PIR 인체감지 센서 | 방 안의 움직임 감지 |
| USB 웹캠 | AI 객체검출용 영상 입력 |
| 능동 부저 | 침입 감지 시 경고음 출력 |
| 브레드보드 | 센서와 부저 연결 |
| 점퍼 케이블 | GPIO 배선 |

LED는 사용하지 않는다.

## 5. 회로 연결표

### 5.1 2핀 능동 부저를 사용하는 경우

수정본 요구사항의 기본 연결은 2핀 부저 기준이다.

| 장치 | 핀 | Raspberry Pi 연결 |
| --- | --- | --- |
| PIR 센서 | `S` 또는 `Signal` | `GPIO 16`, 물리 36번 핀 |
| PIR 센서 | `V` 또는 `VCC` | `3.3V`, 물리 1번 핀 |
| PIR 센서 | `G` 또는 `GND` | `GND` |
| 2핀 능동 부저 | `+` | `GPIO 18`, 물리 12번 핀 |
| 2핀 능동 부저 | `-` | `GND` |
| USB 웹캠 | USB | Raspberry Pi USB 포트 |

### 5.2 사용자가 가진 3핀 능동 부저 모듈을 사용하는 경우

사용자의 부저처럼 `S`, `+`, `-`가 있는 3핀 부저 모듈은 아래처럼 연결한다. 이 경우 `+`를 GPIO18에 연결하지 않는다.

| 장치 | 핀 | Raspberry Pi 연결 |
| --- | --- | --- |
| PIR 센서 | `S` 또는 `Signal` | `GPIO 16`, 물리 36번 핀 |
| PIR 센서 | `V` 또는 `VCC` | `3.3V`, 물리 1번 핀 |
| PIR 센서 | `G` 또는 `GND` | `GND` |
| 3핀 능동 부저 모듈 | `S` 또는 `Signal` | `GPIO 18`, 물리 12번 핀 |
| 3핀 능동 부저 모듈 | `+` 또는 `VCC` | `3.3V`, 물리 1번 핀 |
| 3핀 능동 부저 모듈 | `-` 또는 `GND` | `GND` |
| USB 웹캠 | USB | Raspberry Pi USB 포트 |

모든 GND는 공통 GND로 연결한다.

## 6. 아주 쉬운 회로 연결 설명

브레드보드로 3.3V와 GND를 나눠 쓰는 그림은 `wiring_breadboard_guide.html`을 열어 확인한다.

1. 라즈베리파이 전원을 끈다.
2. PIR 센서의 `S`를 라즈베리파이 `GPIO 16`에 연결한다.
3. PIR 센서의 `V`를 라즈베리파이 `3.3V`에 연결한다.
4. PIR 센서의 `G`를 라즈베리파이 `GND`에 연결한다.
5. 2핀 부저라면 부저 `+`를 `GPIO 18`, 부저 `-`를 `GND`에 연결한다.
6. 3핀 부저 모듈이라면 부저 `S`를 `GPIO 18`, `+`를 `3.3V`, `-`를 `GND`에 연결한다.
7. USB 웹캠을 라즈베리파이 USB 포트에 연결한다.
8. 배선을 다시 확인한 뒤 전원을 켠다.

주의: LED는 연결하지 않는다.

## 7. 동작 흐름

1. 프로그램 시작 시 `"AI 침입 감지 시스템 대기 중..."` 메시지를 출력한다.
2. PIR 센서 값을 반복 확인한다.
3. PIR 값이 `1`이면 움직임 감지로 판단한다.
4. USB 웹캠에서 프레임을 읽는다.
5. MobileNet SSD 모델로 `person` 객체를 탐지한다.
6. confidence가 기준값 이상이면 침입 이벤트로 판단한다.
7. 현재 프레임을 `captures/` 폴더에 저장한다.
8. 부저를 일정 시간 울린다.
9. 텔레그램 메시지를 전송한다.
10. 저장된 사진이 있으면 텔레그램 사진도 전송한다.
11. `logs/event_log.csv`에 이벤트를 기록한다.
12. cooldown 시간 안에는 중복 알림을 보내지 않는다.
13. `Ctrl+C` 입력 시 부저를 끄고 안전하게 종료한다.

## 8. 설치 방법

회로 연결이 끝난 뒤 실행 순서만 빠르게 보고 싶으면 `after_wiring_run_guide.html`을 열어 확인한다.

라즈베리파이 터미널에서 실행한다.

```bash
cd ~
git clone https://github.com/PDJ-N/iot-ex.git
cd iot-ex/aiot_ai_room_security

sudo apt update
sudo apt install -y python3-venv python3-pip git curl

python3 -m venv .venv --system-site-packages
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 9. OpenCV DNN 모델 파일 준비 방법

수업 Section 16에서 사용한 OpenCV DNN MobileNet SSD 모델 파일 두 개가 필요하다.
이 프로젝트는 얼굴의 신원을 구분하는 얼굴인식이 아니라, 웹캠 화면 안에서 `person` 객체가 있는지 확인하는 사람 객체검출을 사용한다.
모델 준비는 GitHub 저장소를 검색하거나 clone하지 않고, 스크립트가 필요한 원본 파일만 직접 내려받는 방식으로 진행한다.

```text
models/
├── frozen_inference_graph.pb
└── ssd_mobilenet_v2_coco_2018_03_29.pbtxt
```

준비 명령:

```bash
cd ~/iot-ex/aiot_ai_room_security
python3 download_models.py
ls -lh models
```

`ls -lh models`를 실행했을 때 아래 두 파일이 보여야 한다.

```text
frozen_inference_graph.pb
ssd_mobilenet_v2_coco_2018_03_29.pbtxt
```

모델 파일이 없으면 프로그램은 필요한 파일명을 콘솔에 안내하고 비정상 종료되지 않도록 처리한다.

이미 수업 때 받은 모델 파일이 라즈베리파이에 있으면 다운로드 대신 직접 복사해도 된다.

```bash
cd ~/iot-ex/aiot_ai_room_security
mkdir -p models
cp /모델파일이있는경로/frozen_inference_graph.pb models/
cp /모델파일이있는경로/ssd_mobilenet_v2_coco_2018_03_29.pbtxt models/
ls -lh models
```

## 10. 텔레그램 봇 설정 방법

1. 텔레그램에서 `BotFather`를 검색한다.
2. `/newbot` 명령으로 새 봇을 만든다.
3. BotFather가 발급한 token을 복사한다.
4. 새 봇 채팅방에 들어가 아무 메시지나 보낸다.
5. 라즈베리파이 터미널에서 아래 명령으로 `chat_id`를 확인한다.

```bash
export TELEGRAM_BOT_TOKEN="BotFather에서_받은_token"
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates"
```

출력 JSON에서 `"chat":{"id":...}` 값을 찾아 설정한다.

```bash
export TELEGRAM_CHAT_ID="확인한_chat_id"
```

token과 chat_id가 비어 있으면 텔레그램 전송만 건너뛰고 콘솔 출력과 로그 기록은 계속 진행된다.

## 11. 실행 방법

### 11.1 하드웨어 없이 mock 테스트

```bash
cd ~/iot-ex/aiot_ai_room_security
source .venv/bin/activate

export AIOT_MOCK_MODE=1
export AIOT_MOCK_MOTION=1
export AIOT_MOCK_PERSON_DETECTED=1
export AIOT_MAX_LOOP_COUNT=1
export AIOT_BUZZER_BEEP_SECONDS=0.1

python main.py
```

### 11.2 실제 라즈베리파이 실행

```bash
cd ~/iot-ex/aiot_ai_room_security
source .venv/bin/activate

export AIOT_MOCK_MODE=0
export AIOT_CAMERA_INDEX=0
export TELEGRAM_BOT_TOKEN="BotFather에서_받은_token"
export TELEGRAM_CHAT_ID="확인한_chat_id"

python main.py
```

종료할 때는 `Ctrl+C`를 누른다.

## 12. 주요 설정값

| 설정 | 기본값 | 설명 |
| --- | --- | --- |
| `PIR_SENSOR_PIN` | `16` | PIR Signal GPIO |
| `BUZZER_PIN` | `18` | 2핀 부저 `+` 또는 3핀 부저 `S` |
| `PERSON_CONFIDENCE_THRESHOLD` | `0.50` | 사람 탐지 confidence 기준 |
| `ALERT_COOLDOWN_SECONDS` | `10.0` | 중복 알림 방지 시간 |
| `BUZZER_BEEP_SECONDS` | `2.0` | 부저 경고음 시간 |
| `MOCK_MODE` | `True` | 하드웨어 없는 테스트 모드 |

## 13. 데모 시나리오

1. 라즈베리파이, PIR 센서, 부저, USB 웹캠 연결 상태를 보여준다.
2. 프로그램 실행 화면에서 `"AI 침입 감지 시스템 대기 중..."` 메시지를 보여준다.
3. 사람이 방 안으로 들어와 PIR 센서가 움직임을 감지하게 한다.
4. 콘솔의 AI person 탐지 confidence를 보여준다.
5. 부저 경고음이 울리는 모습을 촬영한다.
6. `captures/` 폴더에 저장된 사진을 보여준다.
7. 텔레그램 메시지와 사진 알림을 보여준다.
8. `logs/event_log.csv`에 기록된 이벤트를 보여준다.
9. 10초 이내 재감지 시 cooldown 메시지가 나오는지 확인한다.
10. `Ctrl+C`로 종료하면 부저가 꺼지는지 보여준다.

## 14. 제출 링크

- 유튜브 결과 링크: `<영상 업로드 후 입력>`
- GitHub 링크: `https://github.com/PDJ-N/iot-ex`

## 15. 보고서 작성 초안

### 15.1 요약

본 프로젝트는 PIR 인체감지 센서와 OpenCV DNN MobileNet SSD 객체검출을 결합한 Raspberry Pi 기반 AIoT 방 침입 감지 시스템이다. PIR 센서가 움직임을 감지하면 USB 웹캠 프레임을 분석하여 사람이 있는지 확인하고, 사람이 감지되면 능동 부저, 텔레그램 알림, 사진 저장, CSV 로그 기록을 수행한다.

### 15.2 실험 목적

센서 입력, AI 영상 분석, GPIO 출력, 원격 알림, 로그 기록을 결합하여 실제 생활 공간에 적용 가능한 간단한 방 보안 시스템을 구현하는 것이 목적이다. 단순 움직임 감지만 사용하는 경보기보다 AI person 객체검출을 추가하여 침입 판단의 신뢰도를 높인다.

### 15.3 실험 내용

PIR 센서로 움직임을 감지하고, 움직임이 발생했을 때 USB 웹캠에서 프레임을 읽는다. OpenCV DNN MobileNet SSD 모델로 `person` 객체를 탐지하고, confidence가 기준값 이상이면 침입 이벤트로 판단한다. 이후 부저 경고음, 이미지 저장, 텔레그램 메시지 및 사진 전송, CSV 로그 기록을 수행한다.

### 15.4 실험 관련 이론 및 기술

PIR 센서는 사람이나 동물의 움직임에 따른 적외선 변화를 감지하는 센서이다. OpenCV는 영상 처리 라이브러리이며, DNN 모듈을 사용하면 사전 학습된 MobileNet SSD 모델로 사람, 차량, 동물 등 다양한 객체를 탐지할 수 있다. Telegram Bot API는 HTTP 요청을 이용해 메시지와 사진을 사용자의 텔레그램 앱으로 전송한다. CSV 로그는 이벤트 발생 내역을 파일로 남기는 간단한 데이터 기록 방식이다.

### 15.5 실험 환경 및 절차

Raspberry Pi 5에 PIR 센서, 능동 부저, USB 웹캠을 연결한다. Python 가상환경을 만들고 OpenCV, gpiozero, requests를 설치한다. MobileNet SSD 모델 파일을 `models/` 폴더에 준비하고, 텔레그램 bot token과 chat_id를 환경변수로 설정한다. mock 모드로 소프트웨어 흐름을 먼저 확인한 뒤, 실제 모드에서 센서와 부저, 웹캠 동작을 검증한다.

### 15.6 실험 결과 예상

사람이 방에 들어오면 PIR 센서 값이 `1`로 변하고, 웹캠 프레임에서 AI가 `person` 객체를 탐지한다. 침입 이벤트가 발생하면 부저가 울리고, 사진이 `captures/` 폴더에 저장되며, 텔레그램으로 메시지와 사진이 전송된다. 동시에 `logs/event_log.csv`에 감지 시간, 이벤트 종류, confidence, 이미지 파일명이 기록된다.

### 15.7 결론 및 고찰

본 시스템은 PIR 센서와 AI 객체검출을 함께 사용하여 간단한 방 침입 감지 기능을 구현하였다. PIR 센서는 빠르게 움직임을 감지하지만 사람 외의 움직임에도 반응할 수 있으므로, OpenCV AI를 통해 사람이 맞는지 한 번 더 확인하는 구조가 의미 있다. 다만 조명 상태, 웹캠 각도, 모델 파일 경로, confidence 기준값에 따라 탐지 성능이 달라질 수 있으므로 실제 방 환경에서 반복 테스트하며 값을 조정해야 한다.
