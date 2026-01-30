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
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
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
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        # Add topic ID if configured (for supergroup forums)
        if TELEGRAM_TOPIC_ID:
            payload["message_thread_id"] = int(TELEGRAM_TOPIC_ID)
        
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


def test_connection() -> bool:
    """Test if the Telegram bot configuration is working."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] Bot token or chat ID not configured.")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
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
