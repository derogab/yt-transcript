#!/bin/bash

echo "🚀 Deploying YouTube Transcript Bot"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
  echo "📝 Creating .env file..."
  cat > .env << EOF
# Telegram Bot Token (get from @BotFather)
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Whisper model size (tiny, base, small, medium, large)
WHISPER_MODEL=base
EOF
  echo "✅ .env file created"
  echo "⚠️  Please edit .env file and add your Telegram bot token"
  echo "   Get your token from: https://t.me/BotFather"
  exit 1
fi

# Check if TELEGRAM_TOKEN is set
if grep -q "your_telegram_bot_token_here" .env; then
  echo "❌ Please edit .env file and add your Telegram bot token"
  echo "   Get your token from: https://t.me/BotFather"
  exit 1
fi

echo "🐳 Starting bot with Docker Compose..."
docker compose up -d

echo "✅ Bot deployed successfully!"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker compose logs -f"
echo "  Stop bot:  docker compose down"
echo "  Restart:   docker compose restart"
echo ""
echo "🤖 Send a YouTube URL to your bot to test it!" 