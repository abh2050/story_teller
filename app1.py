import streamlit as st
import openai
import os
from gtts import gTTS
import tempfile

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state for story
if "story" not in st.session_state:
    st.session_state.story = ""

# Function to generate a story using GPT-4
def generate_story(prompt, max_tokens):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are a creative storyteller that helps parents and children co-create engaging, educational stories."
                    " Your role is to generate interactive narratives based on user inputs and respond to mid-story modifications."
                    "\n\nKey Instructions:\n"
                    "- Use the provided main subject as the protagonist.\n"
                    "- Incorporate the chosen theme to teach a moral lesson.\n"
                    "- Integrate specified settings and activities into the story.\n"
                    "- Ensure a structured story with a beginning, middle, and end.\n"
                    "- Use age-appropriate, engaging language for children.\n"
                    "- Be responsive to user feedback to make the story interactive.\n\n"
                    "Make sure the story is engaging, dynamic, and fun!"
                )},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.95,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating story: {e}"

# Streamlit App Layout
st.title("Magic Storyland: Interactive Story Generator")

st.markdown("""
This app helps you build a mega prompt to generate a story using GPT-4. 
Fill in the inputs below, adjust the parameters, and click the button to generate your story.
""")

# User Inputs
subject = st.text_input("Main Subject (e.g., a monkey, a princess, a robot)", "monkey")

theme = st.selectbox(
    "Theme",
    ["Friendship", "Courage", "Kindness", "Adventure", "Inspiration"],
    index=0  # Ensures a default selection
)

activity = st.text_input("Activity or Setting (e.g., in a magical forest, on a spaceship)", "in a magical forest")
additional_elements = st.text_area("Additional Elements (optional)", "cookies, rain, and a mysterious treasure")

# Story length control
word_count = st.slider("Approximate Word Count", min_value=50, max_value=1000, value=300, step=50)
duration_minutes = st.slider("Approximate Reading Duration (minutes)", min_value=1, max_value=30, value=5, step=1)

# Construct a structured prompt
mega_prompt = f"""
Write a creative and engaging children's story with the following details:
- **Main Subject:** {subject}
- **Theme:** {theme}
- **Setting/Activity:** {activity}
- **Additional Elements:** {additional_elements}

The story should be approximately **{word_count} words long**, which should take about **{duration_minutes} minutes** to read.
Ensure it has a clear **beginning, middle, and end**, with a lesson related to **{theme.lower()}**.
"""

st.subheader("Generated Mega Prompt")
st.code(mega_prompt, language="markdown")

# Generate story on button click
if st.button("Generate Story"):
    with st.spinner("Generating story..."):
        max_tokens = int(word_count * 1.3)  # Approximate word-to-token conversion
        story_text = generate_story(mega_prompt, max_tokens)
        if "Error" in story_text:
            st.error(story_text)
        else:
            st.session_state.story = story_text
            st.subheader("Your Generated Story")
            st.write(st.session_state.story)

# Convert text to speech and play audio
if st.session_state.story and st.button("Play Story"):
    with st.spinner("Converting story to speech..."):
        try:
            tts = gTTS(st.session_state.story, lang='en', slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                temp_filename = tmp.name
                tts.save(temp_filename)
            st.audio(temp_filename)
            os.remove(temp_filename)  # Cleanup temporary file
        except Exception as e:
            st.error(f"Error converting story to speech: {e}")

