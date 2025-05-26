import os
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class MemeGenerator:
    def __init__(self, api_key=os.environ.get("GEMINI_API_KEY")):
        self.api_key = api_key

    def save_binary_file(self, file_name, data):
        with open(file_name, "wb") as f:
            f.write(data)
        print(f"File saved to: {file_name}")

    def generate_meme_text(self, prompt: str) -> str:
        client = genai.Client(api_key=self.api_key)

        model = "gemini-2.0-flash-lite"
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]
        generate_content_config = types.GenerateContentConfig(response_mime_type="text/plain")

        full_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                print(chunk.text, end="")  # Optional: print generated text
                full_text += chunk.text

        return full_text.strip()

    def generate_meme_image(self, meme_text: str):
        client = genai.Client(api_key=self.api_key)

        model = "gemini-2.0-flash-preview-image-generation"
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=meme_text)],
            )
        ]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            response_mime_type="text/plain",
        )

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates
                and chunk.candidates[0].content
                and chunk.candidates[0].content.parts
                and chunk.candidates[0].content.parts[0].inline_data
            ):
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                file_extension = mimetypes.guess_extension(inline_data.mime_type)
                # file_name = f"meme_output{file_extension}"
                # self.save_binary_file(file_name, inline_data.data)
                return inline_data.data, inline_data.mime_type
            elif chunk.text:
                print(chunk.text)
        return None, None


def main():
    user_prompt = input("Enter a meme idea (e.g., 'generate a cat meme'): ")
    print("\nGenerating meme text...")
    generator = MemeGenerator()
    meme_text = generator.generate_meme_text(user_prompt)

    print("\n\nGenerating meme image...")
    generator.generate_meme_image(meme_text)


if __name__ == "__main__":
    main()
