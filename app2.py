import streamlit as st
import openai
import os
import requests
import tempfile
from dotenv import load_dotenv

# Set your OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

# Initialize session state for the story if not already set
if "story" not in st.session_state:
    st.session_state.story = None

# Function to generate a story using GPT-4
def generate_story(prompt, max_tokens):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a creative and dynamic storyteller designed to help parents and children co-create engaging, educational stories. "
                    "Your role is to generate interactive narratives based on user inputs and to be responsive to mid-story modifications.\n\n"
                    "Key Instructions:\n\n"
                    "Input Gathering:\n"
                    "Subject & Characters: Use the provided main subject (e.g., a monkey, princess, robot) as the story’s protagonist.\n\n"
                    "Theme & Lesson: Incorporate the chosen theme (such as anti-bullying, confidence, kindness, or adventure) to craft a narrative that teaches a moral or lesson.\n\n"
                    "Setting & Activities: Integrate any specified settings or activities (like “in a magical forest” or “on a spaceship”) and additional elements (e.g., cookies, rain, trains) into the story.\n\n"
                    "Story Generation:\n"
                    "Create a story with a clear beginning, middle, and end.\n\n"
                    "The narrative should be engaging for children and include a reflective conclusion that highlights the day’s lesson (e.g., “What did we learn today?”).\n\n"
                    "Use playful and imaginative language that is age-appropriate and fun.\n\n"
                    "Interactivity:\n"
                    "If a child interrupts or provides feedback (e.g., “I don’t want a crocodile, I want a rabbit”), promptly adjust the narrative.\n\n"
                    "Recalibrate the current segment of the story to reflect the change while maintaining narrative coherence.\n\n"
                    "Overall Objective:\n"
                    "Build an interactive storytelling experience that feels like a personalized, nightly story session between a parent and child. "
                    "Ensure the story is dynamic, engaging, and capable of evolving based on user input, making each session unique.\n\n"
                    "Remember, your goal is to transform simple input prompts into rich, imaginative narratives that not only entertain but also instill valuable lessons in a fun and interactive way."
                )
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    story_text = response["choices"][0]["message"]["content"]
    return story_text

# Function to convert text to speech using ElevenLabs with adjustable voice settings
def text_to_speech_elevenlabs(text, speech_rate, exaggeration, similarity_boost):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}?optimize_streaming=true"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": exaggeration,       # using exaggeration control for stability
            "similarity_boost": similarity_boost,
            "speech_rate": speech_rate         # assumed parameter for controlling speed
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
        return None

# Streamlit App Layout
st.title("Magic Storyland: Interactive Story Generator")

st.markdown("""
This app helps you build a mega prompt to generate a story using GPT-4. 
Fill in the inputs below, adjust the parameters, and click the button to generate your story.
""")

# Inputs for characters, themes, and activities
subject = st.text_input("Main Subject (e.g., a monkey, a princess, a robot)", "monkey")
theme = st.selectbox("Theme", ["Friendship", "Courage", "Kindness", "Adventure", "Inspiration"])
activity = st.text_input("Activity or Setting (e.g., in a magical forest, on a spaceship)", "in a magical forest")
additional_elements = st.text_area("Additional Elements (optional)", "cookies, rain, and a mysterious treasure")

# Slider for word length
word_count = st.slider("Approximate Word Count", min_value=50, max_value=1000, value=300, step=50)

# New sliders for speech settings with descriptions
speech_rate = st.slider("Speech Speed", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
st.caption("Adjust the rate at which the story is spoken (0.5 = slower, 2.0 = faster).")

exaggeration = st.slider("Exaggeration (Stability)", min_value=0.0, max_value=1.0, value=0.75, step=0.05)
st.caption("Control the stability of the voice output. Lower values might sound more expressive, while higher values sound more consistent.")

similarity_boost = st.slider("Similarity Boost", min_value=0.0, max_value=1.0, value=0.75, step=0.05)
st.caption("Adjust how closely the voice matches the target voice characteristics. Higher values yield more similar voices.")

# Construct the mega prompt based on the inputs
mega_prompt = f"""Write a creative and engaging story for children with the following details:
- Main Subject: {subject}
- Theme: {theme}
- Setting/Activity: {activity}
- Additional Elements: {additional_elements}

The story should be approximately {word_count} words long.
Make sure the story has a clear beginning, middle, and end, and includes a lesson or moral related to {theme.lower()}.
"""

st.subheader("Generated Mega Prompt")
st.code(mega_prompt, language="markdown")

# Generate story on button click
if st.button("Generate Story"):
    with st.spinner("Generating story..."):
        max_tokens = int(word_count / 0.75)  # Approximate conversion from words to tokens
        try:
            story_text = generate_story(mega_prompt, max_tokens)
            st.session_state.story = story_text  # Save the generated story in session state
            st.subheader("Your Generated Story")
            st.write(story_text)
        except Exception as e:
            st.error(f"Error generating story: {e}")

# Play Story Button: Convert story text to speech and play the audio using ElevenLabs
if st.session_state.story and st.button("Play Story"):
    with st.spinner("Converting story to speech using ElevenLabs..."):
        try:
            audio_bytes = text_to_speech_elevenlabs(
                st.session_state.story,
                speech_rate=speech_rate,
                exaggeration=exaggeration,
                similarity_boost=similarity_boost
            )
            if audio_bytes:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                    tmp.write(audio_bytes)
                    tmp.seek(0)
                    st.audio(tmp.name)
        except Exception as e:
            st.error(f"Error converting story to speech: {e}")
