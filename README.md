# 🍳 Shared Skillet AI – Your Personal AI Cooking Companion

**Shared Skillet AI** is a smart, interactive cooking assistant powered by OpenAI and Streamlit. Whether you're planning meals for the week or need a quick dinner recipe, this AI chef has you covered—offering real-time recipes, ingredient lists, and meal planning tailored to your preferences and dietary needs.

---

## ✨ Features

### 💬 AI Cooking Chatbot
- Ask questions about cooking techniques, ingredients, or substitutions.
- Get personalized recipe suggestions with step-by-step instructions.
- Learns your preferences through conversation.

### 🛒 Interactive Shopping List
- Extracts structured ingredient lists from any recipe.
- Organizes by category: produce, dairy, pantry, etc.
- Add/remove items manually and export to CSV.

### 📅 Weekly Meal Planner
- Automatically generates a 7-day plan (breakfast, lunch, dinner).
- Respects dietary preferences, skill level, and cooking style.
- Easily pull recipes from the plan into your shopping list.

### ⚙️ Customizable Experience
- Adjust your cooking style (e.g., Indian, Mediterranean).
- Set your experience level (Beginner to Pro).
- Define multiple dietary restrictions (Vegan, Gluten-Free, Keto, etc.).

---

## 🛠️ Built With

- **Streamlit** for UI
- **OpenAI GPT-3.5 / GPT-4** for intelligent language understanding
- **Python** for backend logic
- **Pandas** for data handling and export

---

## 🔐 Setup Secrets

Create a `.streamlit/secrets.toml` file:

```toml
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
