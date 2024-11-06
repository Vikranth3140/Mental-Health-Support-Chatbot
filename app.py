import streamlit as st
import openai
from textblob import TextBlob
import pandas as pd
import altair as alt

# Set up OpenAI API securely
openai.api_key = 'your-openai-api-key'


# Initialize session state for text size if not already set
if 'text_size' not in st.session_state:
    st.session_state['text_size'] = 18  # Default font size

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
        return "API quota limit reached. Please try again later."

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
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

def provide_coping_strategy(sentiment):
    strategies = {
        "Very Positive": "Keep up the positive vibes! Consider sharing your good mood with others.",
        "Positive": "It's great to see you're feeling positive. Keep doing what you're doing!",
        "Neutral": "Feeling neutral is okay. Consider engaging in activities you enjoy.",
        "Negative": "It seems you're feeling down. Try to take a break and do something relaxing.",
        "Very Negative": "I'm sorry to hear that you're feeling very negative. Consider talking to a friend or seeking professional help."
    }
    return strategies.get(sentiment, "Keep going, you're doing great!")

def display_disclaimer(text_size):
    st.sidebar.markdown(
        f"<h2 style='color: #FF0000; font-size: {text_size}px;'>Data Privacy Disclaimer</h2>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        f"<span style='color: #FF0000; font-size: {text_size}px;'>This application stores your session data, including your messages and "
        "sentiment analysis results, in temporary storage during your session. "
        "This data is not stored permanently and is used solely to improve your interaction with the chatbot. "
        "Please avoid sharing personal or sensitive information during your conversation.</span>",
        unsafe_allow_html=True
    )

def display_mood_chart():
    """Display a mood tracking chart."""
    mood_data = pd.DataFrame(st.session_state['mood_tracker'], columns=["Message", "Sentiment", "Polarity"]).reset_index()
    line = alt.Chart(mood_data).mark_line(color='gray').encode(x='index', y='Polarity')
    points = alt.Chart(mood_data).mark_point(filled=True).encode(
        x='index',
        y='Polarity',
        color=alt.Color('Sentiment:N', scale=alt.Scale(domain=["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"],
                                                       range=['red', 'orange', 'yellow', 'lightgreen', 'green'])),
        tooltip=['Message', 'Sentiment', 'Polarity']
    )
    st.altair_chart((line + points).properties(title="Sentiment Polarity Over Time"), use_container_width=True)
    st.caption("Sentiment polarity ranges from -1 (very negative) to +1 (very positive).")

# Sidebar slider to adjust text size
st.session_state['text_size'] = st.sidebar.slider("Adjust Text Size", min_value=12, max_value=24, value=st.session_state['text_size'])

# Main title with adjustable font size
st.markdown(f"<h1 style='font-size: {st.session_state['text_size'] + 8}px;'>Mental Health Support Chatbot</h1>", unsafe_allow_html=True)

# Initialize session state for messages and mood tracking
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'mood_tracker' not in st.session_state:
    st.session_state['mood_tracker'] = []

# Chat input form
with st.form(key='chat_form'):
    user_message = st.text_input("You:")
    submit_button = st.form_submit_button(label='Send')

if submit_button and user_message:
    # Get sentiment and coping strategy only when there's a new user message
    sentiment, polarity = analyze_sentiment(user_message)
    coping_strategy = provide_coping_strategy(sentiment)

    # Append messages and mood tracking to session state
    st.session_state['messages'].append(("You", user_message))
    st.session_state['messages'].append(("Bot", generate_response(user_message)))
    st.session_state['mood_tracker'].append((user_message, sentiment, polarity))

# Display chat messages with adjustable text size
for sender, message in st.session_state['messages']:
    if sender == "You":
        st.markdown(f"<div style='font-size: {st.session_state['text_size']}px;'><strong>You:</strong> {message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size: {st.session_state['text_size']}px;'><strong>Bot:</strong> {message}</div>", unsafe_allow_html=True)

# Display mood tracking chart
if st.session_state['mood_tracker']:
    display_mood_chart()

# Sidebar resources with adjustable text size
st.sidebar.markdown(f"<h2 style='font-size: {st.session_state['text_size'] + 2}px;'>Resources</h2>", unsafe_allow_html=True)
st.sidebar.write(f"<div style='font-size: {st.session_state['text_size']}px;'>If you need immediate help, please contact one of the following resources:</div>", unsafe_allow_html=True)
st.sidebar.write(f"<div style='font-size: {st.session_state['text_size']}px;'>1. National Suicide Prevention Lifeline: 1-800-273-8255</div><br>", unsafe_allow_html=True)
st.sidebar.write(f"<div style='font-size: {st.session_state['text_size']}px;'>2. Crisis Text Line: Text 'HELLO' to 741741</div><br>", unsafe_allow_html=True)

# Add extra space before the link
st.sidebar.write(f"<div style='font-size: {st.session_state['text_size']}px;'>"
                 f"<a href='https://www.mentalhealth.gov/get-help/immediate-help' target='_blank' style='color: #0000FF; text-decoration: none;'>More Resources</a></div><br>",
                 unsafe_allow_html=True)
# Sidebar session summary
if st.sidebar.button("Show Session Summary"):
    st.sidebar.markdown(f"<h3 style='font-size: {st.session_state['text_size']}px;'>Session Summary</h3>", unsafe_allow_html=True)
    for i, (message, sentiment, polarity) in enumerate(st.session_state['mood_tracker']):
        st.sidebar.markdown(f"<div style='font-size: {st.session_state['text_size']}px;'>{i + 1}. {message} - Sentiment: {sentiment} (Polarity: {polarity})</div>", unsafe_allow_html=True)

# Ensure that the coping strategy is displayed if available
if 'coping_strategy' in locals():
    st.write(f"<div style='font-size: {st.session_state['text_size']}px;'>{coping_strategy}</div>",
             unsafe_allow_html=True)

# Display disclaimer in sidebar
display_disclaimer(st.session_state['text_size'])