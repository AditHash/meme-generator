# pip install google-genai python-dotenv

import os
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")


def generate_meme_text(prompt: str) -> str:
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

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


def generate_meme_image(meme_text: str):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

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
            file_name = f"meme_output{file_extension}"
            save_binary_file(file_name, inline_data.data)
            return
        elif chunk.text:
            print(chunk.text)


def main():
    user_prompt = input("Enter a meme idea (e.g., 'generate a cat meme'): ")
    print("\nGenerating meme text...")
    meme_text = generate_meme_text(user_prompt)

    print("\n\nGenerating meme image...")
    generate_meme_image(meme_text)


if __name__ == "__main__":
    main()
