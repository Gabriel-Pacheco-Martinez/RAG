from config.settings import PROMPTS_PATH

def load_prompt(file: str) -> str:
    with open(PROMPTS_PATH + file, "r", encoding="utf-8") as f:
        return f.read()