import streamlit as st
import openai
from textblob import TextBlob

# Change it to your open ai api key
openai.api_key = 'your_openai_api_key'

# Function to generate a response from GPT-3
def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Analyze sentiment
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Streamlit UI setup
st.title("Mental Health Support Chatbot")

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

with st.form(key='chat_form'):
    user_message = st.text_input("You:")
    submit_button = st.form_submit_button(label='Send')

if submit_button and user_message:
    st.session_state['messages'].append(("You", user_message))
    
    sentiment = analyze_sentiment(user_message)
    response = generate_response(user_message)
    
    st.session_state['messages'].append(("Bot", response))

for sender, message in st.session_state['messages']:
    if sender == "You":
        st.text(f"You: {message}")
    else:
        st.text(f"Bot: {message}")

# Display resources
st.sidebar.title("Resources")
st.sidebar.write("If you need immediate help, please contact one of the following resources:")
st.sidebar.write("1. National Suicide Prevention Lifeline: 1-800-273-8255")
st.sidebar.write("2. Crisis Text Line: Text 'HELLO' to 741741")
st.sidebar.write("[More Resources](https://www.mentalhealth.gov/get-help/immediate-help)")