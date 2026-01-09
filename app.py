import streamlit as st
from PIL import Image
import random
import os
import json

# Load the image configuration
with open('image_config.json', 'r') as f:
    IMAGE_CONFIG = json.load(f)

# Helper mapping for display names to JSON keys
MODE_MAP = {
    "US State Capitals": "us_state_capitals",
    "Top 20 US Metros": "us_top20_metros",
    "10 Largest US Cities": "us_top10_cities",
    "20 Largest US Cities": "us_top20_cities",
    "30 Largest US Cities": "us_top30_cities"
}

# --- Configuration ---
IMAGE_FOLDER = "images" 

st.set_page_config(page_title="City Guess Game", layout="wide") 

st.title("🏙️ Bird's Eye View")
st.markdown("---")

# --- Initial Setup ---

if not os.path.isdir(IMAGE_FOLDER):
    st.error(f"Image folder not found: Please create a directory named '{IMAGE_FOLDER}' next to this app file.")
    st.stop()

image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".png",".jpg",".jpeg"))]

if not image_files:
    st.error(f"No images found in the /{IMAGE_FOLDER} folder. Please add some city images.")
    st.stop()

# --- Session State Initialization ---

# Store the original list for resetting the game later
if "original_image_files" not in st.session_state:
    st.session_state.original_image_files = image_files.copy()

if "image_queue" not in st.session_state:
    st.session_state.image_queue = image_files.copy()
    random.shuffle(st.session_state.image_queue)

if "game_state" not in st.session_state:
    st.session_state.game_state = "start_screen"

if "game_mode" not in st.session_state:
    st.session_state.game_mode= "us_state_capitals"

if "hard_mode_enabled" not in st.session_state:
    st.session_state.hard_mode_enabled = False

if "total_image_count" not in st.session_state:
    st.session_state.total_image_count = len(image_files)

if "current_image" not in st.session_state:
    st.session_state.current_image = None

if "prev_guess" not in st.session_state:
    st.session_state.prev_guess = None
if "prev_answer" not in st.session_state:
    st.session_state.prev_answer = None
if "prev_was_correct" not in st.session_state:
    st.session_state.prev_was_correct = None 

if "guess_input_key" not in st.session_state:
    st.session_state.guess_input_key = ""
    
if "input_error" not in st.session_state:
    st.session_state['input_error'] = ""

if "total_games" not in st.session_state:
    st.session_state.total_games = 0
if "total_wins" not in st.session_state:
    st.session_state.total_wins = 0

if "history" not in st.session_state:
    st.session_state.history = []
# --- Control Functions ---

def return_to_main_menu():
    """Resets game variables and transitions back to the start screen."""
    # Reset the navigation controls
    st.session_state.game_state = "start_screen"
    st.session_state.current_image = None  # This is the "Key" to leaving the end screen
    
    # Reset the game data
    st.session_state.total_games = 0
    st.session_state.total_wins = 0
    st.session_state.history = []
    st.session_state.prev_guess = None
    st.session_state.prev_answer = None
    st.session_state.prev_was_correct = None
    
    # Refresh image queue for the next game
    st.session_state.image_queue = st.session_state.original_image_files.copy()
    random.shuffle(st.session_state.image_queue)
                    
def set_mode_and_start(hard_mode=False, category=None):
    """Filters images by category and starts the game."""
    st.session_state.hard_mode_enabled = hard_mode
    
    # Filter images based on the selected category from JSON
    filtered_images = [
        item['filename'] for item in IMAGE_CONFIG 
        if category in item['category']
    ]
    
    if not filtered_images:
        st.error(f"No images found for category: {category}")
        return

    # Initialize the queue with ONLY the filtered images
    st.session_state.image_queue = filtered_images.copy()
    random.shuffle(st.session_state.image_queue)
    st.session_state.total_image_count = len(st.session_state.image_queue)
    
    # Pick the first image and go
    st.session_state.current_image = st.session_state.image_queue.pop()
    st.session_state.game_state = "playing"
    st.rerun()


