import logging
import os

import requests

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def _get_sender() -> str:
    address = (os.getenv("EMAIL_FROM_ADDRESS") or "").strip()
    name = (os.getenv("EMAIL_FROM_NAME") or "Smart Library App").strip()
    if not address:
        return f"{name} <no-reply@example.com>"
    return f"{name} <{address}>"


def send_email(*, to_email: str, subject: str, text: str, html: str | None = None) -> bool:
    resend_api_key = (os.getenv("RESEND_API_KEY") or "").strip()
    reply_to = (os.getenv("EMAIL_REPLY_TO") or "").strip() or None

    if not resend_api_key:
        logger.warning("RESEND_API_KEY not configured; email delivery is running in console fallback mode")
        logger.info("Email fallback to=%s subject=%s\n%s", to_email, subject, text)
        return True

    payload: dict[str, object] = {
        "from": _get_sender(),
        "to": [to_email],
        "subject": subject,
        "text": text,
    }
    if html:
        payload["html"] = html
    if reply_to:
        payload["reply_to"] = reply_to

    try:
        response = requests.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {resend_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
    except requests.RequestException:
        logger.exception("Failed to send email via Resend")
        return False

    if response.status_code >= 400:
        logger.error("Resend email failed status=%s body=%s", response.status_code, response.text)
        return False

    return True
