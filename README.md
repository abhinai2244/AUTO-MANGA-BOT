# 🎌 Manga Downloader & Uploader Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Pyrogram-v2-yellow?style=for-the-badge&logo=telegram">
  <img src="https://img.shields.io/badge/MongoDB-Database-green?style=for-the-badge&logo=mongodb">
</p>

An advanced Telegram bot by **RexBots** designed to automate manga management. This bot supports downloading from multiple sources, auto-uploading to channels, PDF/CBZ generation, and advanced customization options.

## 🚀 Features

*   **Multi-Source Support**: Download from MangaDex, MangaForest, Mangakakalot, AllManga, and WebCentral.
*   **Auto-Upload**: Automatically upload new chapters to your Telegram channel.
*   **Format Conversion**: Convert manga chapters to high-quality PDF or CBZ files.
*   **Smart Search**: Search across multiple sources and download specific chapters or ranges.
*   **Advanced Customization**:
    *   **Thumbnails**: Set custom covers for your files.
    *   **Watermarks**: Protect your content with customizable watermarks.
    *   **Captions & Banners**: Personalize your posts with custom text and images.
*   **Interactive Control Panel**: 
    *   **Easy Configuration**: No need to remember complex commands! All settings (Channels, Media, Watermarks, File Formats, etc.) can be easily configured using the interactive **Settings** buttons in the bot.
    *   Simply start the bot and click **⚙️ Settings** to access the full control panel.
*   **Admin Tools**: Broadcast messages, manage admins, and force subscribe.
*   **Persistent Storage**: Uses MongoDB to store user data and settings.

## 🛠 Deployment

### Prerequisites

*   Python 3.10+
*   MongoDB Database
*   Telegram API ID and Hash
*   Bot Token

### Environment Variables

To run the bot, you need to set the following environment variables:

| Variable | Description |
| :--- | :--- |
| `BOT_TOKEN` | Your Telegram Bot Token from @BotFather |
| `API_ID` | Your Telegram API ID from my.telegram.org |
| `API_HASH` | Your Telegram API Hash from my.telegram.org |
| `USER_ID` | Your Telegram User ID (Owner) |
| `DB_URL` | Your MongoDB Connection String |
| `DB_NAME` | Database Name (default: `rex_auto_manga1`) |
| `CHECK_INTERVAL` | Auto-update check interval in seconds (default: `300`) |
| `MAX_CHAPTERS` | Max chapters to process per check (default: `5`) |
| `PORT` | Web server port (default: `8080`) |

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/abhinai2244/MANGA-BOT.git
    cd MANGA-BOT
    ```

2.  **Install dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```

3.  **Run the bot:**
    ```bash
    python3 Bot.py
    ```

### Docker

```bash
docker build -t rexbots-manga-bot -f Docker .
docker run -d --env-file .env rexbots-manga-bot
```

## 🤝 Contributors

A huge thanks to the developers who made this project possible:

<div align="center">

| [**Abhi**](https://github.com/abhinai2244) | [**Abhinav**](https://github.com/) | [**Master**]() |
| :---: | :---: | :---: | :---: |
| Owner | Developer | Developer |

</div>

## 📞 Support

For queries, feature requests, or bug reports, join our official channel:

<div align="center">
  <a href="https://t.me/akaza7902">
    <img src="https://img.shields.io/badge/RexBots-Official%20Channel-blue?style=for-the-badge&logo=telegram">
  </a>
</div>
