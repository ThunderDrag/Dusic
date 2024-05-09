import logging

logger = logging.getLogger("Dusic")
logger.setLevel(logging.INFO)

# Create a file handler for outputting log messages to a file
handler = logging.FileHandler("app.log")

# Set the level of the file handler
handler.setLevel(logging.DEBUG)

# Create a console handler for outputting log messages to the console
console_handler = logging.StreamHandler()

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Add formatter to the handlers
handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(handler)
logger.addHandler(console_handler)
