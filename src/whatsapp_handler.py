import logging
from pathlib import Path

import requests

import config

logger = logging.getLogger(__name__)


def verify_webhook(args: dict) -> tuple:
    """Handle Meta webhook GET verification.

    Returns (response_body, status_code).
    """
    mode = args.get("hub.mode")
    token = args.get("hub.verify_token")
    challenge = args.get("hub.challenge")

    if mode == "subscribe" and token == config.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return challenge, 200

    logger.warning("Webhook verification failed")
    return "Forbidden", 403


def process_webhook(payload: dict) -> dict | None:
    """Process incoming POST webhook from Meta.

    Returns dict with message info or None if not a relevant message.
    """
    try:
        entry = payload.get("entry", [])
        if not entry:
            return None

        changes = entry[0].get("changes", [])
        if not changes:
            return None

        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return None

        message = messages[0]
        phone = message.get("from", "")
        msg_type = message.get("type", "")

        result = {
            "phone": phone,
            "type": msg_type,
        }

        if msg_type == "image":
            media_id = message["image"]["id"]
            result["media_id"] = media_id
            caption = message["image"].get("caption", "")
            result["caption"] = caption
            logger.info(f"Image received from {phone}, media_id={media_id}")

        elif msg_type == "text":
            result["text"] = message["text"]["body"]
            logger.info(f"Text received from {phone}: {result['text']}")

        else:
            logger.info(f"Unsupported message type '{msg_type}' from {phone}")

        return result

    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing webhook payload: {e}")
        return None


def download_media(media_id: str) -> str | None:
    """Download media from Meta API and save to pending_receipts/.

    Returns the local file path or None on failure.
    """
    headers = {"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"}

    # Step 1: Get media URL
    url = f"https://graph.facebook.com/v22.0/{media_id}"
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        media_url = resp.json().get("url")
        if not media_url:
            logger.error(f"No URL in media response for {media_id}")
            return None
    except requests.RequestException as e:
        logger.error(f"Failed to get media URL for {media_id}: {e}")
        return None

    # Step 2: Download the file
    try:
        resp = requests.get(media_url, headers=headers, timeout=60)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to download media {media_id}: {e}")
        return None

    # Determine extension from content type
    content_type = resp.headers.get("Content-Type", "image/jpeg")
    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    ext = ext_map.get(content_type, ".jpg")

    file_path = config.PENDING_DIR / f"{media_id}{ext}"
    file_path.write_bytes(resp.content)
    logger.info(f"Media downloaded: {file_path}")
    return str(file_path)


def send_message(phone: str, text: str) -> bool:
    """Send a text message via WhatsApp Meta API.

    Returns True on success.
    """
    url = f"{config.WHATSAPP_API_URL}/messages"
    headers = {
        "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text},
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        logger.info(f"Message sent to {phone}")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send message to {phone}: {e}")
        return False
