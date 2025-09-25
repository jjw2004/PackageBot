import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BotConfig:
    """Configuration class for the Discord bot"""
    
    # Bot settings
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    PREFIX = os.getenv('BOT_PREFIX', '!')
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Bot information
    BOT_NAME = "PackageBot"
    BOT_DESCRIPTION = "A Discord bot created with discord.py"
    BOT_VERSION = "1.0.0"
    
    # Colors (hex values)
    SUCCESS_COLOR = 0x00ff00
    ERROR_COLOR = 0xff0000
    INFO_COLOR = 0x3498db
    WARNING_COLOR = 0xffaa00
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        if not cls.TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN is required in .env file")
        return True