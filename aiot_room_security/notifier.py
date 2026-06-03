"""requests 라이브러리로 Telegram Bot API에 알림을 전송한다."""

import config


def send_telegram_message(message):
    """텔레그램 메시지를 보내고 성공 여부를 True/False로 반환한다."""
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print(
            "[텔레그램 건너뜀] TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 "
            f"비어 있습니다. 메시지: {message}"
        )
        return False

    try:
        import requests
    except ImportError:
        print("[텔레그램 오류] requests가 없습니다. 'pip install requests'를 실행하세요.")
        return False

    url = (
        "https://api.telegram.org/"
        f"bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    )
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:
        response = requests.post(
            url,
            data=payload,
            timeout=config.TELEGRAM_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        print("[텔레그램 전송 완료] 메시지를 전송했습니다.")
        return True
    except requests.RequestException as exc:
        # 인터넷 연결이 끊기거나 Telegram API 오류가 발생해도 감지 루프는 유지한다.
        print(f"[텔레그램 오류] 메시지를 전송하지 못했습니다: {exc}")
        return False
