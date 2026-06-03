"""PIR 센서, 빨간 LED, 능동부저 모듈의 Signal 핀을 제어한다."""

import time

import config


# MOCK_MODE에서는 gpiozero를 불러오지 않는다.
# 따라서 라즈베리파이가 아닌 일반 PC에서도 실행 흐름을 공부할 수 있다.
if not config.MOCK_MODE:
    try:
        from gpiozero import LED, MotionSensor, OutputDevice
    except ImportError as exc:
        raise RuntimeError(
            "gpiozero를 불러올 수 없습니다. "
            "라즈베리파이에서 'pip install gpiozero'를 실행하거나 "
            "config.py의 MOCK_MODE를 True로 바꾸세요."
        ) from exc

    _pir_sensor = MotionSensor(config.PIR_SENSOR_PIN)
    _red_led = LED(config.RED_LED_PIN)
    # 3핀 부저 모듈에서는 GPIO18을 부저의 S 또는 Signal 핀에 연결한다.
    _active_buzzer = OutputDevice(
        config.ACTIVE_BUZZER_PIN,
        active_high=True,
        initial_value=False,
    )
else:
    _pir_sensor = None
    _red_led = None
    _active_buzzer = None


_mock_led_is_on = False
_mock_buzzer_is_on = False


def read_pir_motion():
    """PIR 센서 값이 1이면 True를 반환한다."""
    if config.MOCK_MODE:
        return config.MOCK_PIR_MOTION
    return _pir_sensor.value == 1


def led_on():
    """빨간 LED를 켠다."""
    global _mock_led_is_on
    if config.MOCK_MODE:
        if not _mock_led_is_on:
            print("[MOCK 하드웨어] 빨간 LED ON")
        _mock_led_is_on = True
        return
    _red_led.on()


def led_off():
    """빨간 LED를 끈다."""
    global _mock_led_is_on
    if config.MOCK_MODE:
        if _mock_led_is_on:
            print("[MOCK 하드웨어] 빨간 LED OFF")
        _mock_led_is_on = False
        return
    _red_led.off()


def buzzer_on():
    """능동부저를 켜서 경고음을 출력한다."""
    global _mock_buzzer_is_on
    if config.MOCK_MODE:
        if not _mock_buzzer_is_on:
            print("[MOCK 하드웨어] 능동부저 ON")
        _mock_buzzer_is_on = True
        return
    _active_buzzer.on()


def buzzer_off():
    """능동부저를 끈다."""
    global _mock_buzzer_is_on
    if config.MOCK_MODE:
        if _mock_buzzer_is_on:
            print("[MOCK 하드웨어] 능동부저 OFF")
        _mock_buzzer_is_on = False
        return
    _active_buzzer.off()


def warning_blink(duration, interval):
    """지정된 시간 동안 LED를 깜빡이고 부저를 울린다."""
    if duration <= 0:
        return
    if interval <= 0:
        raise ValueError("LED 점멸 간격(interval)은 0보다 커야 합니다.")

    print(f"[경고 장치] {duration:.1f}초 동안 LED와 부저를 작동합니다.")
    end_time = time.monotonic() + duration
    buzzer_on()

    try:
        while time.monotonic() < end_time:
            led_on()
            time.sleep(interval)
            led_off()
            time.sleep(interval)
    finally:
        # 실행 중 Ctrl+C가 입력되더라도 경고 장치를 반드시 끈다.
        led_off()
        buzzer_off()


def all_off():
    """프로그램 종료 전에 LED와 부저를 모두 끈다."""
    led_off()
    buzzer_off()
    if config.MOCK_MODE:
        print("[MOCK 하드웨어] 모든 경고 장치를 OFF 상태로 정리했습니다.")
