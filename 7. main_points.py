import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import os
import re
from PIL import Image

# Persistent Storage Paths
CSV_FILE = "eco_logs.csv"
POINTS_FILE = "total_points.pkl"
LEADERBOARD_FILE = "leaderboard.csv"

# Fixed Points per Category (excluding trees)
categories = {
    "Daily Habits/Small Scale": 50, "Large Scale": 150, "Medium Scale": 75, "Transportation": 70,
    "Food & Lifestyle": 60, "Waste Reduction": 70, "Eco-Friendly Shopping": 60, "Home Sustainability": 80,
    "Digital Consciousness": 50, "Community Involvement": 80, "Sustainable Energy Usage": 90,
    "Water Conservation": 70, "Eco-Friendly Commuting": 75, "Green Spaces & Biodiversity": 85,
    "Minimalist Living": 65, "Responsible Tourism": 80, "Sustainable Technology": 75,
    "Environmental Activism & Awareness": 90, "Zero-Waste Living": 85, "Upcycling & DIY Sustainability": 75,
    "Eco-Conscious Pet Care": 60, "Ethical Consumption": 70, "Climate Change Action": 95,
    "Sustainable Food Choices": 75, "Circular Economy Participation": 80,
    "Community-Based Sustainability": 85, "Sustainable Event Planning": 70, "Eco-Friendly Home Design": 90,
    "Others": 50
}

# Load Logs
def load_logs():
    try:
        return pd.read_csv(CSV_FILE).values.tolist()
    except FileNotFoundError:
        return []

# Load Points
def load_points():
    try:
        with open(POINTS_FILE, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return 0

# Save Points
def save_points(points):
    with open(POINTS_FILE, "wb") as f:
        pickle.dump(points, f)

# Tree Growth Rewards
def tree_stage(points_total):
    if points_total < 100:
        return "🌱 Seedling"
    elif points_total < 250:
        return "🌿 Sapling"
    elif points_total < 500:
        return "🌳 Young Tree"
    elif points_total < 1000:
        return "🌲 Mature Tree"
    else:
        return "🌴 Eco Champion Tree"

# Leaderboard Handling
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        return pd.read_csv(LEADERBOARD_FILE)
    return pd.DataFrame(columns=["User", "Points"])

def save_leaderboard(user, points):
    df = load_leaderboard()
    
    if user in df["User"].values:
        df.loc[df["User"] == user, "Points"] += points
    else:
        new_entry = pd.DataFrame([{"User": user, "Points": points}])
        df = pd.concat([df, new_entry], ignore_index=True)
    
    df.to_csv(LEADERBOARD_FILE, index=False)

# Carbon Footprint Estimation
def estimate_carbon_impact(points):
    return round(points * 0.05, 2)  # Dummy calculation: Each action reduces 0.05kg CO2

# Extract number of trees planted from user input
def calculate_tree_points(task_text):
    numbers = re.findall(r'\d+', task_text)
    if numbers:
        num_trees = max(map(int, numbers))  # Get the highest number in input
        return 50 + (num_trees - 1) * 5  # Base 50 points + 5 points per extra tree
    return 0  # If no trees are mentioned, return 0

# Streamlit UI
st.title("🌍 Eco-Tracking Dashboard")

user_name = st.text_input("Enter your name", key="user_name")

task = st.text_area("Describe your eco-action", key="task_input")
category = st.multiselect("Select a category", list(categories.keys()), max_selections=1)
uploaded_image = st.file_uploader("Upload an image (bonus +10pts)", type=['png', 'jpg', 'jpeg'])

if st.button("Submit Action"):
    if not category:
        st.warning("⚠️ Please select a category.")
    else:
        base_points = categories.get(category[0], 0)
        tree_points = calculate_tree_points(task)
        bonus_points = 10 if uploaded_image else 0
        total_points = load_points() + base_points + tree_points + bonus_points
        save_points(total_points)

        if user_name:
            save_leaderboard(user_name, base_points + tree_points + bonus_points)

        st.success(f"✅ Logged: '{task}' | 📂 Category: {category[0]} | 🎉 Base Points: {base_points}")
        if tree_points:
            st.success(f"🌳 Tree Planting Bonus: +{tree_points} Points!")
        if bonus_points:
            st.success(f"📸 Image Upload Bonus: +{bonus_points} Points!")
        
        st.metric("Total Points", total_points)
        st.markdown(f"🏆 Growth Stage: **{tree_stage(total_points)}**")
        st.markdown(f"🌿 Carbon Impact: **-{estimate_carbon_impact(total_points)} kg CO₂**")

        if uploaded_image:
            try:
                image = Image.open(uploaded_image.getvalue())
                st.image(image, caption="Uploaded Image", use_column_width=True)
            except Exception as e:
                st.error(f"Error processing image: {e}")

# Leaderboard Section
st.subheader("🌍 Leaderboard")
leaderboard_df = load_leaderboard()
st.table(leaderboard_df.sort_values(by="Points", ascending=False))

# Progress Reports (Visualization)
st.subheader("📊 Personalized Progress Reports")
df_progress = pd.DataFrame({"Categories": categories.keys(), "Points": categories.values()})
fig, ax = plt.subplots()
ax.bar(df_progress["Categories"], df_progress["Points"], color="green")
plt.xticks(rotation=90)
st.pyplot(fig)

# Habit Tracker
st.subheader("🔄 Habit Tracker")
habit = st.text_input("Set an Eco-Goal (e.g., 'Compost weekly')", key="habit_input")
if st.button("Track Goal"):
    st.success(f"🎯 Goal set: {habit}")

# Eco-Friendly Recommendations
st.subheader("🛒 Eco-Friendly Recommendations")
if task:
    if "Plastic" in task.lower():
        st.markdown("🔄 Recommended: **Reusable Water Bottles, Cloth Bags**")
    elif "transport" in task.lower():
        st.markdown("🚲 Recommended: **Public Transport, Bike Rides**")

# Community Stories & Sharing
st.subheader("💬 Community Stories")
story = st.text_area("Share your eco-success story", key="story_input")
if st.button("Post Story"):
    st.success("🎉 Your story has been shared!")

# Local Sustainability Resources (Mock Data)
st.subheader("📍 Local Sustainability Resources")
resources = pd.DataFrame({"Place": ["Recycling Center", "Organic Market", "Solar Panel Supplier"], "Location": ["Downtown", "Main Street", "Eco Park"]})
st.table(resources)
