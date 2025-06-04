import streamlit as st
import requests
import json
import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Any
import difflib
from dataclasses import dataclass
import logging
import time

# Set up logging
logging.basicConfig(
    filename="api_errors.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Page configuration
st.set_page_config(
    page_title="Shared Skillet AI - Professional Kitchen Assistant",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Darker theme styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #1e1e2e 0%, #3e3e5e 100%);
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
    }
    
    .stTextInput, .stTextArea, .stSelectbox {
        background-color: #2a2a3a;
        border-radius: 12px;
        border: 2px solid #3c3c4c;
        color: #1a1a1a;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > select {
        color: #1a1a1a !important;
    }
    
    .chat-message {
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        color: #1a1a1a;
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, #5a5af5 0%, #8a5af5 100%);
        color: #ffffff;
        margin-left: 20%;
    }
    
    .chat-message.assistant {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
        color: #ffffff;
        margin-right: 20%;
    }
    
    .menu-item-card {
        background: #2a2a3a;
        padding: 15px;
        border-radius: 16px;
        margin: 10px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border: 1px solid #3c3c4c;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .menu-item-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
    }
    
    .menu-item-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #5a5af5, #8a5af5);
    }
    
    .price-badge {
        background: linear-gradient(135deg, #5a5af5 0%, #8a5af5 100%);
        color: #ffffff;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 5px;
    }
    
    .category-badge {
        background: linear-gradient(135deg, #ff9a9e 0%, #ff6b6b 100%);
        color: #ffffff;
        padding: 6px 12px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: 500;
        display: inline-block;
        margin: 5px;
    }
    
    .shopping-list {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 16px;
        border-left: 5px solid #00c851;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        color: #1a1a1a;
    }
    
    .meal-plan {
        background: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%);
        padding: 20px;
        border-radius: 16px;
        border-left: 5px solid #ff4444;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        color: #1a1a1a;
    }
    
    .tab-container {
        background: #2a2a3a;
        border-radius: 16px;
        padding: 5px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #5a5af5 0%, #8a5af5 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(90,90,245,0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(90,90,245,0.6);
    }
    
    .ai-badge {
        background: linear-gradient(45deg, #ff4444, #00c851);
        color: #ffffff;
        padding: 4px 8px;
        border-radius: 8px;
        font-size: 0.7em;
        font-weight: bold;
        margin-left: 8px;
    }
    
    .professional-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #5a5af5 0%, #8a5af5 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        color: #ffffff;
        box-shadow: 0 10px 30px rgba(90,90,245,0.3);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .video-container {
        position: relative;
        width: 100%;
        height: 200px;
        border-radius: 12px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .smart-suggestion {
        background: linear-gradient(135deg, #00c851 0%, #007e33 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #00f2fe;
        color: #1a1a1a;
    }
    
    h1, h2, h3, h4, h5, h6, p, li, span {
        color: #1a1a1a !important;
    }
    
    .price-badge, .category-badge, .stButton > button, .ai-badge,
    .professional-header h1, .professional-header h3, .professional-header p,
    .chat-message.user, .chat-message.assistant {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Data class for menu items
@dataclass
class MenuItem:
    id: int
    dish_name: str
    category: str
    taste_category: str
    image_url: str
    youtube_link: str
    pricing: Dict[str, float]
    serving_info: Dict[str, str]

# Menu items database
MENU_ITEMS = [
    MenuItem(1, "Chicken Mandi", "Main", "Savory", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Chicken+Mandi..jpg", "https://youtube.com/embed/B3IV5P-4PCk?si=Ql_EWzyo6hhQ6mp1", {"full_tray": 90, "half_tray": 50, "per_serving": 12}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(2, "Kabuli Pulao", "Main", "Savory", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Kabuli+Polao.jpg", "https://www.youtube.com/embed/ch8zl7V4ABo", {"full_tray": 90, "half_tray": 50, "per_serving": 12}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(3, "Chicken Dum Biryani", "Main", "Savory", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Chicken+Biryani.jpg", "https://www.youtube.com/embed/9CsloZe-ekI", {"full_tray": 90, "half_tray": 50, "per_serving": 12}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(4, "Kebab Platter", "Appetizer", "Savory", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Kabab+Platter..jpg", "https://www.youtube.com/embed/3ELfF5s8yz0", {"full_tray": 90, "half_tray": 50, "per_serving": 12}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(5, "Chicken Kabsa", "Main", "Savory", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Chicken+Kabsa.jpg", "", {"full_tray": 90, "half_tray": 50, "per_serving": 12}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(6, "Chicken 65 Biryani", "Main", "Spicy", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Chicken+65+Biryani.jpg", "https://www.youtube.com/embed/jFh6NF7cVcE", {"full_tray": 90, "half_tray": 50, "per_serving": 12}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(7, "Chicken Kofta Biryani", "Main", "Savory", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Kofta+Biryani.jpg", "https://www.youtube.com/embed/Q1nDOX4lDuE", {"full_tray": 90, "half_tray": 50, "per_serving": 12}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(8, "Beef Dum Biryani", "Main", "Savory", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Beef+Dum+Biryani.jpg", "https://www.youtube.com/embed/qkiMa9Bke0M", {"full_tray": 90, "half_tray": 50, "per_serving": 12}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(9, "Dubai Cheese Cake", "Dessert", "Sweet", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Dubai+Cheese+Cake.jpg", "https://www.youtube.com/embed/tVJtZBSp3Hw&t", {"full_tray": 94.99, "half_tray": 54.99, "per_serving": 7.99}, {"full_tray": "28-30 people", "half_tray": "12-15 people"}),
    MenuItem(10, "Tiramisu", "Dessert", "Sweet", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Tiramisu.jpg", "https://www.youtube.com/embed/ens-bJaLuQQ", {"full_tray": 89.99, "half_tray": 49.99, "per_serving": 6.99}, {"full_tray": "28-30 people", "half_tray": "12-15 people"}),
    MenuItem(11, "Mango Tiramisu", "Dessert", "Sweet", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Mango+Tiramisu.jpg", "https://drive.google.com/file/d/16rZwh15xVDdm2RE8LseEpjqSrCFdWPJi/preview", {"full_tray": 89.99, "half_tray": 49.99, "per_serving": 6.99}, {"full_tray": "28-30 people", "half_tray": "12-15 people"}),
    MenuItem(12, "Butter Pound Cake", "Dessert", "Sweet", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Pound+Cake.jpg", "https://www.youtube.com/embed/luaEFTC78aQ", {"Whole Cake": 7.99}, {}),
    MenuItem(13, "Malai Sheek Kebab (Beef/Chicken)", "Main", "Savory", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Chicken+Malai+Sheek+Kebab.jpg", "https://www.youtube.com/embed/3Ci1Jr8cWn8&t", {"full_tray": 90, "half_tray": 50, "per_serving": 12}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(14, "Egg Potato Cutlet", "Appetizer", "Savory", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Egg+Potato+Cutlet.jpg", "https://www.youtube.com/embed/LjSN5QtdLmE", {"per count": 3.99}, {}),
    MenuItem(15, "Shahi Malai Jorda", "Dessert", "Sweet", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Shahi+Malai+Jorda.jpg", "https://www.youtube.com/embed/GXS3UHmB6NM", {"full_tray": 90, "half_tray": 50, "per_serving": 9.99}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(16, "Beef Tehari", "Main", "Savory", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Beef+Tehari.jpg", "https://www.youtube.com/embed/3wwr5nW6af0", {"full_tray": 90, "half_tray": 39.99, "per_serving": 9.99}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(17, "Chicken Roast", "Main", "Savory", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Chicken+Roast.jpg", "https://www.youtube.com/embed/P56bYJXx8Ak", {"full_tray": 90, "half_tray": 50, "per_serving": 12}, {"full_tray": "15-17 people", "half_tray": "5-6 people"}),
    MenuItem(18, "Pina colada (Non Alcoholic)", "Drinks", "Sweet and Refreshing", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Pina+Colada.jpg", "", {"per glass": 3}, {}),
    MenuItem(19, "Mango Lassi", "Drinks", "Sweet", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Mango+Lassi.jpg", "", {"per glass": 4}, {}),
    MenuItem(20, "Mint Lemon", "Drinks", "Sweet", "https://s3.us-east-1.amazonaws.com/sharedskillet.com/Mint+Lemon.jpg", "", {"per glass": 2}, {})
]

# Validate image URLs
@st.cache_data
def validate_image_urls():
    for item in MENU_ITEMS:
        try:
            response = requests.head(item.image_url, timeout=5)
            if response.status_code != 200:
                item.image_url = f"https://via.placeholder.com/300x200?text={item.dish_name.replace(' ', '+')}"
                logging.info(f"Replaced URL for {item.dish_name} with placeholder due to status {response.status_code}")
        except Exception as e:
            item.image_url = f"https://via.placeholder.com/300x200?text={item.dish_name.replace(' ', '+')}"
            logging.error(f"Error for {item.dish_name}: {str(e)} - Replaced with placeholder")

# Run URL validation at startup
validate_image_urls()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = {}
if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = {}
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "AI Assistant"
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {
        "cooking_style": "Bangladeshi",
        "expertise_level": "Intermediate",
        "dietary_restrictions": [],
        "spice_level": "Medium",
        "serving_size": "4-6 people"
    }
if 'recommended_items' not in st.session_state:
    st.session_state.recommended_items = []

# Professional header
st.markdown("""
<div class="professional-header">
    <h1>🍳 Shared Skillet AI</h1>
    <h3>Professional Kitchen Assistant with Smart Menu Integration</h3>
    <p>Powered by Advanced AI • Curated Menu • Personalized Experience</p>
</div>
""", unsafe_allow_html=True)

# API Configuration
EURON_API_URL = "https://api.euron.one/api/v1/euri/alpha/chat/completions"
EURON_MODEL = "gemini-2.5-pro-exp-03-25"
FALLBACK_MODEL = "gemini-pro"

def get_euron_api_key():
    try:
        api_key = st.secrets["euron"]["api_key"]
        if not api_key:
            raise KeyError("API key is empty")
        return api_key
    except (KeyError, TypeError) as e:
        logging.error(f"Failed to load API key: {str(e)}")
        return None

def call_euron_api(messages, temperature=0.7, max_tokens=1000, retries=3, initial_delay=2):
    api_key = get_euron_api_key()
    if not api_key:
        logging.error("No API key available")
        return "Error: API key not configured. Please check your Streamlit secrets."
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Try primary model first, then fallback
    for model in [EURON_MODEL, FALLBACK_MODEL]:
        payload = {
            "messages": messages,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        logging.info(f"Sending API request with model {model}: {json.dumps(payload, indent=2)}")
        
        for attempt in range(retries):
            try:
                response = requests.post(EURON_API_URL, headers=headers, json=payload, timeout=5)
                response.raise_for_status()
                data = response.json()
                logging.info(f"API response (model: {model}, attempt: {attempt+1}): {json.dumps(data, indent=2)}")
                
                # Flexible response parsing
                if 'choices' in data and len(data['choices']) > 0:
                    choice = data['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        return choice['message']['content'].strip()
                    elif 'text' in choice:
                        return choice['text'].strip()
                    elif 'content' in choice:
                        return choice['content'].strip()
                logging.warning(f"No valid content in API response (model: {model}, attempt: {attempt+1})")
                return "Error: No valid response content from API."
            
            except requests.exceptions.HTTPError as e:
                logging.error(f"HTTP error (model: {model}, attempt: {attempt+1}): {str(e)} - Status: {e.response.status_code} - Response: {e.response.text}")
                if e.response.status_code == 500 and attempt < retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    logging.info(f"Retrying after {delay} seconds due to 500 error...")
                    time.sleep(delay)
                    continue
                return f"Error: HTTP {e.response.status_code} - {e.response.text}"
            
            except requests.exceptions.Timeout:
                logging.error(f"Request timed out after 5 seconds (model: {model}, attempt: {attempt+1})")
                if attempt < retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    logging.info(f"Retrying after {delay} seconds due to timeout...")
                    time.sleep(delay)
                    continue
                return "Error: API request timed out after multiple attempts."
            
            except requests.exceptions.RequestException as e:
                logging.error(f"Request error (model: {model}, attempt: {attempt+1}): {str(e)}")
                return f"Error: Failed to connect to API - {str(e)}"
            
            except ValueError as e:
                logging.error(f"JSON decode error (model: {model}, attempt: {attempt+1}): {str(e)} - Response: {response.text}")
                return "Error: Invalid API response format."
            
            except Exception as e:
                logging.error(f"Unexpected error (model: {model}, attempt: {attempt+1}): {str(e)}")
                return f"Error: Unexpected issue - {str(e)}"
    
    return f"Error: Failed to get response with models {EURON_MODEL} and {FALLBACK_MODEL} after {retries} attempts."

# Smart menu search
def smart_menu_search(query: str, limit: int = 3) -> List[MenuItem]:
    query_lower = query.lower()
    scored_items = []
    for item in MENU_ITEMS:
        score = 0
        if query_lower in item.dish_name.lower():
            score += 90
        if query_lower in item.category.lower():
            score += 50
        if query_lower in item.taste_category.lower():
            score += 30
        similarity = difflib.SequenceMatcher(None, query_lower, item.dish_name.lower()).ratio()
        score += similarity * 40
        keywords = ['chicken', 'beef', 'biryani', 'kebab', 'dessert', 'drink', 'cake', 'spicy', 'sweet', 'savory']
        for keyword in keywords:
            if keyword in query_lower and keyword in item.dish_name.lower():
                score += 25
        if score > 20:
            scored_items.append((item, score))
    scored_items.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in scored_items[:limit]]

def display_menu_item(item: MenuItem, show_video: bool = True):
    with st.container():
        st.markdown(f"""
        <div class="menu-item-card">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; flex-grow: 1;">{item.dish_name}</h3>
                <span class="category-badge">{item.category}</span>
                <span class="category-badge" style="background: linear-gradient(135deg, #ff9a9e 0%, #ff6b6b 100%); color: #ffffff;">{item.taste_category}</span>
            </div>
            <div style="display: flex; gap: 10px;">
                <div style="flex: 1; max-width: 300px;">
        """, unsafe_allow_html=True)
        try:
            st.image(
                item.image_url,
                use_container_width=False,
                width=300,
                caption=f"{item.dish_name} Image",
                output_format="JPEG",
                clamp=True,
                channels="RGB"
            )
            st.markdown("""
            <style>
                .menu-item-card img {
                    width: 100%;
                    max-width: 300px;
                    height: 200px;
                    object-fit: cover;
                    border-radius: 12px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    display: block;
                    margin: 0 auto;
                }
            </style>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Failed to load image for {item.dish_name}: {str(e)}")
            st.image(
                f"https://via.placeholder.com/300x200?text={item.dish_name.replace(' ', '+')}",
                use_container_width=False,
                width=300,
                caption="Image Not Available"
            )
            st.markdown("""
            <style>
                .menu-item-card img {
                    width: 100%;
                    max-width: 300px;
                    height: 200px;
                    object-fit: cover;
                    border-radius: 12px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    display: block;
                    margin: 0 auto;
                }
            </style>
            """, unsafe_allow_html=True)
        st.markdown("""
                </div>
                <div style="flex: 1;">
                    <h4>Pricing Options:</h4>
        """, unsafe_allow_html=True)
        for option, price in item.pricing.items():
            serving_info = item.serving_info.get(option, "")
            st.markdown(f'<span class="price-badge">{option.replace("_", " ").title()}: ${price} {serving_info}</span>', unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"Get Recipe for {item.dish_name}", key=f"recipe_{item.id}"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"Please provide a detailed recipe for {item.dish_name}, including ingredients, step-by-step instructions, and cooking tips."
                })
                st.session_state.current_tab = "AI Assistant"
                st.rerun()
        with col2:
            if st.button(f"Add to Shopping List", key=f"shop_{item.id}"):
                st.session_state.shopping_list[item.dish_name] = [f"Ingredients for {item.dish_name} (to be detailed)"]
                st.success(f"✅ {item.dish_name} ingredients concept added to shopping list!")
        with col3:
            if item.youtube_link and st.button(f"Watch Video", key=f"video_{item.id}"):
                st.video(item.youtube_link)
        st.markdown("</div>", unsafe_allow_html=True)

def generate_enhanced_system_message(purpose="general", relevant_menu_items=None):
    current_date = datetime.now().strftime("%Y-%m-%d")
    prefs = st.session_state.user_preferences
    menu_context = ""
    if relevant_menu_items:
        menu_context = f"""
        PRIORITY MENU ITEMS (Always suggest these first when relevant):
        {chr(10).join([f"- {item.dish_name} ({item.category}, {item.taste_category})" for item in relevant_menu_items])}
        These are authentic, professional dishes from Shared Skillet. Always prioritize recommending these items when they match the user's request.
        """
    base_system_message = f"""
    You are an expert culinary AI assistant for Shared Skillet, specializing in authentic Bangladeshi and South Asian cuisine. 
    Today is {current_date}.
    Current user preferences:
    - Cooking Style: {prefs["cooking_style"]}
    - Expertise Level: {prefs["expertise_level"]}
    - Dietary Restrictions: {', '.join(prefs["dietary_restrictions"]) if prefs["dietary_restrictions"] else "None"}
    - Spice Level: {prefs["spice_level"]}
    - Serving Size: {prefs["serving_size"]}
    {menu_context}
    CORE GUIDELINES:
    1. ALWAYS check if user requests match our menu items first
    2. If menu items are relevant, present them as the primary recommendation
    3. Only suggest generic/alternative recipes if no menu items match
    4. Provide detailed, professional cooking instructions
    5. Include ingredient substitutions and cooking tips
    6. Emphasize food safety and proper techniques
    7. Adapt complexity to user's expertise level
    8. Respect dietary restrictions and preferences
    RESPONSE STYLE:
    - Professional yet friendly tone
    - Clear, step-by-step instructions
    - Include cooking times, temperatures, and yields
    - Provide cultural context for traditional dishes
    - Suggest presentation and serving tips
    Always prioritize Shared Skillet's authentic menu items over generic suggestions.
    """
    return base_system_message

# Tab system
tab_container = st.container()
with tab_container:
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    tabs = ["AI Assistant", "Menu Explorer", "Shopping List", "Meal Planning", "Smart Recommendations"]
    cols = st.columns(len(tabs))
    for i, tab in enumerate(tabs):
        with cols[i]:
            is_active = st.session_state.current_tab == tab
            button_style = "primary" if is_active else "secondary"
            if st.button(f"{'🤖' if tab == 'AI Assistant' else '📋' if tab == 'Menu Explorer' else '🛒' if tab == 'Shopping List' else '📅' if tab == 'Meal Planning' else '✨'} {tab}", 
                         key=f"tab_{tab}", use_container_width=True, type=button_style):
                st.session_state.current_tab = tab
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Main content
if st.session_state.current_tab == "AI Assistant":
    with st.expander("🎯 Personalize Your Experience", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            cooking_style = st.selectbox(
                "Preferred Cuisine Style",
                ["Bangladeshi", "South Asian", "Indo-Pakistani", "Middle Eastern", "Fusion", "Traditional"],
                index=0
            )
            spice_level = st.select_slider(
                "Spice Preference",
                options=["Mild", "Medium", "Spicy", "Extra Spicy"],
                value=st.session_state.user_preferences["spice_level"]
            )
        with col2:
            expertise_level = st.select_slider(
                "Cooking Expertise",
                options=["Beginner", "Intermediate", "Advanced", "Professional"],
                value=st.session_state.user_preferences["expertise_level"]
            )
            serving_size = st.selectbox(
                "Typical Serving Size",
                ["2-3 people", "4-6 people", "8-10 people", "Large party (15+ people)"],
                index=1
            )
        with col3:
            dietary_restrictions = st.multiselect(
                "Dietary Preferences",
                ["Halal", "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Low-Carb", "Keto"],
                default=st.session_state.user_preferences["dietary_restrictions"]
            )
        if st.button("Update Preferences"):
            st.session_state.user_preferences.update({
                "cooking_style": cooking_style,
                "expertise_level": expertise_level,
                "dietary_restrictions": dietary_restrictions,
                "spice_level": spice_level,
                "serving_size": serving_size
            })
            st.success("✅ Preferences updated!")
    
    with st.expander("🔍 Debug API Status", expanded=False):
        st.write("API call details will appear here after a query.")
        if 'last_api_status' in st.session_state:
            st.markdown(f"**Last API Call Status**: {st.session_state.last_api_status}")
    
    if not st.session_state.messages:
        st.markdown("""
        ## 👋 Welcome to Shared Skillet AI Professional!
        ### 🌟 What makes us special:
        - **Authentic Menu Integration**: Get recipes from our curated collection
        - **Smart Recommendations**: AI-powered suggestions based on your preferences  
        - **Professional Guidance**: Expert-level cooking instructions and tips
        - **Cultural Authenticity**: Traditional Bangladeshi and South Asian specialties
        ### 💡 Try asking:
        - "Show me your best biryani recipes"
        - "I want something spicy for dinner"
        - "What desserts do you recommend?"
        - "Create a traditional Bangladeshi meal plan"
        - "I have chicken and rice, what can you suggest?"
        """)
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm your Shared Skillet AI assistant. I specialize in authentic Bangladeshi and South Asian cuisine, and I have access to our curated menu of professional dishes. What would you like to cook today? 🍳"
        })
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    prompt = st.chat_input("Ask about our menu, get recipes, or culinary advice...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your request and searching our menu..."):
                relevant_items = smart_menu_search(prompt, limit=5)
                if relevant_items:
                    st.markdown("### 🎯 From Our Professional Menu:")
                    cols = st.columns(min(len(relevant_items[:2]), 2))
                    for idx, item in enumerate(relevant_items[:2]):
                        with cols[idx]:
                            display_menu_item(item, show_video=False)
                    st.markdown("---")
                
                st.markdown("### 👨‍🍳 AI-Powered Response:")
                system_message = generate_enhanced_system_message(purpose="recipe_request", relevant_menu_items=relevant_items)
                api_messages = [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]
                response = call_euron_api(api_messages)
                
                # Log API status
                if response.startswith("Error:"):
                    st.session_state.last_api_status = response
                    st.warning(f"{response}\n\nPlease try again later or contact the API provider for assistance.")
                    # Fallback response using smart_menu_search
                    if relevant_items:
                        fallback = f"Sorry, I couldn't fetch a detailed response due to a server error. Based on your query, I recommend checking out these dishes from our menu:\n"
                        fallback += "\n".join([f"- **{item.dish_name}**: {item.category}, {item.taste_category}" for item in relevant_items])
                        st.markdown(fallback)
                        st.session_state.messages.append({"role": "assistant", "content": fallback})
                    else:
                        st.markdown("No relevant menu items found. Please try a different query or wait for the API to stabilize.")
                        st.session_state.messages.append({"role": "assistant", "content": "No relevant menu items found due to API issues."})
                else:
                    st.session_state.last_api_status = f"Success: API returned valid response with model {EURON_MODEL}"
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.recommended_items = relevant_items

elif st.session_state.current_tab == "Menu Explorer":
    st.markdown("## 📋 Menu Explorer")
    st.markdown("Explore our curated selection of authentic Bangladeshi and South Asian dishes.")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("Search menu...", "")
    with col2:
        category_filter = st.selectbox("Category", ["All"] + sorted(set(item.category for item in MENU_ITEMS)))
    with col3:
        taste_filter = st.selectbox("Taste", ["All"] + sorted(set(item.taste_category for item in MENU_ITEMS)))
    filtered_items = MENU_ITEMS
    if search_query:
        filtered_items = smart_menu_search(search_query, limit=len(MENU_ITEMS))
    if category_filter != "All":
        filtered_items = [item for item in filtered_items if item.category == category_filter]
    if taste_filter != "All":
        filtered_items = [item for item in filtered_items if item.taste_category == taste_filter]
    for i in range(0, len(filtered_items), 3):
        cols = st.columns(3, gap="medium")
        for j, item in enumerate(filtered_items[i:i+3]):
            with cols[j]:
                display_menu_item(item)

elif st.session_state.current_tab == "Shopping List":
    st.markdown("## 🛒 Shopping List")
    st.markdown("Manage ingredients needed for your selected dishes.")
    if not st.session_state.shopping_list:
        st.info("Your shopping list is empty. Add items from the Menu Explorer or AI Assistant!")
    else:
        st.markdown('<div class="shopping-list">', unsafe_allow_html=True)
        for dish_name, items in st.session_state.shopping_list.items():
            st.markdown(f"### {dish_name}")
            for item in items:
                st.markdown(f"- {item}")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Clear Shopping List"):
            st.session_state.shopping_list = {}
            st.success("✅ Shopping list cleared!")
            st.rerun()

elif st.session_state.current_tab == "Meal Planning":
    st.markdown("## 📅 Meal Planning")
    st.markdown("Plan your meals with our AI-powered suggestions.")
    col1, col2 = st.columns([2, 1])
    with col1:
        days = st.slider("Select number of days to plan", 1, 7, 3)
    with col2:
        meals_per_day = st.selectbox("Meals per day", [1, 2, 3], index=1)
    if st.button("Generate Meal Plan"):
        with st.spinner("Creating your personalized meal plan..."):
            system_message = generate_enhanced_system_message(purpose="meal_plan")
            prompt = f"""
            Create a {days}-day meal plan with {meals_per_day} meals per day, 
            respecting the following preferences:
            - Cuisine: {st.session_state.user_preferences['cooking_style']}
            - Spice Level: {st.session_state.user_preferences['spice_level']}
            - Dietary Restrictions: {', '.join(st.session_state.user_preferences['dietary_restrictions'])}
            - Serving Size: {st.session_state.user_preferences['serving_size']}
            Prioritize dishes from our menu: {', '.join([item.dish_name for item in MENU_ITEMS])}.
            Format the response as a clear, structured plan with day-wise meal assignments.
            """
            api_messages = [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]
            response = call_euron_api(api_messages)
            if response.startswith("Error:"):
                st.warning(f"{response}\n\nPlease try again later or contact the API provider.")
                st.session_state.meal_plan = {"plan": "Failed to generate meal plan due to API server error."}
            else:
                st.session_state.meal_plan = {"plan": response}
                st.markdown('<div class="meal-plan">', unsafe_allow_html=True)
                st.markdown(response)
                st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.meal_plan.get("plan"):
        st.markdown('<div class="meal-plan">', unsafe_allow_html=True)
        st.markdown("### Current Meal Plan")
        st.markdown(st.session_state.meal_plan["plan"])
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Clear Meal Plan"):
            st.session_state.meal_plan = {}
            st.success("✅ Meal plan cleared!")
            st.rerun()

elif st.session_state.current_tab == "Smart Recommendations":
    st.markdown("## ✨ Smart Recommendations")
    st.markdown("Discover dishes tailored to your preferences and recent interactions.")
    if not st.session_state.recommended_items:
        st.info("No recommendations yet. Interact with the AI Assistant or Menu Explorer to get personalized suggestions!")
    else:
        st.markdown('<div class="smart-suggestion">', unsafe_allow_html=True)
        st.markdown("### Based on Your Recent Activity")
        cols = st.columns(3, gap="medium")
        for idx, item in enumerate(st.session_state.recommended_items[:3]):
            with cols[idx]:
                display_menu_item(item, show_video=False)
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Get More Recommendations"):
            with st.spinner("Generating new recommendations..."):
                system_message = generate_enhanced_system_message(purpose="recommendations")
                prompt = f"""
                Suggest 3 additional dishes from our menu that complement the user's preferences:
                - Cuisine: {st.session_state.user_preferences['cooking_style']}
                - Spice Level: {st.session_state.user_preferences['spice_level']}
                - Dietary Restrictions: {', '.join(st.session_state.user_preferences['dietary_restrictions'])}
                - Serving Size: {st.session_state.user_preferences['serving_size']}
                Current recommendations: {', '.join([item.dish_name for item in st.session_state.recommended_items])}.
                Avoid repeating current recommendations.
                """
                api_messages = [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]
                response = call_euron_api(api_messages)
                if response.startswith("Error:"):
                    st.warning(f"{response}\n\nPlease try again later or contact the API provider.")
                else:
                    new_dish_names = re.findall(r'\b[\w\s]+\b', response)
                    new_recommendations = []
                    for dish_name in new_dish_names:
                        for item in MENU_ITEMS:
                            if dish_name.lower() in item.dish_name.lower() and item not in st.session_state.recommended_items:
                                new_recommendations.append(item)
                                break
                    if new_recommendations:
                        st.session_state.recommended_items.extend(new_recommendations[:3])
                        st.rerun()
                    else:
                        st.warning("No new recommendations found. Try adjusting your preferences!")
