Rasa Chatbot for Topic-based Information and Course Recommendations
This repository contains a chatbot built using Rasa that provides information and recommendations based on user-specified topics. The bot can fetch details like courses from different platforms (e.g., Udemy) and provide general information about a variety of topics.

Features
Topic-based Information: The chatbot can provide information about different topics like AI, Machine Learning, Python, etc.
Course Recommendations: Based on the user's query, the bot can recommend courses from various platforms like Udemy.
Custom Actions: Integrates APIs to fetch data such as course listings or information related to topics.
Rasa NLU and Core: Uses Rasa NLU for intent classification and Rasa Core for managing dialogues.
Requirements
Python 3.7+
Rasa 3.x
Requests library (for making API calls)
API credentials for fetching data (Udemy or other platforms)
Installation
1. Clone the Repository
Clone this repository to your local machine:


git clone https://github.com/yourusername/topic-chatbot.git
cd topic-chatbot
2. Set up a Virtual Environment (optional but recommended)
Create a virtual environment to keep dependencies isolated:


python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
3. Install Dependencies
Install required dependencies listed in the requirements.txt file:


pip install -r requirements.txt
4. API Credentials
Depending on the APIs you're integrating (e.g., Udemy or any other platform), you'll need to insert the correct API keys in your actions.py file. For Udemy, you can get your credentials from their developer portal.

Replace the placeholders YOUR_CLIENT_ID and YOUR_CLIENT_SECRET in actions.py with your actual credentials.

Project Structure
nlu.yml: Contains training examples for intent classification and entity extraction.
domain.yml: Defines entities, intents, actions, and responses for the chatbot.
stories.yml: Contains example conversations (stories) to guide how the bot should respond based on user inputs.
actions.py: Defines custom actions, such as fetching courses or information related to a specific topic.
config.yml: Configuration for Rasa pipelines and policies used for NLU and dialogue management.
requirements.txt: A list of required Python packages.
data/: Directory containing the training data, including NLU data, stories, and rules.
Training the Model
Train the NLU Model:
Run the following command to train the NLU component:


rasa train nlu
Train the Core Model:
Train the entire Rasa model, including dialogue management:


rasa train
Running the Bot
1. Start the Action Server
The action server is responsible for executing custom actions (like fetching Udemy courses or topic-based info). Start the action server with:


rasa run actions
2. Start the Rasa Server
Now, start the Rasa server to run the bot:


rasa run
3. Test the Bot
You can test your bot using the Rasa shell interface:


rasa shell --debug
This will start a conversation with the bot, and you will see debug logs in the terminal.

4. Interacting with the Bot
Once the bot is running, you can start interacting with it. Examples:

User: "Tell me about Python."

Bot: The bot will provide information on Python.

User: "Show me Udemy courses on Python."

Bot: The bot will recommend a list of courses from Udemy related to Python.

Debugging
If the bot doesn't behave as expected, use the --debug flag to view detailed logs:


rasa shell --debug
This will show you the steps, including intent classification, entity extraction, and action predictions, helping you to identify and fix any issues.

Contributing
Feel free to fork this repository, make improvements, and create pull requests. If you encounter any bugs or have feature requests, please open an issue.

License
This project is licensed under the MIT License - see the LICENSE file for details.

