# AI 기반 개인 방 침입 감지 및 텔레그램 알림 시스템

## 1. 프로젝트 개요

Raspberry Pi, PIR 인체 감지 센서, USB 웹캠, 빨간 LED, 능동부저를 결합한 개인 방 보안 시스템이다. PIR 센서가 움직임을 감지하면 웹캠 프레임을 가져오고, OpenCV DNN MobileNet SSD 모델이 `person` 객체를 확인한다. 사람이 맞으면 경고 장치를 작동하고 텔레그램 알림과 CSV 로그를 남긴다.

단순 PIR 경보기와 달리 움직임을 바로 침입으로 확정하지 않는다. PIR 센서를 1차 트리거로 사용하고 AI 객체검출을 2차 확인 단계로 사용하여 오탐을 줄인다.

## 2. 활용한 수업 내용

| 학습자료 | 반영한 내용 |
| --- | --- |
| Section 3, `AIoT_04_p031-036.pdf` | PIR 센서의 `GPIO 16`, 감지값 `1`, 침입 감지 활용 |
| Section 5, `AIoT_06_p048-059.pdf` | 빨간 LED의 `GPIO 21`, `330Ω` 저항 연결 |
| Section 7, `AIoT_08_p071-086.pdf` | BotFather 토큰, `chat_id`, 텔레그램 전송 구조 |
| Section 14, `AIoT_15_p151-157.pdf` | OpenCV 영상 처리 결과와 능동부저 경고 연동 |
| Section 15, `AIoT_16_p158-164.pdf` | 인식 결과 기록과 중복 저장 방지 개념 |
| Section 16, `AIoT_17_p165-174.pdf` | OpenCV DNN, MobileNet SSD, confidence 기반 객체검출 |

수업 저장소의 `project_14/main14.py`, `project_20/main20.py`, `project_6/main6-2.py`, `project_34/main34-1.py`, `project_28/main28-2.py` 흐름도 참고하여 하나의 시스템으로 통합했다.

## 3. 프로젝트 구조

```text
aiot_room_security/
├── main.py                 # 전체 실행 흐름
├── config.py               # 핀, 모델 경로, 텔레그램, cooldown 설정
├── hardware.py             # PIR, LED, 능동부저 제어
├── vision_ai.py            # OpenCV DNN person 탐지
├── notifier.py             # Telegram Bot API 요청
├── logger.py               # CSV 이벤트 로그 기록
├── requirements.txt
├── README.md
└── logs/
    └── event_log.csv
```

실행 중 필요에 따라 `models/`와 `captures/` 폴더를 추가로 사용한다. `models/`에는 AI 모델 파일을 직접 준비하고, `captures/`는 사람 탐지 이미지를 저장할 때 자동 생성된다.

## 4. 하드웨어 구성과 회로 연결표

| 부품 | 부품 핀 | Raspberry Pi 연결 |
| --- | --- | --- |
| PIR Sensor | Signal | `GPIO 16` |
| PIR Sensor | VCC | `3.3V PWR` |
| PIR Sensor | GND | `GND` |
| 빨간 LED | 긴 다리(+) | `GPIO 21` |
| 빨간 LED | 짧은 다리(-) | `330Ω 저항`을 거쳐 `GND` |
| 3핀 능동부저 모듈 | `S` 또는 `Signal` | `GPIO 18` |
| 3핀 능동부저 모듈 | `+` 또는 `VCC` | `3.3V PWR` |
| 3핀 능동부저 모듈 | `-` 또는 `GND` | `GND` |
| USB 웹캠 | USB | Raspberry Pi USB 포트 |

PIR 센서, LED, 저항, 능동부저는 브레드보드에 연결한다. 사용자의 3핀 부저 모듈은 `S`, `+`, `-` 기준으로 연결한다. 즉 `S`는 `GPIO 18`, `+`는 `3.3V`, `-`는 `GND`이다. 2핀 능동부저를 쓰는 경우에만 `+`를 `GPIO 18`, `-`를 `GND`에 연결한다.

## 5. 동작 흐름

