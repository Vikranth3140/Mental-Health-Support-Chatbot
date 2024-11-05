import streamlit as st
import openai
from textblob import TextBlob
import pandas as pd
import altair as alt

# Constants
openai.api_key = 'your-api-key'
COPING_STRATEGIES = {
    "Very Positive": "Keep up the positive vibes! Consider sharing your good mood with others.",
    "Positive": "It's great to see you're feeling positive. Keep doing what you're doing!",
    "Neutral": "Feeling neutral is okay. Consider engaging in activities you enjoy.",
    "Negative": "It seems you're feeling down. Try to take a break and do something relaxing.",
    "Very Negative": "I'm sorry to hear that you're feeling very negative. Consider talking to a friend or seeking "
                     "professional help."
}
RESOURCES = [
    "National Suicide Prevention Lifeline: 1-800-273-8255",
    "Crisis Text Line: Text 'HELLO' to 741741",
    "[More Resources](https://www.mentalhealth.gov/get-help/immediate-help)"
]


# Helper functions
def generate_response(prompt):
    """Generate a response from OpenAI's GPT-3.5-turbo."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content'].strip()
    except openai.error.RateLimitError:
        return "It seems we have reached the API quota limit. Please try again later or check your OpenAI account."


def analyze_sentiment(text):
    """Analyze sentiment and return the label and polarity score."""
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.5:
        return "Very Positive", polarity
    elif 0.1 < polarity <= 0.5:
        return "Positive", polarity
    elif -0.1 <= polarity <= 0.1:
        return "Neutral", polarity
    elif -0.5 < polarity < -0.1:
        return "Negative", polarity
    else:
        return "Very Negative", polarity


def display_disclaimer():
    """Display a data privacy disclaimer in the sidebar."""
    st.sidebar.markdown("<h2 style='color: #FF5733;'>Data Privacy Disclaimer</h2>", unsafe_allow_html=True)
    st.sidebar.markdown(
        "<span style='color: #FF5733;'>This application stores your session data temporarily. "
        "Please avoid sharing personal or sensitive information.</span>", unsafe_allow_html=True
    )


def display_resources():
    """Display emergency resources in the sidebar."""
    st.sidebar.title("Resources")
    st.sidebar.write("If you need immediate help, please contact one of the following resources:")
    for resource in RESOURCES:
        st.sidebar.write(resource)


def display_mood_chart():
    """Display a mood tracking chart."""
    mood_data = pd.DataFrame(st.session_state['mood_tracker'],
                             columns=["Message", "Sentiment", "Polarity"]).reset_index()
    line = alt.Chart(mood_data).mark_line(color='gray').encode(x='index', y='Polarity')
    points = alt.Chart(mood_data).mark_point(filled=True).encode(
        x='index',
        y='Polarity',
        color=alt.Color('Sentiment:N', scale=alt.Scale(domain=list(COPING_STRATEGIES.keys()),
                                                       range=['red', 'orange', 'yellow', 'lightgreen', 'green'])),
        tooltip=['Message', 'Sentiment', 'Polarity']
    )
    st.altair_chart((line + points).properties(title="Sentiment Polarity Over Time"), use_container_width=True)
    st.caption("Sentiment polarity ranges from -1 (very negative) to +1 (very positive).")


def adjust_text_size():
    """Allow the user to adjust the app text size."""
    text_size = st.sidebar.slider("Adjust Text Size", min_value=12, max_value=24, value=18)
    st.markdown(f"<style>.stApp, .stTextInput, .stButton {{ font-size: {text_size}px !important; }}</style>",
                unsafe_allow_html=True)


# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'mood_tracker' not in st.session_state:
    st.session_state['mood_tracker'] = []

# App layout
st.title("Mental Health Support Chatbot")

# User input form
with st.form(key='chat_form'):
    user_message = st.text_input("Enter your message here:", key="message_input")
    submit_button = st.form_submit_button(label='Send')

if submit_button and user_message:
    st.session_state['messages'].append(("You", user_message))
    sentiment, polarity = analyze_sentiment(user_message)
    response = generate_response(user_message)
    st.session_state['messages'].append(("Bot", response))
    st.session_state['mood_tracker'].append((user_message, sentiment, polarity))

# Display conversation history
for sender, message in st.session_state['messages']:
    st.text(f"{sender}: {message}")

# Display mood tracking chart if there are any entries
if st.session_state['mood_tracker']:
    display_mood_chart()

# Display coping strategy for the last message
if user_message:
    st.write(COPING_STRATEGIES.get(sentiment, "Keep going, you're doing great!"))

# Sidebar elements
display_resources()
display_disclaimer()
adjust_text_size()

# Session summary
if st.sidebar.button("Show Session Summary"):
    st.sidebar.write("### Session Summary")
    for i, (message, sentiment, polarity) in enumerate(st.session_state['mood_tracker']):
        st.sidebar.write(f"{i + 1}. {message} - Sentiment: {sentiment} (Polarity: {polarity})")
