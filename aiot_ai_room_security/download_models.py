"""OpenCV DNN MobileNet SSD 모델 파일을 준비한다.

이 프로젝트는 얼굴의 신원을 구분하는 얼굴인식(face recognition)이 아니라,
수업에서 사용한 객체검출 모델로 COCO class_id=1인 person 객체를 찾는다.

라즈베리파이 실행 명령:
    python3 download_models.py
"""

from __future__ import annotations

import shutil
import sys
import tarfile
import tempfile
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

WEIGHTS_PATH = MODEL_DIR / "frozen_inference_graph.pb"
CONFIG_PATH = MODEL_DIR / "ssd_mobilenet_v2_coco_2018_03_29.pbtxt"

# TensorFlow Object Detection Model Zoo의 원본 모델 아카이브이다.
WEIGHTS_ARCHIVE_URL = (
    "http://download.tensorflow.org/models/object_detection/"
    "ssd_mobilenet_v2_coco_2018_03_29.tar.gz"
)

# OpenCV DNN에서 TensorFlow 모델을 읽을 때 사용하는 설정 파일이다.
CONFIG_URL = (
    "https://raw.githubusercontent.com/opencv/opencv_extra/4.x/"
    "testdata/dnn/ssd_mobilenet_v2_coco_2018_03_29.pbtxt"
)

MIN_WEIGHTS_SIZE = 60_000_000
MIN_CONFIG_SIZE = 100_000


def _is_valid_file(path: Path, min_size: int) -> bool:
    """파일이 있고 크기가 충분하면 정상 파일로 판단한다."""
    return path.is_file() and path.stat().st_size >= min_size


def _download(url: str, destination: Path) -> None:
    """URL에서 파일을 내려받는다. 외부 라이브러리 없이 표준 라이브러리만 사용한다."""
    request = Request(url, headers={"User-Agent": "aiot-room-security"})
    destination.parent.mkdir(parents=True, exist_ok=True)

    with urlopen(request, timeout=60) as response, destination.open("wb") as output:
        total_size = int(response.headers.get("Content-Length") or 0)
        downloaded = 0
        next_report_mb = 10

        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break

            output.write(chunk)
            downloaded += len(chunk)
            downloaded_mb = downloaded // (1024 * 1024)

            if downloaded_mb >= next_report_mb:
                if total_size:
                    total_mb = total_size // (1024 * 1024)
                    print(f"  {downloaded_mb}MB / {total_mb}MB 다운로드 중...")
                else:
                    print(f"  {downloaded_mb}MB 다운로드 중...")
                next_report_mb += 10


def _prepare_weights() -> None:
    """TensorFlow 모델 압축 파일에서 frozen_inference_graph.pb만 꺼낸다."""
    if _is_valid_file(WEIGHTS_PATH, MIN_WEIGHTS_SIZE):
        print(f"[확인] 이미 있음: {WEIGHTS_PATH}")
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path = Path(temp_dir) / "ssd_mobilenet_v2_coco_2018_03_29.tar.gz"
        print("[1/2] TensorFlow MobileNet SSD 모델 다운로드 중...")
        _download(WEIGHTS_ARCHIVE_URL, archive_path)

        print("[1/2] frozen_inference_graph.pb 추출 중...")
        with tarfile.open(archive_path, "r:gz") as archive:
            member = next(
                (
                    item
                    for item in archive.getmembers()
                    if item.name.endswith("/frozen_inference_graph.pb")
                ),
                None,
            )

            if member is None:
                raise RuntimeError("압축 파일 안에서 frozen_inference_graph.pb를 찾지 못했습니다.")

            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError("frozen_inference_graph.pb를 압축 파일에서 읽지 못했습니다.")

            MODEL_DIR.mkdir(parents=True, exist_ok=True)
            with source, WEIGHTS_PATH.open("wb") as output:
                shutil.copyfileobj(source, output)


def _prepare_config() -> None:
    """OpenCV DNN 설정 파일을 내려받는다."""
    if _is_valid_file(CONFIG_PATH, MIN_CONFIG_SIZE):
        print(f"[확인] 이미 있음: {CONFIG_PATH}")
        return

    print("[2/2] OpenCV DNN pbtxt 설정 파일 다운로드 중...")
    _download(CONFIG_URL, CONFIG_PATH)


def _print_manual_copy_help() -> None:
    """인터넷 다운로드가 안 될 때 수업자료 파일을 직접 복사하는 방법을 안내한다."""
    print()
    print("[수동 준비 방법]")
    print("인터넷 다운로드가 안 되면 수업 때 사용한 모델 파일 2개를 직접 복사하세요.")
    print("프로젝트 폴더 기준으로 아래 위치에 들어가면 됩니다.")
    print()
    print("  aiot_ai_room_security/models/frozen_inference_graph.pb")
    print("  aiot_ai_room_security/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt")
    print()
    print("예시:")
    print("  mkdir -p models")
    print("  cp /모델파일이있는경로/frozen_inference_graph.pb models/")
    print("  cp /모델파일이있는경로/ssd_mobilenet_v2_coco_2018_03_29.pbtxt models/")


def main() -> int:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    try:
        _prepare_weights()
        _prepare_config()
    except (OSError, URLError, RuntimeError, tarfile.TarError) as exc:
        print(f"[오류] 모델 파일 준비 중 문제가 발생했습니다: {exc}")
        _print_manual_copy_help()
        return 1

    if not _is_valid_file(WEIGHTS_PATH, MIN_WEIGHTS_SIZE):
        print(f"[오류] {WEIGHTS_PATH.name} 파일이 없거나 크기가 너무 작습니다.")
        _print_manual_copy_help()
        return 1

    if not _is_valid_file(CONFIG_PATH, MIN_CONFIG_SIZE):
        print(f"[오류] {CONFIG_PATH.name} 파일이 없거나 크기가 너무 작습니다.")
        _print_manual_copy_help()
        return 1

    print()
    print("모델 파일 준비 완료:")
    print(f"  {WEIGHTS_PATH} ({WEIGHTS_PATH.stat().st_size / 1024 / 1024:.1f}MB)")
    print(f"  {CONFIG_PATH} ({CONFIG_PATH.stat().st_size / 1024:.1f}KB)")
    print()
    print("이제 OpenCV DNN person 객체검출을 실행할 수 있습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
