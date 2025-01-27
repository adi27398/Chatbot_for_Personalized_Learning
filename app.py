import streamlit as st
import requests
import random
import time
import matplotlib.pyplot as plt

# Emojis for bot responses
bot_emojis = ["📚", "🤔", "👍", "😊", "⚡"]

# Set a unique name for the chatbot
chatbot_name = "EduBot"

# Sidebar for settings and information
st.sidebar.title(f"{chatbot_name} Options")
st.sidebar.write("Customize your experience below:")

# Personality selector
selected_personality = st.sidebar.selectbox(
    "Choose Bot Personality:",
    ["Friendly", "Professional", "Humorous"]
)

# Bot response speed slider
response_speed = st.sidebar.slider("Bot Response Speed (seconds):", 1, 5, 2)

# File uploader for future features
uploaded_file = st.sidebar.file_uploader("Upload a file for analysis:")
if uploaded_file:
    st.sidebar.success("File uploaded! The bot will process it.")

# Informational section
st.sidebar.info("This chatbot helps answer your educational questions. Simply type in the box and click 'Send'!")

# Title and greeting with a friendly font
st.markdown("""
    <style>
    .title {
        font-family: 'Courier New', Courier, monospace;
        color: #4CAF50;
        font-size: 40px;
        text-align: center;
        padding: 20px;
    }
    .message-box {
        border-radius: 10px;
        background-color: #f1f1f1;
        padding: 10px;
        font-size: 18px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #d1f1ff;
        text-align: left;
    }
    .bot-message {
        background-color: #e0ffe0;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

st.title(f"🤖 {chatbot_name}")
st.write("Welcome! Ask your questions below:")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input("You:")

# Handle Send button click
if st.button("Send"):
    if user_input.strip():
        with st.empty():
            st.write("🤖 Bot is typing...")
            time.sleep(response_speed)  # Simulate bot response delay

        try:
            # Send user input to Rasa server
            response = requests.post(
                "http://localhost:5005/webhooks/rest/webhook",
                json={"sender": "user", "message": f"[{selected_personality}] {user_input}"}
            )
            response.raise_for_status()  # Raise error for HTTP issues
            bot_responses = response.json()

            # Update chat history
            st.session_state.chat_history.append({"sender": "user", "message": user_input})
            for message in bot_responses:
                if "text" in message:
                    emoji = random.choice(bot_emojis)
                    st.session_state.chat_history.append({"sender": "bot", "message": f"{emoji} {message['text']}"})
                elif "image" in message:
                    st.session_state.chat_history.append({"sender": "bot", "message": "Sent an image"})
                    st.image(message["image"], caption="Bot's Image Response")
                elif "custom" in message:
                    st.session_state.chat_history.append({"sender": "bot", "message": "Sent a custom response"})
                    st.json(message["custom"])

        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with the server: {e}")
    else:
        st.warning("Please enter a valid message.")

# Display chat history with distinct styles for user and bot messages
for entry in st.session_state.chat_history:
    if entry["sender"] == "user":
        st.markdown(f'<div class="message-box user-message">{entry["message"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="message-box bot-message">{entry["message"]}</div>', unsafe_allow_html=True)

# Chat usage insights (sidebar chart)
st.sidebar.write("Chat Insights:")
sentiment_counts = {"Positive": 10, "Neutral": 5, "Negative": 2}
fig, ax = plt.subplots()
ax.bar(sentiment_counts.keys(), sentiment_counts.values(), color=["green", "blue", "red"])
st.sidebar.pyplot(fig)

# Footer message
st.write("💡 Tip: You can customize the bot personality or upload files for future features!")
