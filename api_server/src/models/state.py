from typing import Optional, TypedDict, Required, NotRequired

class ChatState(TypedDict):
    # User message
    user_message: Required[str | bytes]
    user_session_id: Required[int]
    user_message_str: Required[str] 
    user_message_format: Required[str]
    user_message_ambiguous: Required[bool]

    # Intent
    


    # Timers
    start_timer_memory_read: Required[float]
    start_timer_memory_update: Required[float]
    start_timer_intent: Required[float]
    start_timer_topic: Required[float]
    start_timer_llm_rag: Required[float]
    start_timer_llm_generate: Required[float]

    # Errors
    error: Optional[dict]   # value can be None but key must be present

    # User message


    # Intent
    intent_confidence: float
    slots: dict[str, str]

    # Intencion
    

    # Topic
    topic: str
    topic_previous: str
    topic_confidence: float
    is_follow_up: bool
    rewritten_query: str
    document: str
    chapter: str

    # Retrieval
    retreival_confidence: float
    info_source: str

    # LLM
    llm_intent_response: str
    llm_query_response: str

    # Redis
    redis_ttl: int

    # Memory
    context: str
    conversation_history: list[str]
    
    # Final answer
    final_answer: dict