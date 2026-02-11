from typing import TypedDict

class ChatState(TypedDict):
    user_message: str
    
    is_question_relevant: bool
    document: str
    ambiguity: bool