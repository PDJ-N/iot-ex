"""능동 부저를 제어하는 모듈."""

import time

import config


if not config.MOCK_MODE:
    try:
        from gpiozero import OutputDevice
    except ImportError as exc:
        raise RuntimeError(
            "gpiozero를 불러올 수 없습니다. "
            "라즈베리파이에서 'pip install gpiozero'를 실행하거나 "
            "config.py의 MOCK_MODE를 True로 바꾸세요."
        ) from exc

    # 2핀 부저는 + 핀을 GPIO18에 연결한다.
    # 3핀 부저 모듈은 S 핀을 GPIO18에 연결하고, +는 3.3V, -는 GND에 연결한다.
    _buzzer = OutputDevice(config.BUZZER_PIN, active_high=True, initial_value=False)
else:
    _buzzer = None


_mock_buzzer_is_on = False


def buzzer_on():
    """부저를 켠다."""
    global _mock_buzzer_is_on
    if config.MOCK_MODE:
        if not _mock_buzzer_is_on:
            print("[MOCK 부저] ON")
        _mock_buzzer_is_on = True
        return

    _buzzer.on()


def buzzer_off():
    """부저를 끈다."""
    global _mock_buzzer_is_on
    if config.MOCK_MODE:
        if _mock_buzzer_is_on:
            print("[MOCK 부저] OFF")
        _mock_buzzer_is_on = False
        return

    _buzzer.off()


def beep(duration):
    """지정한 시간 동안 부저를 울린 뒤 끈다."""
    if duration <= 0:
        return

    print(f"[부저] {duration:.1f}초 동안 경고음을 울립니다.")
    try:
        buzzer_on()
        time.sleep(duration)
    finally:
        buzzer_off()


def all_off():
    """프로그램 종료 시 부저가 켜진 상태로 남지 않게 한다."""
    buzzer_off()