def handle_submit():
    guess = st.session_state.guess_input_key.strip().lower()
    
    if not guess:
        st.session_state['input_error'] = "Please enter a guess."
        return 
        
    st.session_state['input_error'] = ""
    
    # 1. Find the current image data in your IMAGE_CONFIG
    # (Assuming current_image stores the filename like "new_york_city.jpg")
    current_data = next((item for item in IMAGE_CONFIG if item["filename"] == st.session_state.current_image), None)
    
    if current_data:
        # The "Primary" answer derived from filename
        primary_answer = os.path.splitext(current_data["filename"])[0].replace('_', ' ').lower()
        
        # The list of acceptable aliases from JSON (normalized to lowercase)
        aliases = [a.lower() for a in current_data.get("aliases", [])]
        
        # 2. CHECK FOR MATCH
        # Correct if guess matches the filename OR any alias
        is_correct = (guess == primary_answer) or (guess in aliases)
        
        # Use the filename-based name for display (looks better than "nyc")
        display_answer = primary_answer.title()
    else:
        # Fallback logic if JSON lookup fails
        primary_answer = os.path.splitext(st.session_state.current_image)[0].replace('_', ' ').lower()
        is_correct = guess == primary_answer
        display_answer = primary_answer.title()

    # --- RECORD HISTORY & UPDATE SCORE ---
    st.session_state.history.append({
        "Image": st.session_state.total_games + 1,
        "Your Guess": guess.title(),
        "Correct Answer": display_answer,
        "Result": "✅" if is_correct else "❌"
    })

    st.session_state.total_games += 1 
    if is_correct:
        st.session_state.total_wins += 1

    st.session_state.prev_guess = guess
    st.session_state.prev_answer = st.session_state.current_image 
    st.session_state.prev_was_correct = is_correct 
    
    # 3. Load next image or end game
    if st.session_state.image_queue:
        st.session_state.current_image = st.session_state.image_queue.pop()
    else:
        st.session_state.current_image = "END_OF_GAME"
        
    st.session_state.guess_input_key = ""

# ====================================================================
# --- MAIN APP FLOW ---
# ====================================================================

if st.session_state.game_state == "start_screen":
    st.info("The goal is to guess the US cities shown in the satellite image.")

    # 1. Category Selection (Horizontal to save space)
    st.header("1. Select Game Type")
    selected_mode_display = st.radio(
        "Which cities would you like to guess?",
        options=list(MODE_MAP.keys()),
        horizontal=True,
    )

    st.header("Choose Your Difficulty")
    col_start1, col_start2 = st.columns(2)
    
    # Get the internal key (e.g., 'us_state_capitals') from the display name
    chosen_category = MODE_MAP[selected_mode_display]

    with col_start1:
        # IMPORTANT: Pass the chosen_category here
        if st.button("Start Easy Game", use_container_width=True):
            set_mode_and_start(hard_mode=False, category=chosen_category)

    with col_start2:
        # IMPORTANT: Pass the chosen_category here
        if st.button("Start Hard Game (Rotated)", use_container_width=True):
            set_mode_and_start(hard_mode=True, category=chosen_category)
            
    st.markdown("---")
    st.caption(f"Total cities available: {st.session_state.total_image_count}")

