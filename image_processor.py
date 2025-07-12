import cv2
import numpy as np
from PIL import Image
import io
from rembg import remove
import os

def remove_background(image_path):
    """
    Remove the background from an image using rembg
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        PIL.Image: Image with background removed
    """
    try:
        print(f"Processing image: {image_path}")
        
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read the image
        with open(image_path, 'rb') as f:
            input_data = f.read()
            print(f"Successfully read image data, size: {len(input_data)} bytes")
        
        # Remove background
        print("Starting background removal...")
        output_data = remove(input_data)
        print(f"Background removal complete")
        
        # Convert to PIL Image 
        if isinstance(output_data, bytes):
            img = Image.open(io.BytesIO(output_data))
            print(f"Successfully converted to PIL Image, size: {img.size}")
        elif isinstance(output_data, Image.Image):
            img = output_data
            print(f"Output is already a PIL Image, size: {img.size}")
        else:
            # For other types, convert to bytes first
            print(f"Converting output type {type(output_data)} to image")
            img = Image.open(io.BytesIO(output_data))
            print(f"Successfully converted to PIL Image, size: {img.size}")
        
        return img
    except FileNotFoundError as e:
        print(f"File not found error: {str(e)}")
        raise
    except Exception as e:
        print(f"Error removing background: {str(e)}")
        # Return original image if processing fails
        print("Returning original image due to error")
        try:
            return Image.open(image_path)
        except Exception as inner_e:
            print(f"Error opening original image: {str(inner_e)}")
            # Create a small placeholder image if everything fails
            placeholder = Image.new('RGBA', (400, 400), (255, 255, 255, 0))
            return placeholder

def resize_image(img, max_width=400, max_height=600):
    """
    Resize an image maintaining aspect ratio
    
    Args:
        img (PIL.Image): Image to resize
        max_width (int): Maximum width
        max_height (int): Maximum height
        
    Returns:
        PIL.Image: Resized image
    """
    width, height = img.size
    
    # Calculate aspect ratio
    aspect_ratio = width / height
    
    if width > max_width or height > max_height:
        if aspect_ratio > 1:  # Width greater than height
            new_width = max_width
            new_height = int(max_width / aspect_ratio)
        else:  # Height greater than width
            new_height = max_height
            new_width = int(max_height * aspect_ratio)
        
        # Use high-quality resampling with version compatibility
        try:
            # Try to use the best resampling method available
            # The order is:
            # 1. LANCZOS (PIL 9+ or 10+ with Resampling enum)
            # 2. ANTIALIAS (older PIL versions)
            # 3. BICUBIC (universal fallback)
            # 4. No resampling method (absolute fallback)
            
            # Get the appropriate resampling method based on PIL version
            resampling_method = None
            
            # Check for Resampling enum (PIL 10+)
            if hasattr(Image, 'Resampling') and hasattr(Image.Resampling, 'LANCZOS'):
                resampling_method = Image.Resampling.LANCZOS
            # Check for direct constants in various PIL versions
            elif hasattr(Image, 'LANCZOS'):
                resampling_method = getattr(Image, 'LANCZOS')
            elif hasattr(Image, 'ANTIALIAS'):
                resampling_method = getattr(Image, 'ANTIALIAS')
            elif hasattr(Image, 'BICUBIC'):
                resampling_method = getattr(Image, 'BICUBIC')
                
            # Resize with the determined method or fallback to no method
            if resampling_method is not None:
                img = img.resize((new_width, new_height), resampling_method)
            else:
                img = img.resize((new_width, new_height))
                
        except Exception as e:
            # Final fallback if any error occurs
            print(f"Error during image resize, using simple resize: {str(e)}")
            img = img.resize((new_width, new_height))
    
    return img

def combine_outfit_images(image_paths, canvas_width=600, canvas_height=800):
    """
    Combine multiple clothing item images to create an outfit visualization
    
    Args:
        image_paths (list): List of image paths to combine
        canvas_width (int): Width of the canvas
        canvas_height (int): Height of the canvas
        
    Returns:
        PIL.Image: Combined outfit image
    """
    # Create a transparent canvas
    canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
    
    if not image_paths:
        return canvas
    
    # Calculate positions based on number of items
    num_items = len(image_paths)
    
    # Load and position images based on their categories
    top_position = (canvas_width // 2, canvas_height // 4)
    bottom_position = (canvas_width // 2, canvas_height // 2)
    # Convert float division to integer for dress position
    dress_position = (canvas_width // 2, int(canvas_height // 2.5))
    footwear_position = (canvas_width // 2, 3 * canvas_height // 4)
    accessory_positions = [
        (canvas_width // 4, canvas_height // 5),
        (3 * canvas_width // 4, canvas_height // 5)
    ]
    
    # Track placed categories to avoid duplicates
    placed_categories = set()
    accessory_count = 0
    
    # First pass for main clothing items (tops, bottoms, dresses)
    for path in image_paths:
        if not os.path.exists(path):
            continue
            
        try:
            img = Image.open(path)
            
            # Determine category from filename
            filename = os.path.basename(path)
            category = None
            
            # Get category from database - for now use a simple approach
            if "Top" in filename or "top" in filename:
                category = "Top"
            elif "Bottom" in filename or "bottom" in filename:
                category = "Bottom"
            elif "Dress" in filename or "dress" in filename:
                category = "Dress"
            elif "Footwear" in filename or "footwear" in filename:
                category = "Footwear"
            elif "Accessory" in filename or "accessory" in filename:
                category = "Accessory"
            elif "Ethnic" in filename or "ethnic" in filename:
                category = "Ethnic wear"
            
            # Resize image
            if category == "Top" and "Top" not in placed_categories:
                img = resize_image(img, max_width=canvas_width // 2, max_height=canvas_height // 3)
                position = top_position
                placed_categories.add("Top")
            elif category == "Bottom" and "Bottom" not in placed_categories:
                img = resize_image(img, max_width=canvas_width // 2, max_height=canvas_height // 3)
                position = bottom_position
                placed_categories.add("Bottom")
            elif category == "Dress" and "Dress" not in placed_categories:
                img = resize_image(img, max_width=canvas_width // 2, max_height=canvas_height // 2)
                position = dress_position
                placed_categories.add("Dress")
            elif category == "Footwear" and "Footwear" not in placed_categories:
                img = resize_image(img, max_width=canvas_width // 3, max_height=canvas_height // 4)
                position = footwear_position
                placed_categories.add("Footwear")
            elif category == "Accessory" and accessory_count < len(accessory_positions):
                img = resize_image(img, max_width=canvas_width // 4, max_height=canvas_height // 5)
                position = accessory_positions[accessory_count]
                accessory_count += 1
            elif category == "Ethnic wear" and "Ethnic wear" not in placed_categories:
                img = resize_image(img, max_width=canvas_width // 2, max_height=canvas_height // 2)
                position = dress_position
                placed_categories.add("Ethnic wear")
            else:
                # Skip items that don't fit in our layout
                continue
            
            # Calculate position to center the image
            x = position[0] - img.width // 2
            y = position[1] - img.height // 2
            
            # Paste the image onto the canvas
            canvas.paste(img, (x, y), img)
            
        except Exception as e:
            print(f"Error processing image {path}: {str(e)}")
    
    return canvas
