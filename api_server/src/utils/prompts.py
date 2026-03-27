# General
import json
from typing import Awaitable

# Classes
from src.models.state import ChatState
from langchain_core.prompt_values import PromptValue

# Helpers
from src.utils.io import load_yaml_schema
from src.utils.io import load_prompt
from src.utils.io import load_json_schema

# LangChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate

# Logging
import logging
logger = logging.getLogger('uvicorn.error')


def build_intention_prompt(user_message: str) -> PromptValue:
    # Load files
    base_prompt = load_prompt("intent_prompt.txt")
    answer_schema = load_json_schema("schema_respuestas.json")
    intenciones_schema = load_json_schema("schema_intenciones.json")

    # Build
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(base_prompt),
        HumanMessagePromptTemplate.from_template("Mensaje de usuario:\n{user_message_placeholder}")
    ])

    # Call
    prompt = prompt.invoke({
        "intenciones_schema": json.dumps(intenciones_schema, indent=2, ensure_ascii=False),
        "ejemplo": json.dumps(answer_schema, indent=2, ensure_ascii=False),
        "user_message_placeholder": user_message
    })

    return prompt

def build_topic_prompt(state: ChatState) -> PromptValue:
    # Load files
    base_prompt = load_prompt("topic_prompt.txt")

    # Build
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(base_prompt),
        HumanMessagePromptTemplate.from_template("Mensaje de usuario:\n{user_message}")
    ])

    # Call
    prompt = prompt.invoke({
        "temas": json.dumps(load_yaml_schema("topics.yaml")), # dict
        "documento_previo": state.get("topic_previous"),
        "subdocumento_previo": state.get("chapter_previous"),
        "memoria_conversacion": json.dumps(state.get("conversation_history")), # list
        "user_message": state.get("user_message_str"),
    })
    return prompt

def build_reranking_prompt(points_str: str, query: str) -> PromptValue:
    # Load files
    base_prompt = load_prompt("rerank_prompt.txt")

    # Build
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(base_prompt),
        HumanMessagePromptTemplate.from_template("Por favor haz el rerank de los puntos.")
    ])

    # Call
    prompt = prompt.invoke({
        "query": query,
        "chunks": points_str
    })

    return prompt

def build_generator_prompt(state: ChatState) -> PromptValue:
    # Load files
    base_prompt = load_prompt("generate_prompt.txt")

    # Build
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(base_prompt),
        HumanMessagePromptTemplate.from_template("Mensaje de usuario:\n{user_message_placeholder}")
    ])

    # Call
    prompt = prompt.invoke({
        "contexto": state.get("context"),
        "user_message_placeholder": state["user_message"]
    })

    return prompt

