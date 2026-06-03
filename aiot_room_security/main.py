"""AI 기반 개인 방 침입 감지 및 텔레그램 알림 시스템의 실행 파일."""

import time

import config
import hardware
import vision_ai
from logger import write_event
from notifier import send_telegram_message


INTRUSION_MESSAGE = "방에 누군가 들어왔습니다."


def _handle_motion(last_alert_time):
    """PIR 감지 후 AI 확인과 cooldown 판단을 거쳐 침입 알림을 처리한다."""
    print("[PIR 감지] 움직임이 감지되었습니다. AI로 사람 여부를 확인합니다.")
    person_detected, confidence, frame = vision_ai.detect_person()

    if not person_detected:
        print("[AI 확인] confidence 기준을 넘는 person 객체가 없습니다.")
        return last_alert_time

    now = time.monotonic()
    if last_alert_time is not None:
        elapsed = now - last_alert_time
        if elapsed < config.ALERT_COOLDOWN_SECONDS:
            remaining = config.ALERT_COOLDOWN_SECONDS - elapsed
            print(f"[cooldown] 같은 상황의 반복 알림을 {remaining:.1f}초 동안 억제합니다.")
            return last_alert_time

    print(f"[침입 감지] {INTRUSION_MESSAGE} confidence={confidence:.2f}")
    write_event("INTRUSION", INTRUSION_MESSAGE, confidence)
    vision_ai.save_detection_image(frame, confidence)
    send_telegram_message(INTRUSION_MESSAGE)

    # cooldown 시작 시각을 경고 장치 작동 전에 기록한다.
    last_alert_time = now
    hardware.warning_blink(
        config.WARNING_DURATION_SECONDS,
        config.WARNING_BLINK_INTERVAL_SECONDS,
    )
    return last_alert_time


def main():
    """PIR 센서를 반복 확인하고 Ctrl+C 입력 시 장치를 안전하게 종료한다."""
    print("=== AI 기반 개인 방 침입 감지 시스템 준비 완료 ===")
    print(
        f"MOCK_MODE={config.MOCK_MODE}, "
        f"person confidence 기준={config.PERSON_CONFIDENCE_THRESHOLD:.2f}, "
        f"cooldown={config.ALERT_COOLDOWN_SECONDS:.1f}초"
    )
    print("종료하려면 Ctrl+C를 누르세요.")

    last_alert_time = None
    loop_count = 0

    try:
        while True:
            loop_count += 1
            if hardware.read_pir_motion():
                last_alert_time = _handle_motion(last_alert_time)

            if config.MAX_LOOP_COUNT > 0 and loop_count >= config.MAX_LOOP_COUNT:
                print("[실행 종료] AIOT_MAX_LOOP_COUNT에 도달했습니다.")
                break

            time.sleep(config.PIR_POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n[사용자 종료] Ctrl+C가 입력되었습니다.")
    finally:
        # 정상 종료, Ctrl+C, 예상하지 못한 오류 모두에서 정리 코드를 실행한다.
        vision_ai.close_camera()
        hardware.all_off()
        print("[시스템 종료] LED와 부저를 끄고 프로그램을 종료합니다.")


if __name__ == "__main__":
    main()
