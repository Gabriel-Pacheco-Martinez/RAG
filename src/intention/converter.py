from google import genai
from google.genai import types

class AudioConverter():
    def __init__(self, MODEL:str, API_KEY:str):
        self.model = MODEL
        self.client = genai.Client(api_key=API_KEY)

    def convert_audio_to_text(self, audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
        """
        Converts audio bytes to text using Gemini 2.5 multimodal.

        Text is significantly cheaper than audio. Google bills the Gemini API based on tokens. 
        While 1,000 characters of text might be ~250 tokens, 1 second of audio is roughly 25 to 32 tokens. 
        This means processing audio is always more "token-heavy" than processing plain text.
        """
        try:
            # Native SDK handles the bytes and prompt automatically
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    "Transcribe this audio exactly. Do not summarize.",
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
                ]
            )
            
            # Print the Price Test / Usage Report
            print(response.text)
            return response.text
            
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return None
        