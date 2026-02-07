"""
Telegram Bot integration for sending purchase notifications.
"""
import os
import requests
from datetime import datetime

# Telegram configuration from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_TOPIC_ID = os.getenv("TELEGRAM_TOPIC_ID", "")  # For supergroup topics


def _get_telegram_config():
    return (
        os.getenv("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN),
        os.getenv("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID),
        os.getenv("TELEGRAM_TOPIC_ID", TELEGRAM_TOPIC_ID),
    )


def _add_topic_id(payload: dict, topic_id: str):
    if not topic_id:
        return
    try:
        payload["message_thread_id"] = int(topic_id)
    except ValueError:
        print("  [Telegram] Invalid TELEGRAM_TOPIC_ID, skipping topic threading.")


def send_purchase_notification(famcode: str, package_info: str, result: dict, msisdn: str = "") -> bool:
    """
    Send a purchase success notification to Telegram group/topic.
    
    Args:
        famcode: The family code of the purchased package
        package_info: Description of the package
        result: The purchase result dict
        msisdn: The phone number (optional, for display)
    
    Returns:
        True if sent successfully, False otherwise
    """
    telegram_bot_token, telegram_chat_id, telegram_topic_id = _get_telegram_config()
    if not telegram_bot_token or not telegram_chat_id:
        print("  [Telegram] Bot token or chat ID not configured, skipping notification.")
        return False
    
    try:
        # Format the message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = result.get("status", "UNKNOWN")
        
        # Build message text
        message = f"""🎉 <b>Purchase Success!</b>

📦 <b>Package:</b> {package_info}
📋 <b>Famcode:</b> <code>{famcode}</code>
📱 <b>MSISDN:</b> {msisdn if msisdn else "N/A"}
✅ <b>Status:</b> {status}
🕐 <b>Time:</b> {timestamp}

<i>— XL-CLI Auto Notification</i>"""

        # Prepare API request
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        # Add topic ID if configured (for supergroup forums)
        _add_topic_id(payload, telegram_topic_id)
        
        # Send request
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200 and response.json().get("ok"):
            print("  [Telegram] ✓ Notification sent successfully!")
            return True
        else:
            print(f"  [Telegram] ✗ Failed to send: {response.text}")
            return False
            
    except Exception as e:
        print(f"  [Telegram] ✗ Error sending notification: {e}")
        return False


def send_file_notification(file_path: str, caption: str = "") -> bool:
    """
    Send a file (document) to configured Telegram group/topic.
    """
    telegram_bot_token, telegram_chat_id, telegram_topic_id = _get_telegram_config()
    if not telegram_bot_token or not telegram_chat_id:
        print("  [Telegram] Bot token or chat ID not configured, skipping file notification.")
        return False

    if not os.path.exists(file_path):
        print(f"  [Telegram] File not found, skipping: {file_path}")
        return False

    try:
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
        payload = {
            "chat_id": telegram_chat_id,
        }
        if caption:
            payload["caption"] = caption

        _add_topic_id(payload, telegram_topic_id)

        with open(file_path, "rb") as f:
            files = {
                "document": (os.path.basename(file_path), f, "application/json")
            }
            response = requests.post(url, data=payload, files=files, timeout=30)

        if response.status_code == 200 and response.json().get("ok"):
            print(f"  [Telegram] ✓ File sent: {os.path.basename(file_path)}")
            return True

        print(f"  [Telegram] ✗ Failed to send file: {response.text}")
        return False
    except Exception as e:
        print(f"  [Telegram] ✗ Error sending file: {e}")
        return False


def test_connection() -> bool:
    """Test if the Telegram bot configuration is working."""
    telegram_bot_token, telegram_chat_id, _ = _get_telegram_config()
    if not telegram_bot_token or not telegram_chat_id:
        print("[Telegram] Bot token or chat ID not configured.")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{telegram_bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200 and response.json().get("ok"):
            bot_info = response.json().get("result", {})
            print(f"[Telegram] Connected as: @{bot_info.get('username', 'unknown')}")
            return True
        else:
            print(f"[Telegram] Connection failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"[Telegram] Connection error: {e}")
        return False
