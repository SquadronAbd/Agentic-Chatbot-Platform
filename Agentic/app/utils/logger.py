from loguru import logger

logger.add(
    "logs/ai.log",
    rotation="10 MB",
    level="INFO"
)