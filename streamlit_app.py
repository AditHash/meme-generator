import streamlit as st
import os
import io
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class MemeGenerator:
    def __init__(self, api_key, text_model="gemini-2.0-flash-lite", image_model="gemini-2.0-flash-preview-image-generation"):
        self.api_key = api_key
        self.text_model = text_model
        self.image_model = image_model

    def generate_meme_text(self, prompt: str) -> str:
        client = genai.Client(api_key=self.api_key)

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]
        generate_content_config = types.GenerateContentConfig(response_mime_type="text/plain")

        full_text = ""
        for chunk in client.models.generate_content_stream(
            model=self.text_model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                full_text += chunk.text

        return full_text.strip()

    def generate_meme_image(self, meme_text: str):
        client = genai.Client(api_key=self.api_key)

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
            model=self.image_model,
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
                return inline_data.data, inline_data.mime_type
            elif chunk.text:
                print(chunk.text)
        return None, None


def main():
    st.title("Meme Generator")

    # Sidebar for API key and parameters
    st.sidebar.header("Configuration")
    user_api_key = st.sidebar.text_input("Enter your GEMINI_API_KEY", type="password")
    text_model = st.sidebar.text_input("Text Model", value="gemini-2.0-flash-lite")
    image_model = st.sidebar.text_input("Image Model", value="gemini-2.0-flash-preview-image-generation")

    st.sidebar.markdown("---")
    st.sidebar.info("You can get your API key from Google AI Studio.")

    # Log collector
    logs = []

    if not user_api_key:
        st.warning("Please enter your GEMINI_API_KEY in the sidebar to use the app.")
        st.stop()

    user_prompt = st.text_input("Enter a meme idea (e.g., 'generate a cat meme'):", "")

    if user_prompt:
        generator = MemeGenerator(api_key=user_api_key, text_model=text_model, image_model=image_model)
        with st.spinner("Generating meme text..."):
            meme_text = generator.generate_meme_text(user_prompt)
            logs.append(f"Generated meme text: {meme_text}")

        with st.spinner("Generating meme image..."):
            image_data, mime_type = generator.generate_meme_image(meme_text)
            logs.append(f"Image data: {'present' if image_data else 'missing'}, mime_type: {mime_type}")

        if image_data and mime_type:
            st.image(image_data, caption="Generated Meme")
            file_extension = mimetypes.guess_extension(mime_type) or '.png'
            st.download_button(
                label="Download Meme",
                data=image_data,
                file_name=f"generated_meme{file_extension}",
                mime=mime_type
            )
        else:
            st.error("Failed to generate meme image.")
            logs.append("Failed to generate meme image.")

    # Show logs in an expander
    with st.expander("Show logs / debug output"):
        for log in logs:
            st.write(log)


if __name__ == "__main__":
    main()
