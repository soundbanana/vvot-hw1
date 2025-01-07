from constants import MESSAGES

# Custom error class to handle errors
class ProcessingError(Exception):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details

class MessageResponse:
    """Represents a structured message response with a type and message content."""
    
    TEXT = "text"
    ERROR = "error"
    INFO = "info"
    
    def __init__(self, message: str, response_type: str):
        self.message = message
        self.response_type = response_type

    def is_error(self):
        return self.response_type == self.ERROR

    def is_info(self):
        return self.response_type == self.INFO

    def is_text(self):
        return self.response_type == self.TEXT
    

class CommandHandler:
    """Handles incoming commands."""
    
    def __init__(self, command, chat_id):
        self.command = command
        self.chat_id = chat_id

    def process(self) -> MessageResponse:
        """Processes the command and returns an appropriate response."""
        if self.command == "/start" or self.command == "/help":
            return MessageResponse(MESSAGES["start_help"], MessageResponse.INFO)
        else:
            raise ProcessingError(MESSAGES["unknown_command"])
