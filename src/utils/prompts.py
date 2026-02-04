import json
from langchain_core.prompts import (ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate)

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

def build_intention_prompt(prompt_txt: str, intenciones: dict, memory: dict, answer_example: dict, user_message: str):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(prompt_txt),
        HumanMessagePromptTemplate.from_template("Mensaje de usuario:\n{user_message_placeholder}")
    ])

    prompt = prompt.invoke({
        "intenciones_schema": json.dumps(intenciones, indent=2, ensure_ascii=False),
        "memoria": json.dumps(memory, indent=2, ensure_ascii=False),
        "ejemplo": json.dumps(answer_example, indent=2, ensure_ascii=False),
        "user_message_placeholder": user_message
    })

    return prompt