import random
import json
from database import get_clothing_items, get_clothing_by_category, get_theme_categories, get_top_rated_outfits, get_outfit_feedback

def generate_outfit_recommendation(theme, num_recommendations=3, use_feedback=True):
    """
    Generate outfit recommendations based on the selected theme
    
    Args:
        theme (str): The selected theme
        num_recommendations (int): Number of outfit recommendations to generate
        use_feedback (bool): Whether to use previous user feedback to improve recommendations
        
    Returns:
        list: List of outfits, where each outfit is a list of clothing item IDs
    """
def get_theme_categories(theme):
    theme_map = {
        "casual": ["jeans", "t-shirt", "sneakers"],
        "formal": ["blazer", "slacks", "dress shoes"],
        "sporty": ["tracksuit", "running shoes"],
        # Add more themes as needed
    }
    return theme_map.get(theme, [])

    # Get all clothing items
    all_items = get_clothing_items()
    
    # If no items, return empty list
    if not all_items:
        return []
    
    # Get appropriate categories for the theme
    theme_categories = get_theme_categories(theme)
    
    # Create a dictionary of items by category
    items_by_category = {}
    item_id_map = {}  # Map item IDs to full items for later lookup
    
    for item in all_items:
        item_id = item[0]  # ID is at index 0
        category = item[2]  # Category is at index 2
        if category not in items_by_category:
            items_by_category[category] = []
        items_by_category[category].append(item)
        item_id_map[item_id] = item
    
    # If using feedback, first try to get highly rated outfits for this theme
    recommended_outfits = []
    if use_feedback:
        top_rated = get_top_rated_outfits(theme, limit=3)
        
        # If we found some top-rated outfits, include them
        if top_rated and len(top_rated) > 0:
            for feedback in top_rated:
                try:
                    outfit_items_json = feedback[1]  # outfit_items is at index 1
                    outfit_items_list = json.loads(outfit_items_json)
                    
                    # Convert IDs back to categories for our algorithm
                    outfit_categories = []
                    for item_id in outfit_items_list:
                        if str(item_id).isdigit() and int(item_id) in item_id_map:
                            outfit_categories.append(item_id_map[int(item_id)][2])  # Category at index 2
                    
                    if outfit_categories:
                        recommended_outfits.append(outfit_categories)
                except (json.JSONDecodeError, IndexError, KeyError) as e:
                    # Skip this feedback if there's an error
                    print(f"Error processing feedback: {e}")
                    continue
    
    # Create outfits based on theme categories
    outfits = []
    
    # Determine which categories we need for this theme
    required_categories = []
    
    if theme == "Casual":
        required_categories = ["Top", "Bottom", "Casual wear", "Footwear"]
    elif theme == "Formal":
        required_categories = ["Formal wear", "Top", "Bottom", "Footwear"]
    elif theme == "Party":
        required_categories = ["Dress", "Accessory"]
        # Alternatively, use top and bottom
        if "Dress" not in items_by_category or len(items_by_category.get("Dress", [])) == 0:
            required_categories = ["Top", "Bottom", "Accessory"]
    elif theme == "Traditional":
        required_categories = ["Ethnic wear", "Accessory", "Footwear"]
    elif theme == "Summer":
        required_categories = ["Top", "Bottom", "Casual wear"]
    elif theme == "Winter":
        required_categories = ["Top", "Bottom", "Casual wear"]
    else:
        # Default to a simple outfit
        required_categories = ["Top", "Bottom"]
    
    # Filter to only include categories with available items
    available_categories = [cat for cat in required_categories if cat in items_by_category and items_by_category[cat]]
    
    # If we don't have enough categories, return empty list
    if len(available_categories) < 2:
        return []
    
    # Generate the requested number of outfit recommendations
    attempts = 0
    while len(outfits) < num_recommendations and attempts < 20:
        attempts += 1
        outfit = []
        
        # Handle special case for dress-based outfits
        if "Dress" in available_categories:
            # Add a random dress
            dress = random.choice(items_by_category["Dress"])
            outfit.append("Dress")
            
            # Potentially add accessories or footwear if available
            if "Accessory" in available_categories and random.random() > 0.5:
                outfit.append("Accessory")
            if "Footwear" in available_categories and random.random() > 0.3:
                outfit.append("Footwear")
        
        # Handle special case for ethnic wear
        elif "Ethnic wear" in available_categories:
            # Add ethnic wear
            outfit.append("Ethnic wear")
            
            # Add accessories and footwear if available
            if "Accessory" in available_categories and random.random() > 0.3:
                outfit.append("Accessory")
            if "Footwear" in available_categories and random.random() > 0.3:
                outfit.append("Footwear")
        
        # Standard top and bottom outfit
        else:
            # Always include top and bottom if available
            if "Top" in available_categories:
                outfit.append("Top")
            if "Bottom" in available_categories:
                outfit.append("Bottom")
            
            # Randomly add other available categories
            for category in available_categories:
                if category not in ["Top", "Bottom"] and random.random() > 0.5:
                    outfit.append(category)
        
        # Ensure we have at least 2 items
        if len(outfit) < 2:
            continue
        
        # Convert category names to actual item IDs
        outfit_items = []
        for category in outfit:
            # Get a random item from this category
            if category in items_by_category and items_by_category[category]:
                item = random.choice(items_by_category[category])
                outfit_items.append(category)
        
        # Add this outfit if it's unique
        if outfit_items and outfit_items not in outfits:
            outfits.append(outfit_items)
    
    # Combine the highly rated outfits from feedback with the new generated outfits
    combined_outfits = recommended_outfits + outfits
    
    # Return only the requested number of outfits
    return combined_outfits[:num_recommendations]
