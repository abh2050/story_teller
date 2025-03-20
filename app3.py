import streamlit as st
import openai
import os
import asyncio
from openai import AsyncOpenAI

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI()

# Initialize session state for story
if "story" not in st.session_state:
    st.session_state.story = None

# Define rate limit for story duration
MAX_MINUTES = 15
TOKENS_PER_MINUTE = 150  # Approximate estimation based on speech synthesis
MAX_TOKENS = MAX_MINUTES * TOKENS_PER_MINUTE

# Function to generate a story using GPT-4
async def generate_story(prompt, max_tokens):
    max_tokens = min(max_tokens, MAX_TOKENS)  # Enforce rate limit
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": (
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
            )},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Streamlit UI
st.title("Magic Storyland: Interactive Story Generator")

st.markdown("""
Create a magical, AI-generated story and listen to it come to life!
""")

subject = st.text_input("Main Subject (e.g., a monkey, a princess, a robot)", "monkey")
theme = st.selectbox("Theme", ["Friendship", "Courage", "Kindness", "Adventure", "Inspiration"])
activity = st.text_input("Activity or Setting", "in a magical forest")
additional_elements = st.text_area("Additional Elements", "cookies, rain, and a mysterious treasure")
word_count = st.slider("Approximate Word Count", 50, 1000, 300, 50)

# Adjust word count to fit within max token constraint
adjusted_word_count = min(word_count, MAX_TOKENS * 0.75)

target_prompt = f"""
Write a creative and engaging children's story with:
- Main Subject: {subject}
- Theme: {theme}
- Setting: {activity}
- Elements: {additional_elements}
The story should be around {adjusted_word_count} words and include a lesson on {theme.lower()}.
"""

st.subheader("Generated Mega Prompt")
st.code(target_prompt, language="markdown")

if st.button("Generate Story"):
    with st.spinner("Creating your story..."):
        try:
            st.session_state.story = asyncio.run(generate_story(target_prompt, int(adjusted_word_count / 0.75)))
            st.subheader("Your Generated Story")
            st.write(st.session_state.story)
        except Exception as e:
            st.error(f"Error: {e}")

if st.session_state.story and st.button("Play Story"):
    async def play_story():
        try:
            async with client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice="coral",
                input=st.session_state.story,
                instructions="Narrate the story in a warm, engaging tone for children.",
                response_format="mp3",
            ) as response:
                audio_data = await response.read()  # Ensure coroutine is awaited
                st.audio(audio_data, format='audio/mp3')
        except Exception as e:
            st.error(f"Error: {e}")
    
    asyncio.run(play_story())
