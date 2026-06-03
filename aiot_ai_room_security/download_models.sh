#!/usr/bin/env bash
set -euo pipefail

# OpenCV DNN MobileNet SSD 모델 파일을 내려받는 스크립트입니다.
# 라즈베리파이에서 프로젝트 폴더 안에서 아래 명령으로 실행합니다.
#   bash download_models.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="${PROJECT_DIR}/models"

WEIGHTS_URL="https://raw.githubusercontent.com/moonchuljang/OpencvDnn/master/models/frozen_inference_graph.pb"
CONFIG_URL="https://raw.githubusercontent.com/moonchuljang/OpencvDnn/master/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt"

mkdir -p "${MODEL_DIR}"

echo "[1/2] frozen_inference_graph.pb 다운로드 중..."
curl -L --fail --progress-bar "${WEIGHTS_URL}" -o "${MODEL_DIR}/frozen_inference_graph.pb"

echo "[2/2] ssd_mobilenet_v2_coco_2018_03_29.pbtxt 다운로드 중..."
curl -L --fail --progress-bar "${CONFIG_URL}" -o "${MODEL_DIR}/ssd_mobilenet_v2_coco_2018_03_29.pbtxt"

echo
echo "모델 파일 준비 완료:"
ls -lh "${MODEL_DIR}"

WEIGHTS_SIZE="$(wc -c < "${MODEL_DIR}/frozen_inference_graph.pb")"
CONFIG_SIZE="$(wc -c < "${MODEL_DIR}/ssd_mobilenet_v2_coco_2018_03_29.pbtxt")"

if [ "${WEIGHTS_SIZE}" -lt 60000000 ]; then
  echo "오류: frozen_inference_graph.pb 파일 크기가 너무 작습니다. 다운로드가 실패했을 수 있습니다."
  exit 1
fi

if [ "${CONFIG_SIZE}" -lt 100000 ]; then
  echo "오류: ssd_mobilenet_v2_coco_2018_03_29.pbtxt 파일 크기가 너무 작습니다. 다운로드가 실패했을 수 있습니다."
  exit 1
fi

echo "정상 확인: 이제 python main.py를 실행할 수 있습니다."
