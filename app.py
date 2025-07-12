import os
import logging
import tempfile
import re
from typing import Optional
from pathlib import Path

import yt_dlp
import whisper
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class YouTubeTranscriberBot:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        if not self.telegram_token:
            raise ValueError("TELEGRAM_TOKEN environment variable is required")
        
        # Initialize Whisper model
        model_size = os.getenv('WHISPER_MODEL', 'base')
        logger.info(f"Loading Whisper model ({model_size})...")
        self.whisper_model = whisper.load_model(model_size)
        logger.info("Whisper model loaded successfully")
        
        # YouTube URL patterns
        self.youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+'
        ]
    
    def is_youtube_url(self, text: str) -> bool:
        """Check if the text contains a YouTube URL."""
        for pattern in self.youtube_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def extract_youtube_url(self, text: str) -> Optional[str]:
        """Extract YouTube URL from text."""
        for pattern in self.youtube_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    async def download_youtube_audio(self, url: str) -> Optional[tuple]:
        """Download YouTube video as MP3."""
        try:
            # Create temporary directory for downloads
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, "%(title)s.%(ext)s")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
            }
            
            logger.info(f"Downloading audio from: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Unknown')
                
                # Download the audio
                ydl.download([url])
                
                # Find the downloaded file
                downloaded_files = list(Path(temp_dir).glob("*.mp3"))
                if downloaded_files:
                    audio_file = str(downloaded_files[0])
                    logger.info(f"Successfully downloaded: {video_title}")
                    return audio_file, video_title
                else:
                    logger.error("No audio file found after download")
                    return None, None
                    
        except Exception as e:
            logger.error(f"Error downloading YouTube audio: {e}")
            return None, None
    
    async def transcribe_audio(self, audio_file: str) -> Optional[str]:
        """Transcribe audio file using OpenAI Whisper."""
        try:
            logger.info(f"Transcribing audio file: {audio_file}")
            
            # Transcribe the audio
            result = self.whisper_model.transcribe(audio_file)
            transcription = result["text"]
            
            logger.info("Transcription completed successfully")
            return transcription
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def cleanup_temp_files(self, audio_file: str):
        """Clean up temporary files."""
        try:
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
                temp_dir = os.path.dirname(audio_file)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
                logger.info("Temporary files cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = """
🤖 Welcome to YouTube Transcript Bot!

I can help you transcribe YouTube videos. Here's how to use me:

1. Send me a YouTube link
2. I'll download the audio and transcribe it
3. I'll send you back the transcription

Commands:
/start - Show this help message
/help - Show help information

Just paste a YouTube URL and I'll get started!
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
📖 How to use this bot:

1. Copy a YouTube video URL
2. Paste it in a message to me
3. Wait for me to download and transcribe the audio
4. I'll send you the transcription

Supported YouTube URL formats:
• https://www.youtube.com/watch?v=VIDEO_ID
• https://youtu.be/VIDEO_ID
• https://youtube.com/embed/VIDEO_ID

Note: The transcription process may take a few minutes depending on the video length.
        """
        await update.message.reply_text(help_message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        message = update.message
        text = message.text.strip()
        
        # Check if message contains a YouTube URL
        if not self.is_youtube_url(text):
            await message.reply_text(
                "Please send me a valid YouTube URL. Use /help for more information."
            )
            return
        
        # Extract YouTube URL
        youtube_url = self.extract_youtube_url(text)
        if not youtube_url:
            await message.reply_text("I couldn't extract a valid YouTube URL from your message.")
            return
        
        # Send initial response
        status_message = await message.reply_text("🎵 Downloading audio from YouTube...")
        
        try:
            # Download YouTube audio
            result = await self.download_youtube_audio(youtube_url)
            if not result or result[0] is None:
                await status_message.edit_text("❌ Failed to download the YouTube video. Please check the URL and try again.")
                return
            
            audio_file, video_title = result
            
            # Update status
            await status_message.edit_text(f"📝 Transcribing audio for: {video_title[:50]}...")
            
            # Transcribe audio
            transcription = await self.transcribe_audio(audio_file)
            if not transcription:
                await status_message.edit_text("❌ Failed to transcribe the audio. Please try again.")
                return
            
            # Clean up temporary files
            await self.cleanup_temp_files(audio_file)
            
            # Send transcription
            max_length = 4096
            if len(transcription) > max_length:
                # Split long transcriptions
                chunks = [transcription[i:i+max_length] for i in range(0, len(transcription), max_length)]
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        await status_message.edit_text(f"📄 Transcription (Part {i+1}/{len(chunks)}):\n\n{chunk}")
                    else:
                        await message.reply_text(f"📄 Transcription (Part {i+1}/{len(chunks)}):\n\n{chunk}")
            else:
                await status_message.edit_text(f"📄 Transcription:\n\n{transcription}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await status_message.edit_text("❌ An error occurred while processing your request. Please try again.")
    
    def run(self):
        """Run the bot."""
        # Create application
        application = Application.builder().token(self.telegram_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start the bot
        logger.info("Starting YouTube Transcriber Bot...")
        try:
            application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise

def main():
    """Main function."""
    try:
        bot = YouTubeTranscriberBot()
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        exit(1)

if __name__ == "__main__":
    main()
