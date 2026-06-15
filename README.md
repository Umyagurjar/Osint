# 🌐 OSINT Reconnaissance Intelligence Telegram Bot

<p align="center">
  <img src="https://shields.io" alt="Python Version">
  <img src="https://shields.io" alt="Telegram API">
  <img src="https://shields.io" alt="Deployment Platform">
</p>

---

## ⚡ OSINT Bot By:

```text
██╗░░██╗███╗░░░███╗███████╗░██████╗██╗░░██╗  ░██████╗██╗███╗░░██╗░██████╗░██╗░░██╗
██║░░██║████╗░████║██╔════╝██╔════╝██║░░██║  ██╔════╝██║████╗░██║██╔════╝░██║░░██║
██║░░██║██╔████╔██║█████╗░░╚█████╗░███████║  ╚█████╗░██║██╔██╗██║██║░░██╗░███████║
██║░░██║██║╚██╔╝██║██╔══╝░░░╚═══██╗██╔══██║  ░╚═══██╗██║██║╚████║██║░░╚██╗██╔══██║
╚█████╔╝██║░╚═╝░██║███████╗██████╔╝██║░░██║  ██████╔╝██║██║░╚███║╚██████╔╝██║░░██║
░╚════╝░╚═╝░░░░░╚═╝╚══════╝╚═════╝░╚═╝░░╚═╝  ╚═════╝░╚═╝╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝

░██████╗░██╗░░██╗██████╗░░█████╗░░█████╗░██████╗░
██╔════╝░██║░░██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗
██║░░██╗░██║░░██║██████╔╝███████║███████║██████╔╝
██║░░╚██╗██║░░██║██╔══██╗██╔══██║██╔══██║██╔══██╗
╚██████╔╝╚█████╔╝██║░░██║██║░░██║██║░░██║██║░░██║
░╚═════╝░░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝
```

---

## ✨ Features & Capabilities

*   **📞 Advanced Phone Recon (`/phone`)**: Validates phone numbers globally, extracts carrier network infrastructure details (Jio, Airtel, etc.), geographic zone info, and cross-references them against public breach repositories for security tracking.
*   **🔍 Domain Lookup (`/domain`)**: Resolves target domains to underlying IP addresses and tracks active WHOIS registrar profiles and autonomous system numbers (ASN).
*   **📍 Precise IP Geolocation (`/ip`)**: Extracts geographical metrics including the hosting country, region, operational ISP, and mapping coordinates.
*   **👤 Username Footprint Scanner (`/user`)**: Audits major internet infrastructure networks (GitHub, Reddit, Twitter/X) to detect if a specific username matches existing active digital profiles.
*   **🔒 Channel Force Join Integration**: Restricts system utilization until users subscribe to your specified Telegram Channel.

---

## 🛠️ Project Structure

Your deployment repository requires the following structural file map:
*   `bot.py` — The core asynchronous execution script.
*   `requirements.txt` — Python external dependency stack.
*   `Dockerfile` — Docker container architecture template.
*   `.koyeb.yaml` — Koyeb cloud infrastructure configuration file.

---

## 🚀 Instant Deployment Guide (Koyeb)

### 1. Environment Variable Requirements
Before running the deployment runtime container, configure these keys in your **Koyeb Dashboard Environment Settings**:

| Variable Key | Value Context Example | Description |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | `728394...:AAH_xyz...` | Your HTTP API token from [@BotFather](https://t.me) |
| `CHANNEL_USERNAME` | `@YourChannelHandle` | The target channel username for force join access control |

### 2. Deployment Execution Steps
1. Push your clean folder configurations to an active **GitHub Repository**.
2. Connect your GitHub workspace directly to your **Koyeb Console Profile**.
3. Select **Worker Service Type** (Background Application).
4. Add the required Environment Variables listed above and trigger **Deploy**.

---

## 📖 Operational Telegram Commands

Once your background engine finishes compilation on Koyeb, open your Telegram bot and interface via the following command framework:

*   `/start` — Verifies channel join status and boots up the structural interface menu.
*   `/phone +91XXXXXXXXXX` — Scans international metadata profiles and compromised database indexes.
*   `/domain example.com` — Extracts IP configurations and organizational tracking records.
*   `/ip 8.8.8.8` — Tracks server geolocation positions and structural ISP data.
*   `/user target_handle` — Identifies social footprint registrations across networks.

---

## ⚠️ Legal & Security Disclaimer

This application framework is engineered strictly for educational analysis, personal digital hygiene tracking, and legal penetration testing architectures. Using these search query automations to target entities without explicitly authorized mutual consent is heavily bound to violation parameters regarding global privacy terms and regional law environments. The authors hold no legal accountability or compliance liabilities regarding any system misbehavior, exploitation, or data mishandling by third-party actors.
