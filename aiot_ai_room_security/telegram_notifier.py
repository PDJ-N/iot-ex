"""Telegram Bot API로 메시지와 사진을 전송한다."""

from pathlib import Path

import config


def _telegram_ready():
    """텔레그램 전송에 필요한 token과 chat_id가 있는지 확인한다."""
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("[텔레그램 건너뜀] TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 비어 있습니다.")
        return False
    return True


def send_message(text):
    """텍스트 메시지를 텔레그램으로 전송한다."""
    if not _telegram_ready():
        print(f"[콘솔 메시지] {text}")
        return False

    try:
        import requests
    except ImportError:
        print("[텔레그램 오류] requests가 없습니다. 'pip install requests'를 실행하세요.")
        return False

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": text,
    }

    try:
        response = requests.post(
            url,
            data=payload,
            timeout=config.TELEGRAM_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        print("[텔레그램] 메시지 전송 완료")
        return True
    except requests.RequestException as exc:
        print(f"[텔레그램 오류] 메시지 전송 실패: {exc}")
        return False


def send_photo(photo_path, caption=""):
    """사진 파일을 텔레그램으로 전송한다."""
    if not _telegram_ready():
        print(f"[텔레그램 사진 건너뜀] 전송할 사진: {photo_path}")
        return False

    if not photo_path:
        print("[텔레그램 사진 건너뜀] 저장된 사진 경로가 없습니다.")
        return False

    path = Path(photo_path)
    if not path.is_file():
        print(f"[텔레그램 사진 오류] 사진 파일이 없습니다: {path}")
        return False

    try:
        import requests
    except ImportError:
        print("[텔레그램 오류] requests가 없습니다. 'pip install requests'를 실행하세요.")
        return False

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendPhoto"
    data = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "caption": caption,
    }

    try:
        with path.open("rb") as photo_file:
            response = requests.post(
                url,
                data=data,
                files={"photo": photo_file},
                timeout=config.TELEGRAM_REQUEST_TIMEOUT_SECONDS,
            )
        response.raise_for_status()
        print("[텔레그램] 사진 전송 완료")
        return True
    except requests.RequestException as exc:
        print(f"[텔레그램 오류] 사진 전송 실패: {exc}")
        return False
    except OSError as exc:
        print(f"[텔레그램 사진 오류] 사진 파일을 읽지 못했습니다: {exc}")
        return False
