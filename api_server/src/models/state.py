from typing import Optional, TypedDict, Required, NotRequired

class ChatState(TypedDict):
    # User
    user_message: Required[str|bytes]
    user_session_id: Required[int]
    user_message_format: Required[str]
    user_message_str: NotRequired[str] 

    # Intent
    intent_llm: NotRequired[str]
    intent_score: NotRequired[float]
    required_slots: NotRequired[dict[str, str]]

    # Topic
    topic_llm: NotRequired[str]
    topic_score: NotRequired[float]
    topic_ambiguous: NotRequired[bool]
    info_source: NotRequired[str]
    topic_previous: NotRequired[str]
    document_previous: NotRequired[str]
    chapter_previous: NotRequired[str]
    suggested_clarification: NotRequired[str]

    # Generation
    conversation_history: NotRequired[list[str]]
    document: NotRequired[str]
    chapter: NotRequired[str]
    context: NotRequired[str]
    generate_llm: NotRequired[str]

    # Timers
    start_timer_intent: NotRequired[float]
    start_timer_memory_read: NotRequired[float]
    start_timer_memory_update: NotRequired[float]
    start_timer_topic: NotRequired[float]
    start_timer_embedding: NotRequired[float]
    start_timer_llm_rag: NotRequired[float]
    start_timer_llm_generate: NotRequired[float]

    # Errors
    error: NotRequired[dict]   # value can be None but key must be present

    # REDIS
    redis_ttl: NotRequired[int]

    # Final answer
    final_answer: NotRequired[dict]