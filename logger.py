import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("gmailProcesses.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)