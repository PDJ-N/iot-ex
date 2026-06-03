"""OpenCV DNN MobileNet SSD 모델로 웹캠 프레임의 사람을 탐지한다."""

from datetime import datetime

import config


_cv2 = None
_model = None
_camera = None
_opencv_error_reported = False
_model_error_reported = False
_camera_error_reported = False


def _get_cv2():
    """실제 AI 탐지가 필요할 때만 OpenCV를 불러온다."""
    global _cv2, _opencv_error_reported
    if _cv2 is not None:
        return _cv2

    try:
        import cv2
    except ImportError:
        if not _opencv_error_reported:
            print(
                "[OpenCV 오류] cv2를 불러올 수 없습니다. "
                "'pip install opencv-python'을 실행하세요."
            )
            _opencv_error_reported = True
        return None

    _cv2 = cv2
    return _cv2


def _get_model():
    """MobileNet SSD 가중치와 모델 구조 파일을 한 번만 불러온다."""
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
            print(
                "  README.md의 'OpenCV DNN 모델 파일 준비 방법'을 참고하여 "
                "models 폴더에 두 파일을 넣으세요."
            )
            _model_error_reported = True
        return None

    try:
        # Section 16 수업 자료와 동일한 TensorFlow 모델 로딩 방식을 사용한다.
        _model = cv2.dnn.readNetFromTensorflow(
            str(config.MODEL_WEIGHTS_PATH),
            str(config.MODEL_CONFIG_PATH),
        )
    except cv2.error as exc:
        if not _model_error_reported:
            print(f"[AI 모델 오류] MobileNet SSD 모델을 읽지 못했습니다: {exc}")
            _model_error_reported = True
        return None

    return _model


def _get_camera():
    """웹캠을 한 번 열고 이후 PIR 이벤트에서도 같은 객체를 재사용한다."""
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
                "[웹캠 오류] 웹캠을 열 수 없습니다. USB 연결을 확인하고 "
                "AIOT_CAMERA_INDEX=0 설정도 시험해 보세요."
            )
            _camera_error_reported = True
        return None

    _camera = camera
    return _camera


def _draw_person_box(frame, detection, confidence):
    """사람의 위치에 박스와 confidence 텍스트를 표시한다."""
    cv2 = _get_cv2()
    image_height, image_width, _ = frame.shape

    left = max(0, int(detection[3] * image_width))
    top = max(0, int(detection[4] * image_height))
    right = min(image_width - 1, int(detection[5] * image_width))
    bottom = min(image_height - 1, int(detection[6] * image_height))

    cv2.rectangle(frame, (left, top), (right, bottom), (23, 230, 210), 2)
    label = f"person {confidence:.2f}"
    cv2.putText(
        frame,
        label,
        (left, max(20, top - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2,
    )


def _show_frame_if_enabled(frame):
    """데모 중 필요할 때만 탐지 결과 GUI 창을 표시한다."""
    if not config.SHOW_DETECTION_WINDOW:
        return

    cv2 = _get_cv2()
    try:
        cv2.imshow("AIoT Room Security", frame)
        cv2.waitKey(1)
    except cv2.error as exc:
        print(f"[OpenCV 안내] GUI 창을 표시하지 못했습니다: {exc}")


def detect_person():
    """사람 탐지 여부, 가장 높은 confidence, 박스가 표시된 프레임을 반환한다."""
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

    success, frame = camera.read()
    if not success or frame is None:
        print("[웹캠 오류] 프레임을 읽지 못했습니다. 다음 PIR 이벤트에서 다시 시도합니다.")
        camera.release()
        _camera = None
        return False, 0.0, None

    cv2 = _get_cv2()
    blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True)
    model.setInput(blob)

    try:
        output = model.forward()
    except cv2.error as exc:
        print(f"[AI 탐지 오류] 프레임을 분석하지 못했습니다: {exc}")
        return False, 0.0, frame

    best_confidence = 0.0
    for detection in output[0, 0, :, :]:
        class_id = int(detection[1])
        confidence = float(detection[2])

        # MobileNet SSD의 person 클래스(ID 1)만 침입 판단에 사용한다.
        if (
            class_id == config.PERSON_CLASS_ID
            and confidence >= config.PERSON_CONFIDENCE_THRESHOLD
        ):
            best_confidence = max(best_confidence, confidence)
            _draw_person_box(frame, detection, confidence)

    _show_frame_if_enabled(frame)

    if best_confidence > 0:
        return True, best_confidence, frame
    return False, 0.0, frame


def save_detection_image(frame, confidence):
    """선택적으로 person 탐지 결과 이미지를 captures 폴더에 저장한다."""
    if not config.SAVE_CAPTURE_IMAGES:
        return None
    if frame is None:
        if config.MOCK_MODE:
            print("[MOCK AI] 실제 프레임이 없으므로 탐지 이미지 저장을 건너뜁니다.")
        return None

    cv2 = _get_cv2()
    try:
        config.CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"[이미지 저장 오류] captures 폴더를 만들지 못했습니다: {exc}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = config.CAPTURE_DIR / f"person_{timestamp}_{confidence:.2f}.jpg"

    try:
        if cv2.imwrite(str(path), frame):
            print(f"[이미지 저장] {path}")
            return path
    except cv2.error as exc:
        print(f"[이미지 저장 오류] 탐지 이미지를 저장하지 못했습니다: {exc}")
        return None

    print(f"[이미지 저장 오류] 탐지 이미지를 저장하지 못했습니다: {path}")
    return None


def close_camera():
    """프로그램 종료 시 웹캠과 OpenCV 창을 정리한다."""
    global _camera
    if _camera is not None:
        _camera.release()
        _camera = None
    if _cv2 is not None:
        try:
            _cv2.destroyAllWindows()
        except _cv2.error:
            # GUI 기능이 없는 OpenCV 환경에서도 종료 정리는 계속 진행한다.
            pass
