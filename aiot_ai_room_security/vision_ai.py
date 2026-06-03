"""OpenCV DNN MobileNet SSD로 USB 웹캠 프레임에서 사람을 탐지한다."""

from datetime import datetime

import config


_cv2 = None
_model = None
_camera = None
_opencv_error_reported = False
_model_error_reported = False
_camera_error_reported = False


def _get_cv2():
    """OpenCV가 필요할 때만 import하여 mock 테스트를 쉽게 만든다."""
    global _cv2, _opencv_error_reported
    if _cv2 is not None:
        return _cv2

    try:
        import cv2
    except ImportError:
        if not _opencv_error_reported:
            print("[OpenCV 오류] cv2가 없습니다. 'pip install opencv-python'을 실행하세요.")
            _opencv_error_reported = True
        return None

    _cv2 = cv2
    return _cv2


def _get_model():
    """MobileNet SSD 모델을 한 번만 불러와 재사용한다."""
    global _model, _model_error_reported
    if _model is not None:
        return _model

    cv2 = _get_cv2()
    if cv2 is None:
        return None

    missing_paths = [
        path
        for path in (config.MODEL_WEIGHTS_PATH, config.MODEL_CONFIG_PATH)
        if not path.is_file()
    ]
    if missing_paths:
        if not _model_error_reported:
            print("[AI 모델 오류] MobileNet SSD 모델 파일이 없습니다.")
            for path in missing_paths:
                print(f"  - 필요한 파일: {path}")
            print("  python3 download_models.py를 실행하거나 수업 때 받은 모델 파일을 models 폴더에 넣으세요.")
            _model_error_reported = True
        return None

    try:
        _model = cv2.dnn.readNetFromTensorflow(
            str(config.MODEL_WEIGHTS_PATH),
            str(config.MODEL_CONFIG_PATH),
        )
    except cv2.error as exc:
        if not _model_error_reported:
            print(f"[AI 모델 오류] 모델을 읽지 못했습니다: {exc}")
            _model_error_reported = True
        return None

    return _model


def _get_camera():
    """USB 웹캠을 열고, 이미 열려 있으면 기존 객체를 사용한다."""
    global _camera, _camera_error_reported
    if _camera is not None and _camera.isOpened():
        return _camera

    cv2 = _get_cv2()
    if cv2 is None:
        return None

    camera = cv2.VideoCapture(config.CAMERA_INDEX)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)

    if not camera.isOpened():
        camera.release()
        if not _camera_error_reported:
            print(
                "[웹캠 오류] USB 웹캠을 열 수 없습니다. "
                "연결 상태와 AIOT_CAMERA_INDEX 값을 확인하세요."
            )
            _camera_error_reported = True
        return None

    _camera = camera
    return _camera


def _draw_person_box(frame, detection, confidence):
    """사람 위치에 박스와 confidence 텍스트를 표시한다."""
    cv2 = _get_cv2()
    image_height, image_width, _ = frame.shape

    left = max(0, int(detection[3] * image_width))
    top = max(0, int(detection[4] * image_height))
    right = min(image_width - 1, int(detection[5] * image_width))
    bottom = min(image_height - 1, int(detection[6] * image_height))

    cv2.rectangle(frame, (left, top), (right, bottom), (23, 230, 210), 2)
    cv2.putText(
        frame,
        f"person {confidence:.2f}",
        (left, max(20, top - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2,
    )


def detect_person():
    """사람 탐지 여부, confidence, 프레임을 반환한다."""
    global _camera
    if config.MOCK_MODE:
        if config.MOCK_PERSON_DETECTED:
            confidence = config.MOCK_PERSON_CONFIDENCE
            print(f"[MOCK AI] person 탐지, confidence={confidence:.2f}")
            return True, confidence, None
        print("[MOCK AI] person이 탐지되지 않았습니다.")
        return False, 0.0, None

    model = _get_model()
    camera = _get_camera()
    if model is None or camera is None:
        return False, 0.0, None

    try:
        success, frame = camera.read()
    except Exception as exc:
        print(f"[웹캠 오류] 프레임 읽기 중 오류가 발생했습니다: {exc}")
        return False, 0.0, None

    if not success or frame is None:
        print("[웹캠 오류] 프레임을 읽지 못했습니다. 다음 감지에서 다시 시도합니다.")
        camera.release()
        _camera = None
        return False, 0.0, None

    cv2 = _get_cv2()
    try:
        blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True)
        model.setInput(blob)
        output = model.forward()
    except cv2.error as exc:
        print(f"[AI 탐지 오류] 프레임 분석 중 오류가 발생했습니다: {exc}")
        return False, 0.0, frame

    best_confidence = 0.0
    for detection in output[0, 0, :, :]:
        class_id = int(detection[1])
        confidence = float(detection[2])

        if (
            class_id == config.PERSON_CLASS_ID
            and confidence >= config.PERSON_CONFIDENCE_THRESHOLD
        ):
            best_confidence = max(best_confidence, confidence)
            _draw_person_box(frame, detection, confidence)

    if best_confidence > 0:
        return True, best_confidence, frame
    return False, 0.0, frame


def save_frame(frame):
    """현재 프레임을 captures 폴더에 저장하고 파일 경로를 반환한다."""
    if frame is None:
        if config.MOCK_MODE:
            print("[MOCK 저장] 실제 프레임이 없어서 이미지 저장을 건너뜁니다.")
        return ""

    cv2 = _get_cv2()
    if cv2 is None:
        return ""

    try:
        config.CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"[이미지 저장 오류] captures 폴더를 만들 수 없습니다: {exc}")
        return ""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    image_path = config.CAPTURE_DIR / f"intrusion_{timestamp}.jpg"

    try:
        if cv2.imwrite(str(image_path), frame):
            print(f"[이미지 저장] {image_path}")
            return str(image_path)
    except cv2.error as exc:
        print(f"[이미지 저장 오류] 저장 실패: {exc}")
        return ""

    print(f"[이미지 저장 오류] 저장 실패: {image_path}")
    return ""


def close_camera():
    """프로그램 종료 시 카메라 자원을 정리한다."""
    global _camera
    if _camera is not None:
        _camera.release()
        _camera = None
    if _cv2 is not None:
        try:
            _cv2.destroyAllWindows()
        except _cv2.error:
            pass
