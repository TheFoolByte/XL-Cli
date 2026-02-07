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
  A command-line interface for account operations, package discovery, purchase automation,
  decoy management, and Telegram reporting.
</p>

---

## ✨ Features

| Feature | Description |
| --- | --- |
| 🎨 **Premium Theme** | Cyan/Blue CLI theme with styled menus and ASCII logo |
| 📦 **Multi-Famcode Purchase** | Batch purchase from multiple family codes (max 20) |
| 🧭 **Catalog Tools** | Export package catalog + generate decoy templates from results |
| 🧪 **Decoy Generator** | Build decoy JSON from catalog options with filtering |
| 🤖 **Auto Decoy Mapping** | Auto-map decoy output to operational files by active subscription type |
| 🔔 **Telegram Integration** | Auto-send success messages and JSON result files to Telegram group/topic |
| 🔐 **Secure Auth** | OTP-based authentication with token refresh |
| 📊 **Transaction History** | View and track transactions |
| ⭐ **Hot Packages** | Quick access to HOT/HOT-2 flows |
| 🔖 **Bookmarks** | Save favorite packages for quick access |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

**1. Clone repository**

```bash
git clone https://github.com/TheFoolByte/XL-Cli.git
cd XL-Cli
```

**2. Install dependencies (recommended with venv)**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If your environment uses `python` command directly:

```bash
pip install -r requirements.txt
```

**3. Configure environment**

```bash
cp .env.template .env
# Edit .env with your credentials/config
```

**4. Run app**

```bash
python3 main.py
```

---

## 📱 Termux Installation

```bash
# Update & upgrade
pkg update && pkg upgrade -y

# Install requirements
pkg install git python -y

# Clone & setup
git clone https://github.com/TheFoolByte/XL-Cli.git
cd XL-Cli
bash setup.sh

# Run
python main.py
```

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.template` to `.env` and fill values.

| Variable | Description |
| --- | --- |
| `BASE_API_URL` | API base URL |
| `BASE_CIAM_URL` | CIAM base URL |
| `BASIC_AUTH` | Base auth header payload |
| `UA` | User-Agent used by requests |
| `API_KEY` | API key |
| `ENCRYPTED_FIELD_KEY` | Encryption field key |
| `XDATA_KEY` | XData key |
| `AX_API_SIG_KEY` | API signature key |
| `X_API_BASE_SECRET` | Base secret |
| `CIRCLE_MSISDN_KEY` | Circle key |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (optional) |
| `TELEGRAM_CHAT_ID` | Telegram chat/group ID (optional) |
| `TELEGRAM_TOPIC_ID` | Telegram topic ID for supergroups/forums (optional) |

> 📢 Get environment variables from [Our Telegram Channel](https://t.me/TheBuddie)

---

## 🧭 Main Menus

### Menu Utama

- Login/Ganti akun
- Lihat paket saya
- Beli Paket HOT / HOT-2
- Beli by option code / family code
- Loop purchase by family code
- Riwayat transaksi
- Notifikasi, Bookmark, Opsi Selanjutnya

### Opsi Selanjutnya (Menu Kedua)

- Multi-FamCode Purchase
- Special Offers
- **Catalog Tools**
- Family Plan / Circle / Store Segments / Store Family List / Store Packages / Redeemables

---

## 🧪 Catalog Tools

### 1) Export Package Catalog

Export dari endpoint aktif ke file JSON di folder `results/`.

Output mencakup:

- `family_list_snapshot`
- `families` (family, variant, option, order, price, validity)
- `failed_families`
- `store_search_snapshot` (opsional)
- `segments_snapshot` (opsional)
- metadata export (subs_type, enterprise flag, totals)

Contoh output file:

- `results/catalog-prepaid-retail-20260207-225607.json`

### 2) Generate Decoy Template

Generate decoy dari file catalog:

1. Pilih file catalog
2. Filter keyword (opsional)
3. Pilih opsi paket
4. Pilih payment type (`balance` / `qris` / `qris0`)
5. Set `migration_type` (opsional)
6. Set `price override` (opsional)
7. Tulis ke file decoy

---

## 🤖 Auto Decoy Mapping

Saat generate decoy, mode output default adalah **Auto by active subscription type**.

Mapping profile:

- `PREPAID` -> `default`
- `PRIOHYBRID` -> `priohybrid`
- `PRIORITAS` -> `priopascabayar`
- `GO` -> `go`
- unknown -> `default`

Mapping ke file operasional:

| Auto Profile | balance | qris | qris0 |
| --- | --- | --- | --- |
| `default` | `decoy_data/decoy-default-balance.json` | `decoy_data/decoy-default-qris.json` | `decoy_data/decoy-default-qris0.json` |
| `prio` | `decoy_data/decoy-prio-balance.json` | `decoy_data/decoy-prio-qris.json` | `decoy_data/decoy-prio-qris0.json` |
| `priohybrid` | `decoy_data/decoy-priohybrid-balance.json` | `decoy_data/decoy-prio-qris.json` | `decoy_data/decoy-prio-qris0.json` |
| `priopascabayar` | `decoy_data/decoy-priopascabayar-balance.json` | `decoy_data/decoy-prio-qris.json` | `decoy_data/decoy-prio-qris0.json` |
| `go` | `decoy_data/decoy-priopascabayar-balance.json` | `decoy_data/decoy-prio-qris.json` | `decoy_data/decoy-prio-qris0.json` |

You can still switch to custom output path if needed.

---

## 🔔 Telegram Integration

Telegram integration now supports:

- Purchase success text notifications
- Catalog export JSON file uploads (`results/catalog-*.json`)

Setup:

1. Create bot via [@BotFather](https://t.me/BotFather)
2. Add bot to target group/channel
3. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`
4. If using supergroup topics/forum, set `TELEGRAM_TOPIC_ID`
5. Ensure bot has permission to send messages/documents

---

## 📁 Project Structure

```text
XL-Cli/
├── main.py
├── app/
│   ├── client/                     # API clients
│   ├── menus/
│   │   ├── purchase.py             # Multi-famcode + purchase flow
│   │   └── catalog_export.py       # Catalog tools menu
│   └── service/
│       ├── auth.py
│       ├── decoy.py
│       ├── catalog_export.py       # Catalog exporter service
│       ├── decoy_template.py       # Decoy template generator + auto mapping
│       └── telegram_bot.py         # Telegram text/file notifications
├── decoy_data/                     # Decoy configuration JSON files
├── hot_data/                       # HOT/Special Offers configuration
├── results/                        # Generated purchase/catalog results
├── refresh-tokens.json
└── .env
```

---

## ⚠️ Notes

- For PREPAID accounts, export usually works best with `Subs type = PREPAID` and `is_enterprise = n`.
- If `Failed` count is high during export, try adjusting `subs_type` and enterprise mode.
- On Linux/macOS, use `python3` command if `python` is not available.

---

## ⚠️ Disclaimer

> **Terms of Service**: By using this tool, users are responsible for complying with applicable laws, provider policies, and platform terms.

---

## 📬 Contact

<p align="center">
  <a href="https://t.me/FoolByte"><img src="https://img.shields.io/badge/Telegram-@FoolByte-blue?style=for-the-badge&logo=telegram" alt="Telegram"></a>
  <a href="https://t.me/TheBuddie"><img src="https://img.shields.io/badge/Channel-@TheBuddie-blue?style=for-the-badge&logo=telegram" alt="Channel"></a>
</p>

---

<p align="center">
  Modified by <a href="https://t.me/FoolByte">TheFoolByte</a>
</p>
