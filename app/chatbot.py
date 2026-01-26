import os
import logging
import json
from dotenv import load_dotenv
from google import genai
# ... (imports remain)

# ... (client setup remains)

# ... (get_bot_response remains)

def get_pregnancy_insight(stats: dict):
    """
    Generates a personalized daily insight in JSON format.
    """
    if not GEMINI_READY:
         if not configure_gemini():
            return {"quick_assessment": "AI Unavailable", "detailed_analysis": "Check connection.", "actionable_advice": "Stay hydrated.", "motivation": "You got this!"}

    try:
        prompt = (
            "You are an expert obstetrician. Analyze these daily stats: "
            f"Sleep: {stats.get('sleep_hours', 0)}h, Steps: {stats.get('steps_count', 0)}, Water: {stats.get('water_glasses', 0)} glasses. "
            "Return a valid **JSON object** (no markdown formatting) with these exact keys:\n"
            "- 'quick_assessment': Short summary.\n"
            "- 'analysis_sleep': Specific critique on sleep.\n"
            "- 'analysis_steps': Specific critique on activity.\n"
            "- 'analysis_water': Specific critique on hydration.\n"
            "- 'actionable_advice': 2-3 specific tips.\n"
            "- 'motivation': A closing encouragement.\n"
        )
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Gemini Insight Error: {e}")
        return {
            "quick_assessment": "Error generating insight.",
            "analysis_sleep": "N/A",
            "analysis_steps": "N/A",
            "analysis_water": "N/A", 
            "actionable_advice": "Please try again.", 
            "motivation": "Keep going!"
        }

def get_weekly_guide(week_number: int):
    """
    Generates a pregnancy guide in JSON format.
    """
    if not GEMINI_READY:
         if not configure_gemini():
            return None

    try:
        prompt = (
            f"Generate a medical-grade pregnancy guide for Week {week_number}. "
            "Return a valid **JSON object** (no markdown formatting) with these exact keys:\n"
            "- 'baby_development': Text about baby's size and milestones.\n"
            "- 'mothers_body': Physical changes and symptoms.\n"
            "- 'nutrition_tips': Key nutrients and food advice.\n"
            "- 'todo_list': Medical items and preparations.\n"
            "- 'warning_signs': When to call the doctor.\n"
        )
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Gemini Guide Error: {e}")
        return None

# Load environment variables
load_dotenv()

# Configure Logging
logger = logging.getLogger(__name__)

# --- Configuration ---
# API Key from environment
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

# Global client variable
client = None

def configure_gemini():
    """
    Configures the Google GenAI client.
    Returns True if successful, False otherwise.
    """
    global client
    if not API_KEY:
        logger.error("GEMINI_API_KEY is missing in .env")
        return False
    
    try:
        client = genai.Client(api_key=API_KEY)
        logger.info("Gemini Client configured successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to configure Gemini Client: {e}")
        return False

# Initialize on load
GEMINI_READY = configure_gemini()

# In-memory store for conversation history (for chatbot context)
conversations_history_store = {} 

def get_bot_response(user_input, conversation_id=None):
    """
    Generates a response using Gemini API (google-genai SDK), maintaining context.
    """
    if not GEMINI_READY:
        if not configure_gemini():
             return "I'm having trouble connecting to the stars right now. Please try again later."

    try:
        # Retrieve or initialize history
        history = conversations_history_store.get(conversation_id, [])
        
        # Add User Message to History
        history.append(f"User: {user_input}")
        
        # Limit history to last 10 turns to save tokens
        if len(history) > 10:
            history = history[-10:]

        # Construct Prompt
        system_prompt = (
            "You are a compassionate, expert AI pregnancy companion named 'Future Health Mom'. "
            "Your goal is to support pregnant women with medical information, wellness tips, and emotional support. "
            "Keep answers concise (under 100 words) but helpful. "
            "If asked about medical emergencies, advise like a doctor immediately."
        )
        
        # Combine system prompt with history
        full_prompt = f"{system_prompt}\n\n" + "\n".join(history) + "\nAI:"

        # Generate Response
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt
        )
        
        bot_reply = response.text.strip()
        
        # Add AI Reply to History
        history.append(f"AI: {bot_reply}")
        conversations_history_store[conversation_id] = history
        
        return bot_reply

    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return "I'm currently updating my medical database. Please ask again in a moment."

def get_pregnancy_insight(stats: dict):
    """
    Generates a personalized, detailed daily insight based on daily health stats.
    Returns: Dict
    """
    if not GEMINI_READY:
         if not configure_gemini():
            return {
                "quick_assessment": "AI Unavailable", 
                "motivation": "Keep going!", 
                "analysis_sleep": "N/A", 
                "analysis_steps": "N/A", 
                "analysis_water": "N/A", 
                "actionable_advice": "Stay hydrated."
            }

    try:
        prompt = (
            "You are an expert obstetrician and wellness coach for pregnant women. "
            "Analyze the following daily health stats and return a **valid JSON object** (no markdown formatting) with these exact keys:\n"
            f"**User Stats:** Sleep: {stats.get('sleep_hours', 0)}h, Steps: {stats.get('steps_count', 0)}, Water: {stats.get('water_glasses', 0)} glasses.\n"
            "\n"
            "**Required JSON Keys:**\n"
            "- 'quick_assessment': One sentence summary.\n"
            "- 'analysis_sleep': Specific critique on sleep.\n"
            "- 'analysis_steps': Specific critique on activity.\n"
            "- 'analysis_water': Specific critique on hydration.\n"
            "- 'actionable_advice': 2 specific tips (Markdown allowed).\n"
            "- 'motivation': A short, warm closing encouragement.\n"
        )
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Gemini Insight Error: {e}")
        return {
            "quick_assessment": "Error generating insight.",
            "analysis_sleep": "N/A",
            "analysis_steps": "N/A",
            "analysis_water": "N/A", 
            "actionable_advice": "Please try again.", 
            "motivation": "You got this!"
        }

def get_weekly_guide(week_number: int):
    """
    Generates a pregnancy guide in JSON format.
    """
    if not GEMINI_READY:
         if not configure_gemini():
            return None

    try:
        prompt = (
            f"Generate a medical-grade pregnancy guide for Week {week_number}. "
            "Return a valid **JSON object** (no markdown formatting for the JSON structure itself) with these exact keys. "
            "For the content values, use **Markdown formatting** (bullet points, bold text) where appropriate, especially for lists.\n"
            "- 'baby_development': Text about baby's size and milestones.\n"
            "- 'mothers_body': Physical changes and symptoms.\n"
            "- 'nutrition_tips': Key nutrients and food advice.\n"
            "- 'todo_list': A Markdown bulleted list of medical items and preparations.\n"
            "- 'warning_signs': A Markdown bulleted list of when to call the doctor.\n"
        )
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Gemini Guide Error: {e}")
        return None

