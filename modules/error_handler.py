import logging
import aiohttp
import traceback
import asyncio
from modules.helper import config


log = logging.getLogger(config.LOGGER_NAME)
webhook_url = config.WEBHOOK_URL


class ErrorHandler(logging.Handler):
    # Function called when an error is logged
    def emit(self, record: logging.LogRecord):
        # Only send the log if it is an error
        if record.levelno < logging.ERROR:
            return
        
        log.info("New error recieved")
        error_string = self.format(record)

        # If there is an exception, add the stack trace to the error message
        if record.exc_info:
            # This includes the stack trace in the error record
            exc_type, exc_value, exc_traceback = record.exc_info
            error_string += '\n' + ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        error_string = "```"  + error_string + "```"
        
        # Send the error to discord
        asyncio.create_task(self.send_error(error_string))
        
    # Send the error to discord using webhook
    async def send_error(self, error_string: str):
        log.info("Attempting to send to discord")
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json={"content": error_string}) as response:
                if response.status != 204:
                    log.error(f"Failed to send error to discord: {response.status}")
                    log.error(await response.text())
                    
                    return
                
                log.info("Logged error to discord")


# Set up the logger
logger = logging.getLogger("discord")
logger_python = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = ErrorHandler()
ch.setLevel(logging.ERROR)

logger.addHandler(ch)
log.addHandler(ch)
logger_python.addHandler(ch)