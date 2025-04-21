import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import json
import pandas as pd
import re

# Page configuration
st.set_page_config(
    page_title="Shared Skillet AI",
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
    /* Hide hamburger menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = {}
if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = {}
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Help"
    st.markdown("""
    ## 👨‍🍳 How to Use Shared Skillet AI

    Shared Skillet AI is your virtual kitchen buddy. Just type like you're chatting with a friend, and it can help you:

    - 🍽️ Suggest recipes using ingredients you have
    - 🧠 Answer cooking questions or give tips
    - 🛒 Build and manage your shopping list
    - 🗓️ Create a full 7-day meal plan tailored to your diet and skill level

    ### 🟢 Try asking:
    - "Give me a vegetarian pasta recipe."
    - "What can I make with chicken, tomatoes, and rice?"
    - "Add this recipe to my shopping list."
    - "Create a weekly keto meal plan for a beginner."

    Switch between tabs to access your **Chat**, **Shopping List**, or **Meal Plan** at any time.
    """)
if 'user_preferences' not in st.session_state:
    # Default preferences - you can customize these
    st.session_state.user_preferences = {
        "cooking_style": "General",
        "expertise_level": "Intermediate",
        "dietary_restrictions": []
    }

# Custom tab UI
tabs = ["Chat", "Shopping List", "Meal Planning"]
cols = st.columns(len(tabs))
for i, tab in enumerate(tabs):
    with cols[i]:
        if st.button(tab, key=f"tab_{tab}", use_container_width=True):
            st.session_state.current_tab = tab
            st.rerun()

# Show current tab
st.markdown(f"## {st.session_state.current_tab}")
st.divider()

# Euron API configuration
EURON_API_URL = "https://api.euron.one/api/v1/euri/alpha/chat/completions"
EURON_MODEL = "gemini-2.5-pro-exp-03-25"
# Access the API key from Streamlit secrets
def get_euron_api_key():
    return st.secrets["euron"]["api_key"]

def call_euron_api(messages, temperature=0.7, max_tokens=1000):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_euron_api_key()}"
    }
    
    payload = {
        "messages": messages,
        "model": EURON_MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        response = requests.post(EURON_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        # Extract content based on Euron API response structure
        if 'choices' in data and len(data['choices']) > 0:
            if 'message' in data['choices'][0] and 'content' in data['choices'][0]['message']:
                return data['choices'][0]['message']['content']
        return "I'm sorry, I couldn't process that request."
    except Exception as e:
        print(f"API error: {str(e)}")
        return f"Error: {str(e)}"

# Function to generate system message based on preferences
def generate_system_message(purpose="general"):
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Use stored preferences
    prefs = st.session_state.user_preferences
    cooking_style = prefs["cooking_style"]
    expertise_level = prefs["expertise_level"]
    diet_string = ", ".join(prefs["dietary_restrictions"]) if prefs["dietary_restrictions"] else "No specific dietary restrictions"
    
    base_system_message = f"""
    You are a specialized cooking assistant with expertise in various cuisines and cooking techniques. 
    Today is {current_date}.
    
    Current preferences:
    - Cooking Style Focus: {cooking_style}
    - Expertise Level: {expertise_level}
    - Dietary Restrictions: {diet_string}
    
    Guidelines:
    1. Provide clear, step-by-step cooking instructions when sharing recipes
    2. Suggest ingredient substitutions when appropriate, especially for dietary restrictions
    3. Explain cooking techniques at the appropriate level
    4. Include cooking times, temperatures, and yields where relevant
    5. Offer tips for food preparation, storage, and safety
    
    Always prioritize food safety and proper handling techniques in your advice.
    
    The user can:
    - Ask for recipes
    - Add recipes to their shopping list by saying "add this to my shopping list"
    - Request a meal plan by asking for one
    - Ask cooking questions
    
    Help the user accomplish their cooking goals regardless of their experience level.
    """
    
    if purpose == "shopping_list":
        return base_system_message + """
        For extracting shopping list ingredients:
        1. Extract ingredients from the recipe in a structured format
        2. Group ingredients by category (produce, dairy, meat, pantry items, etc.)
        3. Specify quantities and units clearly
        4. Format your response as a JSON object with the following structure:
        {
            "produce": [{"item": "tomato", "quantity": "2", "unit": "medium"}],
            "dairy": [{"item": "milk", "quantity": "1", "unit": "cup"}],
            "meat": [],
            "pantry": [],
            "spices": [],
            "other": []
        }
        Only respond with the JSON. Do not include any explanations or additional text.
        """
    
    elif purpose == "meal_plan":
        return base_system_message + """
        For creating a meal plan:
        1. Create a 7-day meal plan with breakfast, lunch, and dinner options
        2. Follow any dietary preferences and restrictions
        3. Keep recipes appropriate to the skill level
        4. Include variety across the week
        5. Format your response as a JSON object with the following structure:
        {
            "monday": {
                "breakfast": {"title": "Avocado Toast", "description": "Simple avocado toast with eggs", "prep_time": "15 minutes"},
                "lunch": {"title": "Mediterranean Salad", "description": "Fresh salad with feta and olives", "prep_time": "20 minutes"},
                "dinner": {"title": "Pasta Primavera", "description": "Seasonal vegetables with pasta", "prep_time": "30 minutes"}
            },
            "tuesday": {
                "breakfast": {},
                "lunch": {},
                "dinner": {}
            },
            ...and so on for each day of the week...
        }
        Only respond with the JSON. Do not include any explanations or additional text.
        """
    
    return base_system_message

# Function to extract preferences from user messages
def extract_preferences(message):
    try:
        # Call Euron API to extract preferences
        system_content = "You are a system that extracts cooking preferences from user messages. Extract any mentioned cooking style, dietary restrictions, or expertise level. Format as JSON with keys 'cooking_style', 'expertise_level', and 'dietary_restrictions' (array). Only respond with JSON."
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": message}
        ]
        
        response_content = call_euron_api(messages, temperature=0.3, max_tokens=500)
        
        # Extract JSON from response
        try:
            # Find JSON in the response
            json_match = re.search(r'({.+})', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                prefs = json.loads(json_str)
            else:
                prefs = json.loads(response_content)
            
            # Update preferences if new ones were found
            updated = False
            
            if "cooking_style" in prefs and prefs["cooking_style"]:
                st.session_state.user_preferences["cooking_style"] = prefs["cooking_style"]
                updated = True
                
            if "expertise_level" in prefs and prefs["expertise_level"]:
                st.session_state.user_preferences["expertise_level"] = prefs["expertise_level"]
                updated = True
                
            if "dietary_restrictions" in prefs and prefs["dietary_restrictions"]:
                # Add new restrictions without duplicates
                current = set(st.session_state.user_preferences["dietary_restrictions"])
                new = set(prefs["dietary_restrictions"])
                st.session_state.user_preferences["dietary_restrictions"] = list(current.union(new))
                updated = True
                
            return updated
            
        except Exception as e:
            print(f"Error parsing preferences JSON: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error extracting preferences: {str(e)}")
        return False

# Function to extract ingredients from recipe text
def extract_ingredients(recipe_text):
    try:
        # Call Euron API to extract ingredients in structured format
        messages = [
            {"role": "system", "content": generate_system_message(purpose="shopping_list")},
            {"role": "user", "content": f"Extract ingredients from this recipe: {recipe_text}"}
        ]
        
        response_content = call_euron_api(messages, temperature=0.3, max_tokens=1000)
        
        # Parse the response as JSON
        try:
            # Find JSON in the response
            json_match = re.search(r'({.+})', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                ingredients_json = json.loads(json_str)
            else:
                ingredients_json = json.loads(response_content)
            
            return ingredients_json
        except Exception as e:
            print(f"Error parsing ingredients JSON: {str(e)}")
            return {}
    except Exception as e:
        st.error(f"Error extracting ingredients: {str(e)}")
        return {}

# Function to generate a meal plan
def generate_meal_plan():
    try:
        # Get preferences for the meal plan
        prefs = st.session_state.user_preferences
        preferences = f"Cooking style: {prefs['cooking_style']}, Expertise level: {prefs['expertise_level']}, Dietary restrictions: {', '.join(prefs['dietary_restrictions'])}"
        
        # Call Euron API to generate a meal plan
        messages = [
            {"role": "system", "content": generate_system_message(purpose="meal_plan")},
            {"role": "user", "content": f"Create a weekly meal plan based on these preferences: {preferences}"}
        ]
        
        response_content = call_euron_api(messages, temperature=0.7, max_tokens=2000)
        
        # Parse the response as JSON
        try:
            # Find JSON in the response
            json_match = re.search(r'({.+})', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                meal_plan_json = json.loads(json_str)
            else:
                meal_plan_json = json.loads(response_content)
            
            return meal_plan_json
        except Exception as e:
            print(f"Error parsing meal plan JSON: {str(e)}")
            return {}
    except Exception as e:
        st.error(f"Error generating meal plan: {str(e)}")
        return {}

# Function to add items to shopping list
def add_to_shopping_list(ingredients):
    for category, items in ingredients.items():
        if category not in st.session_state.shopping_list:
            st.session_state.shopping_list[category] = []
        
        # Add new items or update quantities of existing items
        for new_item in items:
            item_exists = False
            for existing_item in st.session_state.shopping_list[category]:
                if existing_item["item"].lower() == new_item["item"].lower():
                    # Item exists, try to update quantity if possible
                    try:
                        if existing_item["unit"] == new_item["unit"]:
                            existing_item["quantity"] = str(float(existing_item["quantity"]) + float(new_item["quantity"]))
                        else:
                            # If units don't match, just add as separate item
                            st.session_state.shopping_list[category].append(new_item)
                    except:
                        # If conversion fails, just add as a new item
                        st.session_state.shopping_list[category].append(new_item)
                    item_exists = True
                    break
            
            if not item_exists:
                st.session_state.shopping_list[category].append(new_item)

# Main content based on current tab
if st.session_state.current_tab == "Chat":
    # Optional user preferences (hidden by default)
    with st.expander("Customize Your Experience", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            cooking_style = st.selectbox(
                "Cooking Style Preference",
                ["General", "Italian", "Mexican", "Asian", "Mediterranean", "Indian", "French", "American", "Vegetarian", "Vegan"],
                index=["General", "Italian", "Mexican", "Asian", "Mediterranean", "Indian", "French", "American", "Vegetarian", "Vegan"].index(st.session_state.user_preferences["cooking_style"])
            )
            
            if cooking_style != st.session_state.user_preferences["cooking_style"]:
                st.session_state.user_preferences["cooking_style"] = cooking_style
        
        with col2:
            expertise_level = st.select_slider(
                "Your Cooking Expertise",
                options=["Beginner", "Intermediate", "Advanced", "Professional"],
                value=st.session_state.user_preferences["expertise_level"]
            )
            
            if expertise_level != st.session_state.user_preferences["expertise_level"]:
                st.session_state.user_preferences["expertise_level"] = expertise_level
        
        dietary_restrictions = st.multiselect(
            "Dietary Preferences or Restrictions",
            ["Gluten-Free", "Dairy-Free", "Nut-Free", "Vegetarian", "Vegan", "Low-Carb", "Low-Sugar", "Keto", "Paleo"],
            default=st.session_state.user_preferences["dietary_restrictions"]
        )
        
        if dietary_restrictions != st.session_state.user_preferences["dietary_restrictions"]:
            st.session_state.user_preferences["dietary_restrictions"] = dietary_restrictions
    
    # Intro message for new users
    if not st.session_state.messages:
        st.markdown("""
        ## 👋 Welcome to Shared Skillet AI!
        You can visit sharedskillet.com and view some ready made recipes. You can also share your own recipes with community.
        
        I'm your AI cooking assistant, ready to help with:
        
        - 🍲 **Recipe ideas and cooking instructions**
        - 📝 **Meal planning** for the week
        - 🛒 **Shopping list generation** from recipes
        - 💡 **Cooking techniques and tips**
        
        Just ask me anything about cooking! Try these examples:
        - "I need a quick pasta recipe for dinner"
        - "How do I make sourdough bread?"
        - "Create a meal plan for the week"
        - "What can I cook with chicken, broccoli and rice?"
        """)
        
        # Add default welcome message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hello! I'm Shared Skillet AI: your cooking assistant. What would you like to cook today?"
        })
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # New message input
    prompt = st.chat_input("Ask me anything about cooking...")

    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Extract preferences if any are mentioned
        extract_preferences(prompt)
        
        # Check if this is a request to add to shopping list or create meal plan
        shopping_list_request = re.search(r"add (this|these|the) (recipe|ingredients) to (my )?(shopping|grocery) list", prompt.lower())
        meal_plan_request = re.search(r"(create|make|generate) (a )?(meal|weekly|menu) plan", prompt.lower())
        
        # Display assistant response with a spinner
        with st.chat_message("assistant"):
            with st.spinner("Cooking up a response..."):
                # Create the messages array for the API call
                messages = [
                    {"role": "system", "content": generate_system_message()}
                ]
                
                # Add all conversation history
                for msg in st.session_state.messages:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                
                # Call Euron API
                try:
                    response_content = call_euron_api(messages, temperature=0.7, max_tokens=1000)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response_content})
                    
                    # Display assistant response
                    st.write(response_content)
                    
                    # Handle shopping list requests
                    if shopping_list_request:
                        # Look at the last few messages to find recipe content
                        recent_messages = st.session_state.messages[-5:]  # Get last 5 messages
                        recipe_text = ""
                        for msg in recent_messages:
                            if msg["role"] == "assistant" and len(msg["content"]) > 100:  # Likely a recipe
                                recipe_text = msg["content"]
                                break
                        
                        if recipe_text:
                            with st.spinner("Adding to shopping list..."):
                                ingredients = extract_ingredients(recipe_text)
                                if ingredients:
                                    add_to_shopping_list(ingredients)
                                    st.success("✅ Ingredients added to your shopping list! Go to the Shopping List tab to view them.")
                    
                    # Handle meal plan requests
                    if meal_plan_request:
                        with st.spinner("Creating your meal plan..."):
                            meal_plan = generate_meal_plan()
                            if meal_plan:
                                st.session_state.meal_plan = meal_plan
                                st.success("✅ Meal plan created! Go to the Meal Planning tab to view it.")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.error("Something went wrong. Please try again later.")

elif st.session_state.current_tab == "Shopping List":
    # Empty shopping list message
    if not st.session_state.shopping_list:
        st.info("Your shopping list is empty. Get recipes in the chat and add them to your list!")
        
        # Button to go back to chat
        if st.button("Ask for Recipe Ideas"):
            st.session_state.current_tab = "Chat"
            st.rerun()
    else:
        # Display shopping list by category
        col1, col2 = st.columns([3, 1])
        
        with col1:
            for category, items in st.session_state.shopping_list.items():
                if items:  # Only show categories with items
                    st.subheader(f"{category.capitalize()}")
                    
                    for i, item in enumerate(items):
                        col_a, col_b, col_c = st.columns([1, 3, 1])
                        with col_a:
                            if st.checkbox("", key=f"item_{category}_{i}"):
                                # Mark as purchased (to implement)
                                pass
                        with col_b:
                            st.write(f"{item['quantity']} {item['unit']} {item['item']}")
                        with col_c:
                            if st.button("Remove", key=f"remove_{category}_{i}"):
                                st.session_state.shopping_list[category].pop(i)
                                st.rerun()
            
        with col2:
            st.subheader("Actions")
            if st.button("Clear Shopping List"):
                st.session_state.shopping_list = {}
                st.rerun()
            
            if st.button("Export as CSV"):
                # Convert to dataframe
                shopping_data = []
                for category, items in st.session_state.shopping_list.items():
                    for item in items:
                        shopping_data.append({
                            "Category": category,
                            "Item": item["item"],
                            "Quantity": item["quantity"],
                            "Unit": item["unit"]
                        })
                
                df = pd.DataFrame(shopping_data)
                
                # Create a download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="shopping_list.csv",
                    mime="text/csv",
                )
            
            st.divider()
            
            st.subheader("Add Item Manually")
            with st.form("add_item_form"):
                new_category = st.selectbox("Category", ["produce", "dairy", "meat", "pantry", "spices", "other"])
                new_item = st.text_input("Item")
                col_qty, col_unit = st.columns(2)
                with col_qty:
                    new_quantity = st.text_input("Quantity", "1")
                with col_unit:
                    new_unit = st.selectbox("Unit", ["", "piece", "lb", "oz", "cup", "tbsp", "tsp", "can", "package"])
                
                if st.form_submit_button("Add Item"):
                    if new_item:
                        if new_category not in st.session_state.shopping_list:
                            st.session_state.shopping_list[new_category] = []
                        
                        st.session_state.shopping_list[new_category].append({
                            "item": new_item,
                            "quantity": new_quantity,
                            "unit": new_unit
                        })
                        st.success(f"Added {new_item} to shopping list!")
                        st.rerun()

elif st.session_state.current_tab == "Meal Planning":
    # Empty meal plan message
    if not st.session_state.meal_plan:
        st.info("You haven't created a meal plan yet.")
        
        # Button to create a meal plan
        if st.button("Create a Meal Plan Now"):
            with st.spinner("Creating your personalized meal plan..."):
                meal_plan = generate_meal_plan()
                if meal_plan:
                    st.session_state.meal_plan = meal_plan
                    st.rerun()
                else:
                    st.error("Failed to create meal plan. Please try again.")
        
        # Button to go back to chat
        if st.button("Ask About Meal Planning"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "I'd like you to create a meal plan for me. Can you help with that?"
            })
            st.session_state.current_tab = "Chat"
            st.rerun()
    else:
        # Display meal plan
        days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        meal_types = ["breakfast", "lunch", "dinner"]
        
        # Date display for the week
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        dates = {days_of_week[i]: (start_of_week + timedelta(days=i)).strftime('%b %d') for i in range(7)}
        
        # Actions for meal plan
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.subheader("Your Weekly Meal Plan")
        with col3:
            if st.button("Create New Plan"):
                st.session_state.meal_plan = {}
                st.rerun()
            
            if st.button("Add All to Shopping List"):
                # Extract all ingredients from all meals
                all_meals_text = ""
                for day in days_of_week:
                    if day in st.session_state.meal_plan:
                        for meal_type in meal_types:
                            if meal_type in st.session_state.meal_plan[day] and st.session_state.meal_plan[day][meal_type]:
                                meal = st.session_state.meal_plan[day][meal_type]
                                all_meals_text += f"{meal['title']}: {meal['description']}\n"
                
                with st.spinner("Adding ingredients to shopping list..."):
                    ingredients = extract_ingredients(all_meals_text)
                    if ingredients:
                        add_to_shopping_list(ingredients)
                        st.success("✅ All meal ingredients added to your shopping list!")
        
        # Display the meal plan in a calendar view
        for day in days_of_week:
            if day in st.session_state.meal_plan:
                with st.expander(f"{day.capitalize()} ({dates[day]})", expanded=True):
                    # Three columns for breakfast, lunch, dinner
                    cols = st.columns(3)
                    
                    for i, meal_type in enumerate(meal_types):
                        with cols[i]:
                            st.subheader(meal_type.capitalize())
                            
                            if meal_type in st.session_state.meal_plan[day] and st.session_state.meal_plan[day][meal_type]:
                                meal = st.session_state.meal_plan[day][meal_type]
                                
                                st.markdown(f"""
                                <div class="recipe-card">
                                    <h4>{meal['title']}</h4>
                                    <p>{meal['description']}</p>
                                    <p><strong>Prep time:</strong> {meal['prep_time']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.button(f"Get Recipe", key=f"recipe_{day}_{meal_type}"):
                                    # Add message to chat history asking for this recipe
                                    st.session_state.messages.append({
                                        "role": "user", 
                                        "content": f"Please give me a detailed recipe for {meal['title']} ({meal['description']})"
                                    })
                                    st.session_state.current_tab = "Chat"
                                    st.rerun()
                                
                                if st.button(f"Add to Shopping List", key=f"shop_{day}_{meal_type}"):
                                    with st.spinner("Adding to shopping list..."):
                                        meal_text = f"{meal['title']}: {meal['description']}"
                                        ingredients = extract_ingredients(meal_text)
                                        if ingredients:
                                            add_to_shopping_list(ingredients)
                                            st.success(f"✅ Added {meal['title']} ingredients to shopping list!")
                            else:
                                st.write("No meal planned")

# Add a small custom footer
st.markdown("""
<div style="text-align: center; margin-top: 30px; font-size: 0.8em; color: #666;">
    Shared Skillet AI | Your personal AI cooking assistant
</div>
""", unsafe_allow_html=True)
