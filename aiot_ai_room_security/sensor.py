"""PIR 인체감지 센서를 읽는 모듈."""

import config


if not config.MOCK_MODE:
    try:
        from gpiozero import MotionSensor
    except ImportError as exc:
        raise RuntimeError(
            "gpiozero를 불러올 수 없습니다. "
            "라즈베리파이에서 'pip install gpiozero'를 실행하거나 "
            "config.py의 MOCK_MODE를 True로 바꾸세요."
        ) from exc

    _pir_sensor = MotionSensor(config.PIR_SENSOR_PIN)
else:
    _pir_sensor = None


def read_motion():
    """PIR 센서 값이 1이면 True, 움직임이 없으면 False를 반환한다."""
    if config.MOCK_MODE:
        if config.MOCK_CONSOLE_INPUT:
            answer = input("[MOCK PIR] 움직임 감지로 처리할까요? (y/n): ").strip().lower()
            return answer in {"y", "yes", "1", "true"}

        print(f"[MOCK PIR] 움직임 감지값: {int(config.MOCK_MOTION)}")
        return config.MOCK_MOTION

    return _pir_sensor.value == 1
