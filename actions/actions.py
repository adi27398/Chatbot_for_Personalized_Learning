# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


import requests
import random
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from rasa_sdk import Action
from rasa_sdk.events import SlotSet, ActionExecuted
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from rasa_sdk import Tracker
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


logger = logging.getLogger(__name__)

class ActionGenerateContent(Action):
    def __init__(self):
        self.model_name = "google/flan-t5-large"
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            logger.info(f"Model {self.model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.tokenizer = None

    def name(self) -> Text:
        return "action_generate_content"

    def generate_prompt(self, topic: str) -> str:
        return f"""Generate a detailed and educational explanation about {topic}.
        Include:
        - Definition and key concepts
        - Main principles or components
        - Real-world applications or examples
        - Important facts and developments
        - Current trends or future perspectives
        Make it informative yet easy to understand."""

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        if not self.model or not self.tokenizer:
            dispatcher.utter_message(text="Sorry, I'm having technical difficulties. Please try again later.")
            return []

        topic = next(tracker.get_latest_entity_values("topic"), None)
        if not topic:
            dispatcher.utter_message(text="I couldn't find a topic. Can you please specify what you'd like to learn about?")
            return []
        
        # Check if the topic is non-educational
        non_educational_keywords = ["pizza", "food", "Infosys", "company", "movie", "celebrity", "sports", "music", "recipe", "travel", "fashion", "gossip", "weather", "news", "politics", "games", "shopping", "cars"]
        if any(keyword in topic.lower() for keyword in non_educational_keywords):
            dispatcher.utter_message(text="Sorry, I couldn't find this topic. Can you please ask some other topic that you'd like to learn about?")
            return []
        
        try:
            input_text = self.generate_prompt(topic)
            inputs = self.tokenizer(input_text, return_tensors="pt", max_length=1024, truncation=True)
            
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=512,          # Increased length for more detailed content
                min_length=100,          # Ensure minimum content length
                num_beams=5,            
                temperature=0.7,         # Slightly increased for more creativity
                do_sample=True,
                top_p=0.92,             # Adjusted for better quality
                top_k=50,               # Added top-k sampling
                repetition_penalty=2.5,  # Increased penalty for repetitions
                length_penalty=1.5,      # Encourage longer outputs
                no_repeat_ngram_size=3,  # Prevent 3-gram repetitions
                early_stopping=True
            )
            
            content = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Format the content for better readability
            formatted_content = content.replace(". ", ".\n\n")
            
            dispatcher.utter_message(text=f"Here's a detailed explanation about {topic}:\n\n{formatted_content}")
            logger.info(f"Generated content for topic: {topic}")
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            dispatcher.utter_message(text="I apologize, but I couldn't generate the content at this moment.")
        
        return [SlotSet("topic", topic)]
    


class ActionFetchYoutubeVideos(Action):
    def name(self) -> Text:
        return "action_fetch_youtube_videos"
        
    def __init__(self):

        self.youtube = build('youtube', 'v3', developerKey='AIzaSyBqODsKSw0TK-FPP0JAMMKFqH3oqhW1q1M')

    def get_video_details(self, video_id):
        try:
            response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()
            return response['items'][0] if response['items'] else None
        except Exception:
            return None

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            topic = tracker.get_slot("topic")
            if not topic:
                dispatcher.utter_message(text="I need a topic to search for videos.")
                return []

            # Add educational keywords to search
            search_query = f"{topic} tutorial how to learn"
            
            search_response = self.youtube.search().list(
                q=search_query,
                part='snippet',
                maxResults=5,
                type='video',
                videoCategoryId='27',  # Education category
                order='relevance',
                safeSearch='moderate',
                relevanceLanguage='en'
            ).execute()

            if not search_response.get('items'):
                dispatcher.utter_message(text=f"Sorry, I couldn't find any tutorial videos about {topic}")
                return []

            videos = []
            for item in search_response['items']:
                video_id = item['id']['videoId']
                details = self.get_video_details(video_id)
                
                if details:
                    description = details['snippet']['description'].lower()
                    # Check for educational indicators
                    edu_terms = ['learn', 'tutorial', 'guide', 'course', 'lesson', 'example', 'explained']
                    edu_score = sum(1 for term in edu_terms if term in description)
                    
                    if edu_score > 0:
                        title = item['snippet']['title']
                        channel = item['snippet']['channelTitle']
                        url = f"https://www.youtube.com/watch?v={video_id}"
                        views = int(details['statistics'].get('viewCount', 0))
                        likes = int(details['statistics'].get('likeCount', 0))
                        
                        videos.append({
                            'title': title,
                            'channel': channel,
                            'url': url,
                            'edu_score': edu_score,
                            'engagement': views + (likes * 100)
                        })

            # Sort by educational score and engagement
            videos.sort(key=lambda x: (x['edu_score'], x['engagement']), reverse=True)
            top_videos = videos[:2]

            if not top_videos:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any quality tutorial videos about {topic}")
                return []

            response = f"Here are 2 educational videos about {topic}:\n\n"
            for video in top_videos:
                response += f"📚 {video['title']}\n"
                response += f"👤 Channel: {video['channel']}\n"
                response += f"🔗 {video['url']}\n\n"

            dispatcher.utter_message(text=response)
            return []

        except HttpError as e:
            dispatcher.utter_message(text="Sorry, I couldn't fetch any videos at the moment.")
            return []

class ActionCollectFeedback(Action):
    def name(self) -> Text:
        return "action_collect_feedback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Check if feedback is already provided
        feedback = tracker.get_slot("feedback") or tracker.latest_message.get('text')

        if feedback:
            try:
                # Log feedback
                with open("feedback_log.txt", "a") as file:
                    file.write(f"Feedback: {feedback}\n")

                dispatcher.utter_message(response="utter_thank_feedback")
                return [SlotSet("feedback", feedback)]
            except Exception as e:
                dispatcher.utter_message(text="An error occurred while saving your feedback. Please try again later.")
                print(f"Error saving feedback: {e}")
                return []
        else:
            dispatcher.utter_message(response="utter_feedback_error")
            return []


class ActionGetCourses(Action):
    def name(self) -> Text:
        return "action_get_courses"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course_topic = tracker.get_slot("course_topic")  # Updated to use course_topic
        if not course_topic:
            dispatcher.utter_message(text="Please specify a topic to search for courses.")
            return []

        # Udemy API details
        api_url = "https://www.udemy.com/api-2.0/courses/"
        client_id = "OXezAwV50jAClVhXuTNdc4fGzNVmcHOjeQ2SIyfy" # Replace with your Udemy Client ID
        client_secret = "CKCwPw0y1qY8qMCFYg4GaKh8s6z0wcizilTmz5USoq0pH33ztK4VOt0mBoYh8cDT83th9N34oeG4OvcHqg180X5lpiXkYGNWApLqG98FdtIlSWJ2qdnMOjWUNXbBTbKF"  # Replace with your Udemy Client Secret

        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {client_id}:{client_secret}"
        }
        params = {
            "search": course_topic,  # Use the course_topic slot value for the search query
            "page_size": 5
        }

        # Make the API request
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code == 200:
            courses = response.json().get("results", [])
            if courses:
                course_list = "\n".join(
                    [f"{i + 1}. {course['title']} (Link: {course['url']})" for i, course in enumerate(courses)]
                )
                dispatcher.utter_message(text=f"Here are some courses on {course_topic}:\n{course_list}")
            else:
                dispatcher.utter_message(text=f"Sorry, no courses found on {course_topic}.")
        else:
            dispatcher.utter_message(text="Failed to fetch courses. Please try again later.")

        return []