1. `hardware.py`가 PIR 센서의 값을 반복 확인한다.
2. PIR 값이 `1`이면 `vision_ai.py`가 웹캠 프레임 한 장을 가져온다.
3. OpenCV DNN이 MobileNet SSD 모델로 프레임을 분석한다.
4. `person` 클래스(ID `1`)가 confidence 기준값 이상이면 침입으로 판단한다.
5. 박스와 `person confidence` 텍스트를 이미지에 표시하고 선택적으로 저장한다.
6. `logs/event_log.csv`에 시각, 이벤트 종류, 메시지, confidence를 기록한다.
7. Telegram Bot API로 `"방에 누군가 들어왔습니다."` 메시지를 전송한다.
8. 빨간 LED를 깜빡이고 능동부저를 울린다.
9. cooldown 시간 동안 같은 상황의 반복 알림을 억제한다.
10. `Ctrl+C` 입력 시 LED와 부저를 반드시 끄고 종료한다.

## 6. OpenCV DNN 모델 파일 준비 방법

Section 16 수업 자료와 동일한 모델 파일 두 개가 필요하다.

```text
aiot_room_security/
└── models/
    ├── frozen_inference_graph.pb
    └── ssd_mobilenet_v2_coco_2018_03_29.pbtxt
```

수업 자료에서 안내한 저장소를 이용하는 방법은 다음과 같다.

```bash
cd ~/aiot_room_security
git clone https://github.com/moonchuljang/OpencvDnn.git /tmp/OpencvDnn
mkdir -p models
cp /tmp/OpencvDnn/models/frozen_inference_graph.pb models/
cp /tmp/OpencvDnn/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt models/
```

모델 파일 경로가 다르면 `config.py`를 수정하거나 `AIOT_MODEL_WEIGHTS_PATH`, `AIOT_MODEL_CONFIG_PATH` 환경변수를 설정한다. 파일이 없으면 프로그램이 필요한 경로를 콘솔에 안내한다.

## 7. 텔레그램 봇 설정 방법

1. 텔레그램에서 `BotFather`를 검색하고 `/newbot` 명령으로 봇을 생성한다.
2. BotFather가 발급한 token을 기록한다. token은 외부에 공개하거나 GitHub에 올리면 안 된다.
3. 새로 만든 봇 채팅방을 열고 먼저 아무 메시지나 보낸다.
4. 아래 명령의 결과에서 `chat.id` 값을 확인한다.

```bash
export TELEGRAM_BOT_TOKEN="BotFather에서_발급받은_token"
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates"
export TELEGRAM_CHAT_ID="확인한_chat_id"
```

token 또는 `chat_id`를 설정하지 않으면 텔레그램 전송만 건너뛰고 콘솔, 경고 장치, CSV 로그는 계속 작동한다.

## 8. 설치 방법

Raspberry Pi 터미널에서 다음 명령을 순서대로 실행한다.

