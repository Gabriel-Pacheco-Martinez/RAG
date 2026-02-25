# Google
from google import genai
from google.genai import types

# Exceptions
from src.models.exceptions import ConvertionError

# Configuration
from config.settings import GEMINI_MULTIMODAL_MODEL
from config.settings import GEMINI_API_KEY


def convert_audio_to_text(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """
    Converts audio bytes to text using Gemini 2.5 multimodal.

    Text is significantly cheaper than audio. Google bills the Gemini API based on tokens. 
    While 1,000 characters of text might be ~250 tokens, 1 second of audio is roughly 25 to 32 tokens. 
    This means processing audio is always more "token-heavy" than processing plain text.
    """
    try:
        model = GEMINI_MULTIMODAL_MODEL
        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model = model,
            contents=[
                "Transcribe this audio exactly. Do not summarize.",
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
            ]
        )
    except Exception as e:
        raise ConvertionError("Error convirtiendo audio a texto: " + str(e))

    return response.text

        