# General
import json

# Classes
from core.models.state import ChatState

# Helpers
from core.utils.io import load_yaml_schema

# LangChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate


def build_intention_prompt(prompt_txt: str, intenciones: dict, answer_example: dict, user_message: str):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(prompt_txt),
        HumanMessagePromptTemplate.from_template("Mensaje de usuario:\n{user_message_placeholder}")
    ])

    prompt = prompt.invoke({
        "intenciones_schema": json.dumps(intenciones, indent=2, ensure_ascii=False),
        "ejemplo": json.dumps(answer_example, indent=2, ensure_ascii=False),
        "user_message_placeholder": user_message
    })

    return prompt

def build_classify_prompt(state: ChatState, _classify_base_prompt: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(_classify_base_prompt),
        HumanMessagePromptTemplate.from_template("Mensaje de usuario:\n{user_message_ph}")
    ])

    prompt = prompt.invoke({
        "temas": json.dumps(load_yaml_schema("topics.yaml")), # dict
        "tema_previo": state["topic_previous"],
        "memoria_conversacion": json.dumps(state["conversation_history"]), # list
        "contexto_rag": state["context"],
        "user_message_ph": state["user_message"],
    })

    return prompt


def build_generator_prompt(prompt_txt: str, user_message: str, contexto: str):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(prompt_txt),
        HumanMessagePromptTemplate.from_template("Mensaje de usuario:\n{user_message_placeholder}")
    ])

    prompt = prompt.invoke({
        "contexto": contexto,
        "user_message_placeholder": user_message
    })

    return prompt

def build_verifier_prompt(prompt_txt: str, generator_answer: str, contexto: str):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(prompt_txt),
        HumanMessagePromptTemplate.from_template("Respuesta a evaluar:\n{answer_placeholder}")
    ])

    prompt = prompt.invoke({
        "contexto": contexto,
        "answer_placeholder": generator_answer
    })

    return prompt

