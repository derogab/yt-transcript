<p align="center">
  <img src="./.github/assets/logo.png" width="140px" style="border-radius: 50%;">
</p>
<h1 align="center">YT-Transcript</h1>
<p align="center">A Dockerized Telegram bot that downloads YouTube videos as MP3 audio and transcribes them using OpenAI Whisper</p>
<p align="center">
   <a href="https://github.com/derogab/voicemail/actions/workflows/deploy.yml">
      <img src="https://github.com/derogab/voicemail/actions/workflows/deploy.yml/badge.svg">
   </a>
</p>

### Features

- 🤖 Telegram bot interface
- 🎵 Download YouTube videos as MP3 audio
- 📝 Transcribe audio using OpenAI Whisper
- 🔄 Automatic cleanup of temporary files
- 📱 Support for long transcriptions (split into multiple messages)
- 🐳 Docker containerized for easy deployment

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd yt-transcript
   ```

2. **Create environment file:**
   ```bash
   # Create .env file
   echo "TELEGRAM_TOKEN=your_telegram_bot_token_here" > .env
   echo "WHISPER_MODEL=base" >> .env
   ```

3. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_TOKEN` | Your Telegram bot token (required) | - |
| `WHISPER_MODEL` | Whisper model size (tiny, base, small, medium, large) | base |

### Manual Docker Build

```bash
# Build the image
docker build -t yt-transcript-bot .

# Run the container
docker run --env-file .env yt-transcript-bot
```

### Usage

1. Start the bot using Docker
2. Open your Telegram bot and send a YouTube URL
3. The bot will:
   - Download the video as MP3
   - Transcribe the audio using Whisper
   - Send you the transcription

### Supported YouTube URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/embed/VIDEO_ID`
- `https://youtube.com/v/VIDEO_ID`

### Bot Commands

- `/start` - Show welcome message and instructions
- `/help` - Show detailed help information

### Configuration

##### Whisper Models

You can change the Whisper model size by setting the `WHISPER_MODEL` environment variable:

- `tiny` - Fastest, least accurate
- `base` - Good balance (default)
- `small` - Better accuracy
- `medium` - High accuracy
- `large` - Best accuracy, slowest

##### Example .env file:
```env
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
WHISPER_MODEL=base
```

##### Docker Commands

```bash
# Start the bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Tip
If you like this project or directly benefit from it, please consider buying me a coffee:  
🔗 `bc1qd0qatgz8h62uvnr74utwncc6j5ckfz2v2g4lef`  
⚡️ `derogab@sats.mobi`  
💶 [Sponsor on GitHub](https://github.com/sponsors/derogab)

### Credits
_Voicemail_ is made with ♥  by [derogab](https://github.com/derogab) and it's released under the [MIT license](./LICENSE).