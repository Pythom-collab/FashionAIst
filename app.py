
headless = True
address = "0.0.0.0"
port = 5000

#[theme]
primaryColor = "#AEC6CF"  # Pastel blue
backgroundColor = "#1a1a1a"
secondaryBackgroundColor = "#E8F4F8"
textColor = "#4a4a4a"

import streamlit as st
import os
import sqlite3
import PIL.Image as Image
import io
import uuid
import json
from datetime import datetime

from database import init_db, save_clothing_item, get_clothing_items, get_clothing_by_category, get_themes
from database import save_outfit_feedback, get_outfit_feedback, get_top_rated_outfits
from image_processor import remove_background, combine_outfit_images
from classifier import classify_clothing
from outfit_recommender import generate_outfit_recommendation
from utils import load_sample_images, allowed_file

# Initialize app
st.set_page_config(
    page_title="FashionAIst",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Load CSS
def load_css():
    with open('.streamlit/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load animations
def load_animations():
    animation_css = """
    <style>
    @keyframes fadeInUp {
        from { opacity: 0; transform: translate3d(0, 40px, 0); }
        to { opacity: 1; transform: translate3d(0, 0, 0); }
    }
    
    @keyframes slideInLeft {
        from { transform: translate3d(-100%, 0, 0); }
        to { transform: translate3d(0, 0, 0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .fade-in-up { animation: fadeInUp 0.8s ease forwards; }
    .slide-in-left { animation: slideInLeft 0.8s ease forwards; }
    .pulse { animation: pulse 2s infinite; }
    
    .staggered-animation > * {
        opacity: 0;
        animation: fadeInUp 0.5s ease forwards;
    }
    
    .staggered-animation > *:nth-child(1) { animation-delay: 0.1s; }
    .staggered-animation > *:nth-child(2) { animation-delay: 0.2s; }
    .staggered-animation > *:nth-child(3) { animation-delay: 0.3s; }
    .staggered-animation > *:nth-child(4) { animation-delay: 0.4s; }
    .staggered-animation > *:nth-child(5) { animation-delay: 0.5s; }
    </style>
    """
    st.markdown(animation_css, unsafe_allow_html=True)

# Load CSS and animations
load_css()
load_animations()

# App title and description with animation
st.markdown("""
<div class="fade-in-up">
    <h1>FashionAIst</h1>
    <p style="font-size:1.2rem; color:#5A5A5A; margin-top:0;">Where style meets smart technology</p>
    <div style="height:3px; background:linear-gradient(to right, #E8F4F8, #1E6B8C, #E8F4F8); margin:10px 0 20px 0; border-radius:2px;"></div>
</div>
""", unsafe_allow_html=True)

# Create necessary folders
os.makedirs("uploaded_images", exist_ok=True)
os.makedirs("processed_images", exist_ok=True)

# Sidebar menu
st.sidebar.title("Menu")
option = st.sidebar.radio(
    "Choose an option",
    [
        "Home",
        "Upload to Wardrobe",
        "My Digital Wardrobe",
        "Get Outfit Recommendations"
    ]
)

# Home page
if option == "Home":
    # Animated hero section
    st.markdown("""
    <div class="fade-in-up" style="background:linear-gradient(135deg, #E8F4F8, #c7e6f0); padding:30px; border-radius:15px; margin-bottom:30px; border:2px solid #AEC6CF; box-shadow:0 10px 20px rgba(0,0,0,0.05);">
        <h2 style="color:#1E6B8C; text-align:center; font-weight:700; letter-spacing:1px;">Welcome to FashionAIst!</h2>
        <p style="font-size:18px; text-align:center; line-height:1.6; color:#444;">Your personal AI fashion assistant that helps you create stylish outfits from your digital wardrobe.</p>
        <div style="width:120px; height:5px; background-color:#AEC6CF; margin:20px auto; border-radius:5px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature heading with animation
    st.markdown("""
    <div class="slide-in-left">
        <h3 style="color:#1E6B8C; border-bottom:3px solid #AEC6CF; padding-bottom:10px; display:inline-block;">How It Works</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards with animations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="staggered-animation">
            <div class="styled-border" style="background-color:#FFFFFF; padding:25px; border-radius:12px; height:100%; border:none; border-left:5px solid #1E6B8C;">
                <h4 style="color:#1E6B8C; margin-bottom:15px;">Upload & Categorize</h4>
                <ul style="padding-left:20px; line-height:1.8;">
                    <li>Upload your clothing items to your digital wardrobe</li>
                    <li>Automatic clothing categorization system</li>
                    <li>Organize by categories, colors, and seasons</li>
                    <li>Support for all clothing types including ethnic wear</li>
                </ul>
                <div style="height:4px; width:80px; background-color:#AEC6CF; margin-top:15px; border-radius:2px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="staggered-animation">
            <div class="styled-border" style="background-color:#FFFFFF; padding:25px; border-radius:12px; height:100%; border:none; border-left:5px solid #1E6B8C;">
                <h4 style="color:#1E6B8C; margin-bottom:15px;">Create & Customize</h4>
                <ul style="padding-left:20px; line-height:1.8;">
                    <li>Select themes for outfit recommendations</li>
                    <li>Get multiple outfit options instantly</li>
                    <li>Rate outfits to improve future recommendations</li>
                    <li>Support for various clothing types including Indian dresses</li>
                </ul>
                <div style="height:4px; width:80px; background-color:#AEC6CF; margin-top:15px; border-radius:2px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Single spacer is sufficient
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
    
    # Call to action with pulsing animation
    st.markdown("""
    <div class="pulse" style="background:linear-gradient(135deg, #AEC6CF, #1E6B8C); padding:25px; border-radius:12px; margin-top:40px; text-align:center; box-shadow:0 10px 20px rgba(0,0,0,0.1);">
        <h3 style="color:white; margin-bottom:10px; font-weight:700; letter-spacing:1px;">Ready to upgrade your style?</h3>
        <p style="color:white; font-size:16px; margin-bottom:20px;">Start by uploading your clothing items to create your personalized digital wardrobe!</p>
        <div style="width:60px; height:5px; background-color:white; margin:0 auto; border-radius:5px; opacity:0.7;"></div>
    </div>
    """, unsafe_allow_html=True)

# Upload to Wardrobe page
elif option == "Upload to Wardrobe":
    st.markdown("""
    <div class="fade-in-up" style="background:linear-gradient(135deg, #E8F4F8, #c7e6f0); padding:25px; border-radius:15px; margin-bottom:25px; border:2px solid #AEC6CF; box-shadow:0 10px 20px rgba(0,0,0,0.05);">
        <h2 style="color:#1E6B8C; text-align:center; font-weight:700; letter-spacing:1px;">Add to Your Digital Wardrobe</h2>
        <p style="font-size:16px; text-align:center; line-height:1.6; color:#444;">Upload clothing items to build your personalized digital wardrobe</p>
        <div style="width:100px; height:4px; background-color:#1E6B8C; margin:15px auto; border-radius:4px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section for item details with better styling
    st.markdown("""
    <div class="slide-in-left styled-border" style="background-color:#FFFFFF; padding:20px; border-radius:12px; margin:25px 0; box-shadow:0 6px 12px rgba(0,0,0,0.08); border-left:4px solid #1E6B8C;">
        <h4 style="color:#1E6B8C; font-weight:600; margin-bottom:15px;">Item Details</h4>
        <p style="font-size:14px; color:#666; font-style:italic;">Provide detailed information about your clothing item to enable better outfit suggestions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user input for the clothing details in a three-column layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Basic Information")
        name = st.text_input("Name", value="New clothing item")
        
        categories = ["Top", "Bottom", "Dress", "Footwear", "Accessory", 
                    "Ethnic wear", "Formal wear", "Casual wear", "Other"]
        selected_category = st.selectbox("Category", categories)
        
        # Add section field
        sections = ["Everyday Wear", "Work Attire", "Party Outfit", "Seasonal", "Traditional", "Special Occasions"]
        selected_section = st.selectbox("Section", sections)
    
    with col2:
        st.subheader("Color Details")
        primary_color = st.color_picker("Primary Color", "#ffffff")
        
        # Add secondary color option
        has_secondary = st.checkbox("Has secondary color")
        secondary_color = None
        if has_secondary:
            secondary_color = st.color_picker("Secondary Color", "#000000")
        
        # Text input for color name
        color_name = st.text_input("Color Description", 
                                value="White" if primary_color == "#ffffff" else "")
    
    with col3:
        st.subheader("Additional Details")
        brand = st.text_input("Brand (optional)")
        
        season = st.multiselect("Suitable Seasons", 
                             ["Spring", "Summer", "Fall", "Winter", "All Seasons"])
        
        occasion = st.multiselect("Suitable Occasions", 
                               ["Casual", "Formal", "Party", "Work", 
                                "Traditional", "Festival", "Beach", "Sports"])
    
    # AFTER item details, add the uploader with better styling
    st.markdown("""
    <div class="fade-in-up styled-border" style="background-color:#FFFFFF; padding:20px; border-radius:12px; margin:30px 0; box-shadow:0 6px 12px rgba(0,0,0,0.08); border-left:4px solid #1E6B8C;">
        <h4 style="color:#1E6B8C; font-weight:600; margin-bottom:10px;">Upload Your Item Image</h4>
        <p style="font-size:14px; color:#666; font-style:italic;">Upload a clear photo of your clothing item for best results</p>
        <div style="height:3px; width:60px; background-color:#AEC6CF; margin-top:10px; border-radius:2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        # Add a decorative drop zone
        st.markdown("""
        <div style="border:2px dashed #AEC6CF; border-radius:12px; padding:30px; text-align:center; margin-bottom:15px; background-color:#F9FCFF;">
            <div style="color:#1E6B8C; font-size:24px; margin-bottom:10px;">📸</div>
            <p style="color:#666; font-size:16px; margin-bottom:5px;">Drag and drop your image here</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Select a clothing item image file", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
        
        # Helper text with better styling
        st.markdown("""
        <div style="text-align:center; margin-top:5px;">
            <p style="color:#888; font-size:12px; font-style:italic;">Supported formats: JPG, JPEG, PNG | Max size: 5MB</p>
        </div>
        """, unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Show the uploaded image
        st.markdown("<h5 style='text-align: center; color: #1E6B8C;'>Your Item Image</h5>", unsafe_allow_html=True)
        image = Image.open(uploaded_file)
        st.image(image, caption='', use_container_width=False, width=300)
        
        # Add save button
        save_btn = st.button("💾 Save to Wardrobe", type="primary")
        
        if save_btn:
            with st.spinner("Saving your item..."):
                try:
                    # Generate unique filename
                    filename = f"{uuid.uuid4()}.png"
                    upload_path = os.path.join("uploaded_images", filename)
                    processed_path = os.path.join("processed_images", filename)
                    
                    # Create directories if they don't exist
                    os.makedirs("uploaded_images", exist_ok=True)
                    os.makedirs("processed_images", exist_ok=True)
                    
                    # Save original image to both locations (no background removal)
                    image.save(upload_path)
                    image.save(processed_path)  # Save same image to processed folder for compatibility
                    
                    # Combine colors
                    color_info = {
                        "name": color_name,
                        "primary": primary_color,
                        "secondary": secondary_color if has_secondary else None,
                        "section": selected_section  # Add section here for better filtering
                    }
                    
                    # Additional details
                    additional_info = {
                        "brand": brand,
                        "section": selected_section,
                        "seasons": season
                    }
                    
                    # Convert to JSON strings
                    color_json = json.dumps(color_info)
                    additional_json = json.dumps(additional_info)
                    
                    # Make occasion a list if it isn't already
                    if not isinstance(occasion, list):
                        if occasion:
                            occasion = [occasion]
                        else:
                            occasion = []
                    
                    # Save to database
                    save_clothing_item(name, selected_category, color_json, occasion, filename)
                    
                    # Display success message
                    st.success("✅ Item successfully added to your digital wardrobe!")
                    
                    # Show a hint with button to view wardrobe
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.info("💡 Your item has been saved. What would you like to do next?")
                    with col2:
                        if st.button("View My Wardrobe"):
                            # This will trigger a rerun with the new option
                            st.session_state.option = "My Digital Wardrobe"
                            st.rerun()
                
                except Exception as e:
                    st.error(f"Error saving item: {str(e)}")
                    st.info("Please try again or contact support if the problem persists.")

# My Digital Wardrobe page
elif option == "My Digital Wardrobe":
    st.markdown("""
    <div class="fade-in-up" style="background:linear-gradient(135deg, #E8F4F8, #c7e6f0); padding:25px; border-radius:15px; margin-bottom:25px; border:2px solid #AEC6CF; box-shadow:0 10px 20px rgba(0,0,0,0.05);">
        <h2 style="color:#1E6B8C; text-align:center; font-weight:700; letter-spacing:1px;">My Digital Wardrobe</h2>
        <p style="font-size:16px; text-align:center; line-height:1.6; color:#444;">Explore and organize your digital clothing collection</p>
        <div style="width:100px; height:4px; background-color:#1E6B8C; margin:15px auto; border-radius:4px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all clothing items
    items = get_clothing_items()
    
    # Filters container with better styling
    with st.container():
        st.markdown("""
        <div class="slide-in-left styled-border" style="background-color:#FFFFFF; padding:20px; border-radius:12px; margin:25px 0; box-shadow:0 6px 12px rgba(0,0,0,0.08); border-left:4px solid #1E6B8C;">
            <h4 style="color:#1E6B8C; font-weight:600; margin-bottom:10px;">Find Your Perfect Items</h4>
            <p style="font-size:14px; color:#666; font-style:italic;">Filter your wardrobe to quickly find what you're looking for</p>
            <div style="height:3px; width:60px; background-color:#AEC6CF; margin-top:10px; border-radius:2px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create multi-column filter layout
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            categories = ["All"] + list(set([item[2] for item in items if item[2]]))
            selected_category = st.selectbox("Category", categories)
        
        with filter_col2:
            # Extract sections from items (requires color to be JSON with additional_info)
            sections = ["All"]
            for item in items:
                try:
                    if item[3]:  # Color field might contain the JSON with section info
                        color_data = json.loads(item[3])
                        if isinstance(color_data, dict) and "section" in color_data:
                            if color_data["section"] not in sections:
                                sections.append(color_data["section"])
                except:
                    pass
            
            if len(sections) == 1:  # Only "All" exists
                sections += ["Everyday Wear", "Work Attire", "Party Outfit", "Seasonal", "Traditional"]
                
            selected_section = st.selectbox("Section", sections)
        
        with filter_col3:
            # Add sorting options
            sort_options = ["Newest First", "Oldest First", "Name (A-Z)", "Name (Z-A)"]
            sort_by = st.selectbox("Sort By", sort_options)
    
    # Search bar with icon
    search_col1, search_col2 = st.columns([5, 1])
    with search_col1:
        search_query = st.text_input("🔍 Search items by name, color, or category")
    with search_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        clear_filters = st.button("Clear Filters")
    
    # Apply filters
    filtered_items = items
    
    # Apply category filter
    if selected_category != "All":
        filtered_items = [item for item in filtered_items if item[2] == selected_category]
    
    # Apply section filter
    if selected_section != "All":
        section_filtered = []
        for item in filtered_items:
            try:
                if item[3]:  # Color field
                    color_data = json.loads(item[3])
                    if isinstance(color_data, dict) and "section" in color_data:
                        if color_data["section"] == selected_section:
                            section_filtered.append(item)
                    else:
                        # If no section info found, keep the item when filtering by "Everyday Wear"
                        if selected_section == "Everyday Wear":
                            section_filtered.append(item)
            except:
                # If error parsing, keep the item when filtering by "Everyday Wear"
                if selected_section == "Everyday Wear":
                    section_filtered.append(item)
        filtered_items = section_filtered
    
    # Apply search filter
    if search_query:
        search_filtered = []
        query = search_query.lower()
        for item in filtered_items:
            item_id, name, category, color, occasion, filename, date_added = item
            # Search in name, category, and color
            if (query in name.lower() or 
                query in category.lower() or 
                (color and query in color.lower())):
                search_filtered.append(item)
        filtered_items = search_filtered
    
    # Apply sorting
    if sort_by == "Newest First":
        # Already sorted by date_added DESC from database
        pass
    elif sort_by == "Oldest First":
        filtered_items = sorted(filtered_items, key=lambda x: x[6])  # date_added is at index 6
    elif sort_by == "Name (A-Z)":
        filtered_items = sorted(filtered_items, key=lambda x: x[1].lower())  # name is at index 1
    elif sort_by == "Name (Z-A)":
        filtered_items = sorted(filtered_items, key=lambda x: x[1].lower(), reverse=True)
    
    # Display items header with count - styled better
    st.markdown(f"""
    <div class="staggered-animation styled-border" style="background-color:#FFFFFF; padding:20px; border-radius:12px; margin:30px 0 20px; box-shadow:0 6px 12px rgba(0,0,0,0.08); border-left:4px solid #1E6B8C; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h4 style="color:#1E6B8C; font-weight:600; margin-bottom:5px;">Your Clothing Collection</h4>
            <p style="font-size:14px; color:#666; font-style:italic;">Showing {len(filtered_items)} items in your wardrobe</p>
        </div>
        <div style="background-color:#E8F4F8; border-radius:20px; padding:5px 15px; border:1px solid #AEC6CF;">
            <span style="font-weight:bold; color:#1E6B8C;">{len(filtered_items)}</span>
            <span style="color:#666; font-size:14px;"> items</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not filtered_items:
        # Empty state with guidance
        st.markdown("""
        <div style="text-align:center; padding:40px; background-color:#f8f9fa; border-radius:10px; margin:20px 0">
            <img src="https://cdn-icons-png.flaticon.com/512/4076/4076503.png" style="width:100px; opacity:0.5">
            <h3 style="color:#6c757d; margin-top:20px">Your wardrobe is empty</h3>
            <p style="color:#6c757d">Upload some clothing items to get started with your digital wardrobe.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add a suggestion
        st.info("💡 Tip: Click on 'Upload to Wardrobe' in the menu to add your first clothing item!")
    else:
        cols = st.columns(3)
    
    for i, item in enumerate(filtered_items):
        st.write(f"Debug - Item {i}: {item}")
        st.write(f"Length of item {i}: {len(item)}")

        try:
            # Unpack only the first 7 elements to avoid ValueError
            item_id, name, category, color, occasion, filename, date_added, tags = item
        except ValueError:
            st.warning(f"Skipping item {i} due to unexpected structure: {item}")
            continue

        img_path = os.path.join("processed_images", filename)

        try:
            with cols[i % 3]:
                # Create an enhanced card (your existing UI rendering logic here)
                ...
        except Exception as e:
            st.error(f"Error displaying item {i}: {e}")


            img_path = os.path.join("processed_images", filename)
            
            try:
                with cols[i % 3]:
                    # Create an enhanced card-like container with hover effect and animation
                    st.markdown(f"""
                    <div class="staggered-animation">
                        <div class="styled-border" style="background:linear-gradient(to bottom, #FFFFFF, #F9FCFF); border-radius:12px; margin-bottom:20px; box-shadow:0 8px 16px rgba(0,0,0,0.05); overflow:hidden; transition:all 0.3s ease; border:1px solid #eaeaea;">
                            <div style="padding:15px; border-bottom:1px solid #f0f0f0;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                    <h4 style="margin:0; color:#1E6B8C; font-weight:600;">{name}</h4>
                                    <span style="background-color:#E8F4F8; color:#1E6B8C; padding:4px 8px; border-radius:20px; font-size:11px; font-weight:bold;">{category}</span>
                                </div>
                            </div>
                    """, unsafe_allow_html=True)
                    
                    # Image container with consistent height
                    st.markdown("""
                        <div style="height:250px; display:flex; align-items:center; justify-content:center; overflow:hidden; background-color:#f8f9fa; padding:10px;">
                    """, unsafe_allow_html=True)
                    
                    if os.path.exists(img_path):
                        img = Image.open(img_path)
                        st.image(img, caption="", use_container_width=True)
                    else:
                        st.error("Image not available")
                    
                    # Close image container div
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Item details with enhanced formatting
                    st.markdown(f"""
                            <div style="padding:15px;">
                    """, unsafe_allow_html=True)
                    
                    # Try to parse color as JSON for better display
                    try:
                        if color:
                            color_data = json.loads(color)
                            if isinstance(color_data, dict):
                                color_name = color_data.get("name", "")
                                primary = color_data.get("primary", "")
                                st.markdown(f"""
                                <p style="margin:2px 0;">
                                    <span style="color:#666; font-weight:bold;">Color:</span> 
                                    <span style="display:inline-block; width:12px; height:12px; background-color:{primary}; border-radius:50%; margin-right:5px;"></span>
                                    {color_name}
                                </p>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""<p style="margin:2px 0;"><span style="color:#666; font-weight:bold;">Color:</span> {color}</p>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<p style="margin:2px 0;"><span style="color:#666; font-weight:bold;">Color:</span> Not specified</p>""", unsafe_allow_html=True)
                    except:
                        st.markdown(f"""<p style="margin:2px 0;"><span style="color:#666; font-weight:bold;">Color:</span> {color}</p>""", unsafe_allow_html=True)
                    
                    # Format occasion nicely
                    try:
                        if occasion:
                            occasion_list = json.loads(occasion) if isinstance(occasion, str) else occasion
                            if isinstance(occasion_list, list):
                                occasion_str = ", ".join(occasion_list)
                                st.markdown(f"""<p style="margin:2px 0;"><span style="color:#666; font-weight:bold;">Occasions:</span> {occasion_str}</p>""", unsafe_allow_html=True)
                            else:
                                st.markdown(f"""<p style="margin:2px 0;"><span style="color:#666; font-weight:bold;">Occasions:</span> {occasion}</p>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<p style="margin:2px 0;"><span style="color:#666; font-weight:bold;">Occasions:</span> Not specified</p>""", unsafe_allow_html=True)
                    except:
                        st.markdown(f"""<p style="margin:2px 0;"><span style="color:#666; font-weight:bold;">Occasions:</span> {occasion}</p>""", unsafe_allow_html=True)
                    
                    # Add the date in a subtle format
                    date_display = date_added.split('T')[0] if 'T' in date_added else date_added
                    st.markdown(f"""
                    <p style="margin:5px 0; font-size:12px; color:#999; text-align:right;">Added: {date_display}</p>
                    """, unsafe_allow_html=True)
                    
                    # Close all divs properly
                    st.markdown("""
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error displaying item: {str(e)}")

# Get Outfit Recommendations page
elif option == "Get Outfit Recommendations":
    st.markdown("""
    <div class="fade-in-up" style="background:linear-gradient(135deg, #E8F4F8, #c7e6f0); padding:25px; border-radius:15px; margin-bottom:25px; border:2px solid #AEC6CF; box-shadow:0 10px 20px rgba(0,0,0,0.05);">
        <h2 style="color:#1E6B8C; text-align:center; font-weight:700; letter-spacing:1px;">Outfit Recommendations</h2>
        <p style="font-size:16px; text-align:center; line-height:1.6; color:#444;">Let AI create stylish outfit combinations from your digital wardrobe</p>
        <div style="width:100px; height:4px; background-color:#1E6B8C; margin:15px auto; border-radius:4px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all available themes
    themes = get_themes()
    
    if not themes:
        # Empty state with guidance
        st.markdown("""
        <div style="text-align:center; padding:40px; background-color:#f8f9fa; border-radius:10px; margin:20px 0">
            <img src="https://cdn-icons-png.flaticon.com/512/2589/2589175.png" style="width:100px; opacity:0.5">
            <h3 style="color:#6c757d; margin-top:20px">Not enough items in your wardrobe</h3>
            <p style="color:#6c757d">Please add more clothing items to get recommendations. You need at least tops, bottoms, and accessories.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add a suggestion
        st.info("💡 Tip: Upload a variety of clothing items including tops, bottoms, and accessories to enable outfit recommendations!")
    else:
        # Create a two-column layout for the selection options
        col1, col2 = st.columns(2)
        
        with col1:
            # Theme selection with enhanced styling
            st.markdown("""
            <div class="slide-in-left styled-border" style="background-color:#FFFFFF; padding:18px; border-radius:12px; margin-bottom:15px; box-shadow:0 6px 12px rgba(0,0,0,0.08); border-left:4px solid #1E6B8C;">
                <h5 style="color:#1E6B8C; margin:0; font-weight:600;">Select Your Theme</h5>
                <p style="font-size:13px; color:#666; margin-top:5px; font-style:italic;">Choose a theme for your outfit recommendation</p>
                <div style="height:3px; width:50px; background-color:#AEC6CF; margin-top:10px; border-radius:2px;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            selected_theme = st.selectbox("", themes, label_visibility="collapsed")
            
            # Enhanced theme descriptions with icons
            theme_descriptions = {
                "Casual": "👕 Relaxed, everyday outfits perfect for running errands or hanging out with friends",
                "Formal": "👔 Elegant and professional outfits suitable for office, business meetings or special events",
                "Party": "🎉 Stylish and eye-catching combinations for social gatherings and celebrations",
                "Traditional": "👘 Cultural and ethnic outfits that celebrate heritage and tradition",
                "Summer": "☀️ Light, breathable outfits for warm weather and sunny days",
                "Winter": "❄️ Warm, layered combinations to keep you stylish during cold weather"
            }
            
            if selected_theme in theme_descriptions:
                st.markdown(f"""
                <div style="background-color:#f8f9fa; padding:12px; border-radius:8px; margin-top:10px; border-left:3px solid #AEC6CF;">
                    <p style="margin:0; color:#555; font-size:14px;">{theme_descriptions[selected_theme]}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Customize recommendations with enhanced styling
            st.markdown("""
            <div class="slide-in-left styled-border" style="background-color:#FFFFFF; padding:18px; border-radius:12px; margin-bottom:15px; box-shadow:0 6px 12px rgba(0,0,0,0.08); border-left:4px solid #1E6B8C;">
                <h5 style="color:#1E6B8C; margin:0; font-weight:600;">Customize Your Recommendations</h5>
                <p style="font-size:13px; color:#666; margin-top:5px; font-style:italic;">Fine-tune your outfit suggestions</p>
                <div style="height:3px; width:50px; background-color:#AEC6CF; margin-top:10px; border-radius:2px;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            num_recommendations = st.slider("Number of outfit suggestions", 1, 5, 3)
            
            # Option to use feedback for smart recommendations
            st.markdown("""
            <div style="padding:10px; margin:10px 0; background-color:#F8F8F8; border-radius:5px;">
                <p style="margin:0; font-size:14px;">Smart recommendations improve with your feedback over time</p>
            </div>
            """, unsafe_allow_html=True)
            
            use_feedback = st.checkbox("Use my previous feedback for better recommendations", value=True)
            
            # Add explanation for the option
            st.caption("Your outfit ratings will help the system learn your style preferences")
        
        # Generate button with enhanced styling
        generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
        with generate_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            generate_btn = st.button("✨ Generate My Outfits", type="primary", use_container_width=True)
        
        if generate_btn:
            with st.spinner("Creating stylish outfits for you..."):
                # Get recommendations using feedback if selected
                outfits = generate_outfit_recommendation(selected_theme, num_recommendations, use_feedback)
                
                if not outfits:
                    # Better error message with styling
                    st.markdown("""
                    <div style="background-color:#FFF3CD; padding:20px; border-radius:10px; margin:20px 0; border-left:5px solid #FFD700;">
                        <h4 style="color:#856404; margin-top:0">Limited Wardrobe Variety</h4>
                        <p>We couldn't generate outfits for this theme with your current wardrobe items. Try adding more variety to your collection.</p>
                        <p><strong>Suggestion:</strong> Add more tops, bottoms, and accessories that match the selected theme.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Enhanced header for results with animation
                    st.markdown(f"""
                    <div class="fade-in-up" style="background:linear-gradient(135deg, #E8F4F8, #c7e6f0); padding:20px; border-radius:15px; margin:30px 0; border:2px solid #AEC6CF; box-shadow:0 10px 20px rgba(0,0,0,0.05);">
                        <h3 style="color:#1E6B8C; text-align:center; margin:0; font-weight:700; letter-spacing:0.5px;">
                            {len(outfits)} Outfit Suggestions for "{selected_theme}" Theme
                        </h3>
                        <div style="width:80px; height:3px; background-color:#1E6B8C; margin:15px auto; border-radius:3px;"></div>
                        <p style="text-align:center; font-size:14px; margin:0; color:#444;">
                            Swipe through your personalized outfit recommendations below
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display each outfit in an enhanced card-like container with staggered animation
                    for i, outfit in enumerate(outfits):
                        # Create an outfit card with improved styling and animation
                        st.markdown(f"""
                        <div class="staggered-animation" style="background:linear-gradient(to bottom, #FFFFFF, #F8F9FA); padding:25px; border-radius:12px; margin-bottom:40px; border:1px solid #E0E0E0; box-shadow:0 8px 16px rgba(0,0,0,0.05);">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; border-bottom:2px solid #E8F4F8; padding-bottom:15px;">
                                <h4 style="color:#1E6B8C; margin:0; font-weight:600;">Outfit {i+1}</h4>
                                <span style="background-color:#E8F4F8; color:#1E6B8C; padding:5px 12px; border-radius:20px; font-size:12px; font-weight:bold;">{selected_theme} Theme</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Get items for this outfit
                        outfit_items = []
                        for item_id in outfit:
                            # Get items by their category
                            category_items = get_clothing_by_category(item_id)
                            if category_items:
                                outfit_items.append(category_items[0])
                        
                        # Display outfit items
                        if outfit_items:
                            # Create columns for the combined outfit and individual items
                            main_col1, main_col2 = st.columns([2, 3])
                            
                            with main_col1:
                                # Create and display combined outfit
                                image_paths = [os.path.join("processed_images", item[5]) for item in outfit_items]
                                combined_outfit = combine_outfit_images(image_paths)
                                st.image(combined_outfit, caption="Combined Look", use_container_width=True)
                            
                            with main_col2:
                                # Header for items
                                st.markdown("""
                                <div style="background-color:#F0F8FF; padding:8px; border-radius:6px; margin-bottom:10px;">
                                    <h5 style="color:#1E6B8C; margin:0; font-size:16px;">Outfit Components</h5>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Display individual items in a horizontal scroll container
                                st.markdown("""
                                <style>
                                .scroll-container {
                                    display: flex;
                                    flex-wrap: nowrap;
                                    overflow-x: auto;
                                    padding: 10px 0;
                                    gap: 15px;
                                }
                                .item-card {
                                    min-width: 150px;
                                    border: 1px solid #e0e0e0;
                                    border-radius: 8px;
                                    padding: 10px;
                                    background-color: white;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                                }
                                </style>
                                <div class="scroll-container">
                                """, unsafe_allow_html=True)
                                
                                # Create HTML for each item
                                item_cards_html = ""
                                for j, item in enumerate(outfit_items):
                                    _, name, category, color, _, filename, _ = item
                                    img_path = os.path.join("processed_images", filename)
                                    
                                    if os.path.exists(img_path):
                                        # We can't directly insert the image into HTML, so we'll place items conventionally
                                        item_cards_html += f"""
                                        <div class="item-card">
                                            <p style="font-weight:bold; color:#1E6B8C; margin:0 0 5px 0; text-align:center;">
                                                {category}
                                            </p>
                                        </div>
                                        """
                                
                                st.markdown(item_cards_html + "</div>", unsafe_allow_html=True)
                                
                                # Now add the images conventionally
                                cols = st.columns(len(outfit_items))
                                for j, item in enumerate(outfit_items):
                                    _, name, category, color, _, filename, _ = item
                                    img_path = os.path.join("processed_images", filename)
                                    
                                    with cols[j]:
                                        if os.path.exists(img_path):
                                            img = Image.open(img_path)
                                            st.image(img, caption=f"{name}", use_container_width=True)
                                            st.caption(f"{category}")
                            
                            # Add a separator between outfits
                            st.markdown("<hr style='margin:30px 0; opacity:0.2;'>", unsafe_allow_html=True)
                        
                    # Enhanced feedback section with animation
                    st.markdown("""
                    <div class="fade-in-up" style="background:linear-gradient(135deg, #E8F4F8, #c7e6f0); padding:25px; border-radius:15px; margin:40px 0 25px; border:2px solid #AEC6CF; box-shadow:0 10px 20px rgba(0,0,0,0.05);">
                        <h3 style="color:#1E6B8C; text-align:center; margin:0; font-weight:700; letter-spacing:0.5px;">
                            How were your outfit recommendations?
                        </h3>
                        <div style="width:80px; height:3px; background-color:#1E6B8C; margin:15px auto; border-radius:3px;"></div>
                        <p style="text-align:center; font-size:15px; margin:0; color:#444; line-height:1.5;">
                            Your feedback helps us understand your style preferences and create<br>better personalized recommendations just for you
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create columns for feedback layout
                    feedback_col1, feedback_col2 = st.columns([2, 3])
                    
                    with feedback_col1:
                        # Enhanced rating section
                        st.markdown("""
                        <div class="slide-in-left styled-border" style="background-color:#FFFFFF; padding:18px; border-radius:12px; margin-bottom:15px; box-shadow:0 6px 12px rgba(0,0,0,0.08); border-left:4px solid #1E6B8C;">
                            <h5 style="color:#1E6B8C; margin:0; font-weight:600;">Rate Your Experience</h5>
                            <p style="font-size:13px; color:#666; margin-top:5px; font-style:italic;">How well did we match your style?</p>
                            <div style="height:3px; width:50px; background-color:#AEC6CF; margin-top:10px; border-radius:2px;"></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Visual star rating with emoji
                        st.markdown("""
                        <div style="text-align:center; padding:10px; background-color:#f8f9fa; border-radius:8px; margin:15px 0;">
                            <p style="margin:0; color:#666; font-size:14px;">Select your rating below:</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add star rating with better styling
                        rating = st.slider("Your rating", 1, 5, 3, 
                                         help="1 = Not helpful, 5 = Perfect recommendations",
                                         label_visibility="collapsed")
                        
                        # Visual representation of rating
                        star_display = "⭐" * rating
                        st.markdown(f"""
                        <div style="text-align:center; margin:5px 0 15px;">
                            <span style="font-size:24px;">{star_display}</span>
                            <p style="margin:10px 0 0; font-size:14px; color:#666;">
                                {rating}/5 stars
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with feedback_col2:
                        # Enhanced comments section
                        st.markdown("""
                        <div class="slide-in-left styled-border" style="background-color:#FFFFFF; padding:18px; border-radius:12px; margin-bottom:15px; box-shadow:0 6px 12px rgba(0,0,0,0.08); border-left:4px solid #1E6B8C;">
                            <h5 style="color:#1E6B8C; margin:0; font-weight:600;">Share Your Thoughts</h5>
                            <p style="font-size:13px; color:#666; margin-top:5px; font-style:italic;">Tell us what you liked or how we can improve</p>
                            <div style="height:3px; width:50px; background-color:#AEC6CF; margin-top:10px; border-radius:2px;"></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Feedback suggestions
                        st.markdown("""
                        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:15px;">
                            <span style="background:#f0f4f8; padding:5px 10px; border-radius:15px; font-size:12px; color:#555;">Great combinations!</span>
                            <span style="background:#f0f4f8; padding:5px 10px; border-radius:15px; font-size:12px; color:#555;">Colors don't match my style</span>
                            <span style="background:#f0f4f8; padding:5px 10px; border-radius:15px; font-size:12px; color:#555;">Perfect for the occasion</span>
                            <span style="background:#f0f4f8; padding:5px 10px; border-radius:15px; font-size:12px; color:#555;">Need more accessories</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Enhanced text area
                        feedback_text = st.text_area("Share your thoughts (optional)",
                                                  placeholder="What did you like or dislike about these recommendations? Any specific items that worked well together?",
                                                  height=120,
                                                  label_visibility="collapsed")
                        
                        st.caption("Your detailed feedback helps us improve our recommendations algorithm")
                    
                    # Submit button with enhanced styling
                    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
                    feedback_btn_col1, feedback_btn_col2, feedback_btn_col3 = st.columns([1, 2, 1])
                    with feedback_btn_col2:
                        submit_feedback = st.button("💫 Submit Feedback", 
                                                 type="primary",
                                                 use_container_width=True)
                    
                    if submit_feedback:
                        try:
                            # Get all outfit item IDs to save
                            all_outfit_item_ids = []
                            for outfit in outfits:
                                outfit_item_ids = []
                                for item_id in outfit:
                                    # Get actual item IDs from categories
                                    category_items = get_clothing_by_category(item_id)
                                    if category_items and len(category_items) > 0:
                                        outfit_item_ids.append(category_items[0][0])  # First item's ID
                                
                                if outfit_item_ids:
                                    all_outfit_item_ids.extend(outfit_item_ids)
                            
                            # Save feedback to database
                            save_outfit_feedback(all_outfit_item_ids, selected_theme, rating, feedback_text)
                            
                            # Success message
                            st.success("Thank you for your feedback! We'll use it to improve your future recommendations.")
                            
                        except Exception as e:
                            st.error(f"Error saving feedback: {str(e)}")
                    
                    # Enhanced call to action at the end with animation
                    st.markdown("""
                    <div class="pulse" style="background:linear-gradient(135deg, #AEC6CF, #1E6B8C); padding:25px; border-radius:12px; margin-top:40px; text-align:center; box-shadow:0 10px 20px rgba(0,0,0,0.1);">
                        <h3 style="color:white; margin-bottom:10px; font-weight:700; letter-spacing:1px;">Want to explore more?</h3>
                        <p style="color:white; font-size:16px; margin-bottom:20px; line-height:1.6;">
                            Try different themes or add more items to your wardrobe to discover<br>exciting new outfit combinations!
                        </p>
                        <div style="display:flex; justify-content:center; gap:20px; flex-wrap:wrap;">
                            <div style="background:rgba(255,255,255,0.2); padding:10px 20px; border-radius:50px; backdrop-filter:blur(5px);">
                                <span style="color:white; font-size:14px;">🔄 Try another theme</span>
                            </div>
                            <div style="background:rgba(255,255,255,0.2); padding:10px 20px; border-radius:50px; backdrop-filter:blur(5px);">
                                <span style="color:white; font-size:14px;">👕 Add more clothing</span>
                            </div>
                        </div>
                        <div style="width:60px; height:5px; background-color:white; margin:20px auto; border-radius:5px; opacity:0.7;"></div>
                    </div>
                    """, unsafe_allow_html=True)
