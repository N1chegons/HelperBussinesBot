import logging
import sys

def setup_logging_bot():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('bot.log')
        ],
        force=True
    )

def get_logger_bot(name):
    return logging.getLogger("telegram_bot")

setup_logging_bot()