elif st.session_state.current_image == "END_OF_GAME":
    st.balloons()
    st.header("🎉 Game Over!")
    
    # 1. Show final round feedback
    if st.session_state.prev_guess:
        st.subheader("Final Round Results")
        if st.session_state.prev_was_correct:
            st.success(f"**CORRECT!** Final guess: **{st.session_state.prev_guess}**")
        else:
            st.error(f"**INCORRECT.** Final guess: **{st.session_state.prev_guess}**")
        
        # Fixing .title() call in case filename has extension
        clean_answer = os.path.splitext(st.session_state.prev_answer)[0].replace('_', ' ')
        st.info(f"The last city was: **{clean_answer.title()}**")
    
    st.divider()
    
    # 2. Show Overall Summary
    st.subheader("Game Summary")
    
    # Calculate accuracy safely to avoid division by zero
    accuracy = (st.session_state.total_wins / st.session_state.total_games * 100) if st.session_state.total_games > 0 else 0
    
    st.metric("Final Accuracy", f"{accuracy:.1f}%")
    st.write(f"You got {st.session_state.total_wins} out of {st.session_state.total_games} correct.")
        # 3. Single Return Button (with unique key)
    if st.button("Return to Main Menu", key="final_return_btn"):
        st.session_state.history = [] 
        return_to_main_menu()
        st.rerun()
    st.markdown("---") 

    st.table(st.session_state.history)





elif st.session_state.game_state == "playing":
    
    col1, col2 = st.columns([1, 1]) 

    # --------------------------------
    # COLUMN 1: IMAGE DISPLAY
    # --------------------------------
    with col1:
        st.subheader("❓ Current City to Guess")
        
        img_path = os.path.join(IMAGE_FOLDER, st.session_state.current_image)
        try:
            img = Image.open(img_path)
            
            # Rotation logic (Conditional based on hard_mode_enabled)
            if st.session_state.hard_mode_enabled:
                rotation_angle = random.choice([0, 90, 180, 270]) 
                if rotation_angle > 0:
                    img = img.rotate(rotation_angle, expand=True) 
                caption_text = "Image is randomly rotated (Hard Mode)"
            else:
                rotation_angle = 0
                caption_text = "Image is in original orientation (Easy Mode)"
            
            st.image(img, caption=caption_text) 
        except FileNotFoundError:
            st.error(f"Error: Image file not found at {img_path}")
            st.stop()
            
    # --------------------------------
    # COLUMN 2: SCORECARD, RESULTS, AND GUESS FORM
    # --------------------------------
    with col2:
        st.subheader("Score and Play Area")
        stat_col1, stat_col2 = st.columns([2,1])

        with stat_col1:
            current_game_number = st.session_state.total_games + 1
            total_images = st.session_state.total_image_count
            st.markdown(f"**Progress:** {current_game_number} / {total_images}")
            st.progress(current_game_number / total_images)

        with stat_col2:
            total_games = st.session_state.total_games
            total_wins = st.session_state.total_wins
            win_pct = (total_wins / total_games * 100) if total_games > 0 else 0
            
            st.metric(
                label="Win Rate", 
                value=f"{win_pct:.1f}%", 
                delta=f"{total_wins} Wins" if total_games > 0 else None
            )
        
        st.markdown("---") 

        # Form for Guessing
        with st.form(key="city_guess_form"):
            st.text_input(
                "Your guess:", 
                key="guess_input_key", 
                placeholder="e.g., New York City, Houston, Denver...",
            )
            
            st.form_submit_button(
                "Submit Guess and See Next City", 
                on_click=handle_submit, 
            )
        
        # Display Results from Last Round
        if st.session_state.prev_guess:
            st.markdown("##### ➡️ Previous Result")
            
            if st.session_state.prev_was_correct:
                st.success(f"**CORRECT!** You guessed: **{st.session_state.prev_guess}**")
            else:
                st.error(f"**INCORRECT.** Your guess: **{st.session_state.prev_guess}**")

            display_answer = os.path.splitext(st.session_state.prev_answer)[0]
            st.info(f"The correct answer was: **{display_answer}**")
        else:
            st.write("Submit your first guess to start scoring!")
            
        st.markdown("---") 

        if st.session_state['input_error']:
            st.error(st.session_state['input_error'])

        # --- RETURN TO MAIN MENU BUTTON ---
        st.button(
            "⬅️ Return to Main Menu", 
            on_click=return_to_main_menu, 
            key="main_menu_button",
            type="primary"
        )
        # Display history as a clean table
        st.table(st.session_state.history)