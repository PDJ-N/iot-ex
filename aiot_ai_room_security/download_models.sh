#!/usr/bin/env bash
set -euo pipefail

# 호환용 스크립트입니다.
# 실제 다운로드 로직은 Python 표준 라이브러리만 사용하는 download_models.py에 있습니다.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${PROJECT_DIR}/download_models.py"
