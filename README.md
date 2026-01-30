<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20Termux-green?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

<h1 align="center">🔧 XL-CLI</h1>

<p align="center">
  <strong>Advanced CLI Tool for Indonesian Mobile Service Provider</strong>
</p>

<p align="center">
  A powerful command-line interface for managing packages, purchases, and account operations with premium theming and Telegram integration.
</p>

---

## ✨ Features

| Feature                       | Description                                           |
| ----------------------------- | ----------------------------------------------------- |
| 🎨 **Premium Theme**          | Beautiful Cyan/Blue gradient UI with modern ASCII art |
| 📦 **Multi-Famcode Purchase** | Batch purchase from multiple family codes (max 20)    |
| 🔔 **Telegram Notifications** | Auto-send purchase results to Telegram group/topic    |
| 🔐 **Secure Auth**            | OTP-based authentication with token refresh           |
| 📊 **Transaction History**    | View and track all your transactions                  |
| ⭐ **Hot Packages**           | Quick access to trending/popular packages             |
| 🔖 **Bookmarks**              | Save your favorite packages for quick access          |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/TheFoolByte/XL-Cli.git
cd XL-Cli
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment**

```bash
cp .env.template .env
# Edit .env with your credentials
```

**4. Run the application**

```bash
python main.py
```

---

## 📱 Termux Installation

```bash
# Update & Upgrade
pkg update && pkg upgrade -y

# Install requirements
pkg install git python -y

# Clone & Setup
git clone https://github.com/TheFoolByte/XL-Cli.git
cd XL-Cli
bash setup.sh

# Run
python main.py
```

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.template` to `.env` and fill in the required values:

| Variable             | Description                                  |
| -------------------- | -------------------------------------------- |
| `BASE_API_URL`       | API base URL                                 |
| `API_KEY`            | Your API key                                 |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (optional)                |
| `TELEGRAM_CHAT_ID`   | Telegram chat/group ID (optional)            |
| `TELEGRAM_TOPIC_ID`  | Telegram topic ID for supergroups (optional) |

> 📢 Get environment variables from [Our Telegram Channel](https://t.me/TheBuddie)

---

## 🔔 Telegram Integration

Enable automatic notifications for successful purchases:

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Add the bot to your group/channel
3. Configure `.env` with your bot token and chat ID
4. For supergroups with topics, add the topic ID

---

## 📁 Project Structure

```
XL-Cli/
├── main.py              # Entry point
├── app/
│   ├── menus/           # UI menus and interactions
│   ├── client/          # API clients
│   └── service/         # Core services (auth, telegram, etc.)
├── results/             # Purchase results (auto-generated)
├── hot_data/            # Hot package configurations
└── .env                 # Environment configuration
```

---

## ⚠️ Disclaimer

> **Terms of Service**: By using this tool, the user agrees to comply with all applicable laws and regulations and to release the developer from any and all claims arising from its use.

---

## 📬 Contact

<p align="center">
  <a href="https://t.me/FoolByte"><img src="https://img.shields.io/badge/Telegram-@FoolByte-blue?style=for-the-badge&logo=telegram" alt="Telegram"></a>
  <a href="https://t.me/TheBuddie"><img src="https://img.shields.io/badge/Channel-@TheBuddie-blue?style=for-the-badge&logo=telegram" alt="Channel"></a>
</p>

---

<p align="center">
  Modified with ❤️ by <a href="https://t.me/FoolByte">TheFoolByte</a>
</p>
