import streamlit as st
import openai
import os
from datetime import datetime, timedelta
import json
import pandas as pd
import re

# Set your OpenAI client using API key from secrets
try:
    client = openai.Client(api_key=st.secrets.get("OPENAI_API_KEY", ""))
except Exception as e:
    st.error("Failed to initialize OpenAI client. Check your API key setup.")

# Page configuration
st.set_page_config(
    page_title="Kitchen Companion",
    page_icon="🍳",
    layout="wide"
)

# Streamlit UI styling
st.markdown("""
<style>
    .main {
        background-color: #f9f7f1;
        color: #333333;
    }
    .stTextInput, .stTextArea {
        background-color: #ffffff;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #f0f0f0;
        border-left: 5px solid #FF9776;
    }
    .chat-message.assistant {
        background-color: #e6f7ff;
        border-left: 5px solid #2E7D32;
    }
    .chat-message p {
        margin: 0;
    }
    .shopping-list {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
    .meal-plan {
        background-color: #fff8e1;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF9800;
    }
    .recipe-card {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        border: 1px solid #ddd;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Replace OpenAI call in extract_preferences

def extract_preferences(message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a system that extracts cooking preferences from user messages. Extract any mentioned cooking style, dietary restrictions, or expertise level. Format as JSON with keys 'cooking_style', 'expertise_level', and 'dietary_restrictions' (array). Only respond with JSON."},
                {"role": "user", "content": message}
            ],
            temperature=0.3,
            max_tokens=500
        )
        try:
            prefs = json.loads(response.choices[0].message.content)
            updated = False
            if "cooking_style" in prefs and prefs["cooking_style"]:
                st.session_state.user_preferences["cooking_style"] = prefs["cooking_style"]
                updated = True
            if "expertise_level" in prefs and prefs["expertise_level"]:
                st.session_state.user_preferences["expertise_level"] = prefs["expertise_level"]
                updated = True
            if "dietary_restrictions" in prefs and prefs["dietary_restrictions"]:
                current = set(st.session_state.user_preferences["dietary_restrictions"])
                new = set(prefs["dietary_restrictions"])
                st.session_state.user_preferences["dietary_restrictions"] = list(current.union(new))
                updated = True
            return updated
        except:
            return False
    except Exception as e:
        print(f"Error extracting preferences: {str(e)}")
        return False

# Replace OpenAI call in extract_ingredients

def extract_ingredients(recipe_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": generate_system_message(purpose="shopping_list")},
                {"role": "user", "content": f"Extract ingredients from this recipe: {recipe_text}"}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        ingredients_json = json.loads(response.choices[0].message.content)
        return ingredients_json
    except Exception as e:
        st.error(f"Error extracting ingredients: {str(e)}")
        return {}

# Replace OpenAI call in generate_meal_plan

def generate_meal_plan():
    try:
        prefs = st.session_state.user_preferences
        preferences = f"Cooking style: {prefs['cooking_style']}, Expertise level: {prefs['expertise_level']}, Dietary restrictions: {', '.join(prefs['dietary_restrictions'])}"
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": generate_system_message(purpose="meal_plan")},
                {"role": "user", "content": f"Create a weekly meal plan based on these preferences: {preferences}"}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        meal_plan_json = json.loads(response.choices[0].message.content)
        return meal_plan_json
    except Exception as e:
        st.error(f"Error generating meal plan: {str(e)}")
        return {}

# Ensure all future OpenAI calls also use client.chat.completions.create