```bash
cd ~
git clone <본인의_GitHub_저장소_URL>
cd <저장소_폴더>/aiot_room_security
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

이후 6절의 모델 파일과 7절의 텔레그램 환경변수를 준비한다.

## 9. 실행 방법

실제 Raspberry Pi에서 실행:

```bash
cd ~/<저장소_폴더>/aiot_room_security
source .venv/bin/activate
export AIOT_MOCK_MODE=0
export TELEGRAM_BOT_TOKEN="BotFather에서_발급받은_token"
export TELEGRAM_CHAT_ID="확인한_chat_id"
python main.py
```

웹캠이 열리지 않으면 다음 설정도 시험한다.

```bash
export AIOT_CAMERA_INDEX=0
python main.py
```

일반 PC의 PowerShell에서 하드웨어 없이 1회 테스트:

```powershell
cd .\aiot_room_security
$env:AIOT_MOCK_MODE="1"
$env:AIOT_MOCK_PIR_MOTION="1"
$env:AIOT_MAX_LOOP_COUNT="1"
$env:AIOT_WARNING_DURATION="0.1"
python .\main.py
```

## 10. 주요 설정값

| 설정 | 기본값 | 설명 |
| --- | --- | --- |
| `PIR_SENSOR_PIN` | `16` | PIR Signal GPIO |
| `RED_LED_PIN` | `21` | 빨간 LED GPIO |
| `ACTIVE_BUZZER_PIN` | `18` | 능동부저 GPIO |
| `PERSON_CONFIDENCE_THRESHOLD` | `0.50` | person 최소 confidence |
| `ALERT_COOLDOWN_SECONDS` | `30.0` | 반복 알림 억제 시간 |
| `MOCK_MODE` | `True` | PC 테스트용 모드 |
| `SAVE_CAPTURE_IMAGES` | `True` | 탐지 이미지 저장 여부 |

환경변수로 바꿀 때에는 설정 이름 앞에 `AIOT_`를 붙인다. 예: `AIOT_ALERT_COOLDOWN=60`, `AIOT_PERSON_CONFIDENCE=0.60`.

## 11. 데모 시나리오

1. 프로그램을 실행하고 터미널의 준비 완료 메시지를 촬영한다.
2. 사람이 없는 상태에서 LED와 부저가 꺼져 있음을 보여준다.
3. 사람이 방 안으로 들어가 PIR 센서를 작동시킨다.
4. 콘솔의 PIR 감지, AI person confidence, CSV 로그 저장 메시지를 보여준다.
5. 빨간 LED 점멸과 능동부저 경고음을 촬영한다.
6. 스마트폰의 텔레그램 알림을 보여준다.
7. 곧바로 다시 움직여 cooldown 메시지가 출력되고 중복 알림이 억제되는지 확인한다.
8. `Ctrl+C`로 종료하여 LED와 부저가 꺼지는 모습을 보여준다.

## 12. 제출 링크

- 유튜브 결과 링크: `<영상 업로드 후 입력>`
- GitHub 링크: `<GitHub 저장소 업로드 후 입력>`

## 13. 결과보고서에 사용할 수 있는 설명

### 13.1 실험 목적

PIR 센서 기반 움직임 감지, OpenCV DNN 기반 사람 객체검출, GPIO 출력, 텔레그램 알림, CSV 로그 기록을 결합하여 Raspberry Pi 기반 AIoT 보안 시스템을 구현한다. AI 2차 판정을 사용하여 단순 움직임 감지보다 침입 판단의 신뢰도를 높이는 것이 목적이다.

### 13.2 실험 내용

PIR 센서가 움직임을 감지하면 웹캠 프레임을 입력받는다. MobileNet SSD 모델로 `person` 객체를 검출하고 confidence가 기준값 이상일 때 침입 이벤트를 생성한다. 이벤트 발생 시 LED, 능동부저, 텔레그램, CSV 로그를 연동하고 cooldown으로 중복 알림을 줄인다.

### 13.3 실험 관련 이론 및 기술

PIR 센서는 사람과 같은 열원 이동에 따른 주변 적외선 변화를 수동적으로 감지한다. OpenCV는 웹캠 프레임을 처리하며, DNN 모듈은 사전 학습된 MobileNet SSD의 가중치와 모델 구조를 불러와 객체의 클래스, confidence, 위치를 추론한다. Telegram Bot API는 HTTP 요청으로 실시간 알림을 전달한다.

### 13.4 실험 환경 및 절차

Raspberry Pi에 PIR 센서, LED, `330Ω` 저항, 능동부저를 브레드보드로 연결하고 USB 웹캠을 장착한다. Python 가상환경에 필요한 라이브러리를 설치하고 모델 파일, 텔레그램 token, `chat_id`를 설정한다. mock 모드로 소프트웨어 흐름을 먼저 확인한 뒤 실제 모드에서 센서와 경고 장치를 검증한다.

### 13.5 실험 결과 예상

사람이 방 안에 들어오면 PIR 센서 값이 `1`로 변하고, AI가 `person` 객체를 기준 confidence 이상으로 탐지한다. 빨간 LED와 능동부저가 작동하며 텔레그램 메시지, CSV 로그, 선택적 캡처 이미지가 생성된다. cooldown 동안에는 같은 이벤트의 알림이 반복되지 않는다.

### 13.6 결론 및 고찰

이 프로젝트는 센서 입력, AI 영상 분석, 물리적 경고, 원격 알림, 로그 기록을 하나의 AIoT 흐름으로 통합한다. PIR 센서만 사용할 때 발생할 수 있는 오탐을 AI person 검출로 보완한다. 조명, 카메라 각도, confidence 기준값, PIR 감도에 따라 탐지 결과가 달라질 수 있으므로 실제 방 환경에서 반복 시험하여 값을 조정해야 한다.
