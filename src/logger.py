import logging
from pathlib import Path
from config.settings import LOGS_PATH
from config.settings import LOGS_FILE

# Ensure log folder exists
Path(LOGS_PATH).mkdir(parents=True, exist_ok=True)

# Configure logging 
logging.basicConfig(
    filename=LOGS_FILE,
    encoding="utf-8",
    filemode="w",
    format="{asctime} - {levelname} - {name} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)