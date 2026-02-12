from typing import TypedDict

class ChatState(TypedDict):
    # User message
    user_session_id: int
    user_message: str
    user_message_ambiguos: bool

    # Topic
    topic: str
    topic_previous: str
    topic_confidence: float
    is_follow_up: bool
    rewritten_query: str

    # Memory
    conversation_history: list[str]
    context: str

    # LLM
    llm_topic_response: str
    llm_clarify_response: str
    llm_query_response: str

    # Redis
    redis_ttl: int