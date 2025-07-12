import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def get_db_connection():
    """Get a connection to the PostgreSQL database"""
    try:
        # Replace these with your pgAdmin database credentials
        conn = psycopg2.connect(
            dbname="fashionaist",
            user="postgres",  # Replace with your username if different
            password="fashionAIst@123",  # Replace with your actual password
            host="localhost", 
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None

def init_db():
    """Initialize the database with required tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create clothing_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clothing_items (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        color TEXT,
        occasion TEXT,
        filename TEXT NOT NULL,
        date_added TEXT NOT NULL
    )
    ''')
    
    # Create themes table for outfit recommendations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS themes (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        categories TEXT NOT NULL
    )
    ''')
    
    # Create feedback table to track user satisfaction with outfits
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS outfit_feedback (
            id SERIAL PRIMARY KEY,
            outfit_items TEXT NOT NULL,
            theme TEXT NOT NULL,
            rating INTEGER NOT NULL,
            feedback_text TEXT,
            date_added TEXT NOT NULL
        )
        ''')
    except psycopg2.errors.UniqueViolation:
        # If the table already exists, roll back and continue
        conn.rollback()
    
    # Insert default themes if they don't exist
    themes = [
        ('Casual', 'Everyday comfortable outfits', json.dumps(['Top', 'Bottom', 'Casual wear', 'Footwear'])),
        ('Formal', 'Professional and elegant outfits', json.dumps(['Formal wear', 'Top', 'Bottom', 'Footwear'])),
        ('Party', 'Stylish and trendy outfits for parties', json.dumps(['Dress', 'Top', 'Bottom', 'Accessory'])),
        ('Traditional', 'Cultural and traditional outfits', json.dumps(['Ethnic wear', 'Accessory', 'Footwear'])),
        ('Summer', 'Light and breezy outfits for hot weather', json.dumps(['Top', 'Bottom', 'Casual wear', 'Footwear'])),
        ('Winter', 'Warm and cozy outfits for cold weather', json.dumps(['Top', 'Bottom', 'Casual wear', 'Footwear']))
    ]
    
    try:
        cursor.execute('SELECT COUNT(*) FROM themes')
        result = cursor.fetchone()
        count = result[0] if result else 0
        
        if count == 0:
            for theme in themes:
                cursor.execute(
                    'INSERT INTO themes (name, description, categories) VALUES (%s, %s, %s)',
                    theme
                )
    except psycopg2.errors.UndefinedTable:
        # Table doesn't exist yet, so we're creating it for the first time
        conn.rollback()
        # Create table again (previous CREATE TABLE might have been rolled back)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS themes (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            categories TEXT NOT NULL
        )
        ''')
        
        # Insert themes
        for theme in themes:
            cursor.execute(
                'INSERT INTO themes (name, description, categories) VALUES (%s, %s, %s)',
                theme
            )
    
    conn.commit()
    conn.close()

def save_clothing_item(name, category, color, occasion, filename):
    """Save a clothing item to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert occasion list to JSON string
    if isinstance(occasion, list):
        occasion = json.dumps(occasion)
    
    cursor.execute(
        'INSERT INTO clothing_items (name, category, color, occasion, filename, date_added) VALUES (%s, %s, %s, %s, %s, %s)',
        (name, category, color, occasion, filename, datetime.now().isoformat())
    )
    
    conn.commit()
    conn.close()

def get_clothing_items():
    """Get all clothing items from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM clothing_items ORDER BY date_added DESC')
    items = cursor.fetchall()
    
    conn.close()
    return items

def get_clothing_by_category(category):
    """Get clothing items by category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM clothing_items WHERE category = %s', (category,))
    items = cursor.fetchall()
    
    conn.close()
    return items

def get_clothing_item(item_id):
    """Get a specific clothing item by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM clothing_items WHERE id = %s', (item_id,))
    item = cursor.fetchone()
    
    conn.close()
    return item

def get_themes():
    """Get all available themes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT name FROM themes')
        themes = [theme[0] for theme in cursor.fetchall()]
    except psycopg2.Error as e:
        print(f"Error retrieving themes: {e}")
        themes = []
    
    conn.close()
    return themes

def get_theme_categories(theme_name):
    """Get the categories for a specific theme"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT categories FROM themes WHERE name = %s', (theme_name,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return json.loads(result[0])
    return []

def save_outfit_feedback(outfit_items, theme, rating, feedback_text=""):
    """
    Save user feedback for an outfit recommendation
    
    Args:
        outfit_items (list): List of item IDs in the outfit
        theme (str): Theme used for the outfit recommendation
        rating (int): User rating (1-5)
        feedback_text (str): Optional feedback comments
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert outfit items list to JSON string
    if isinstance(outfit_items, list):
        outfit_items = json.dumps(outfit_items)
    
    cursor.execute(
        'INSERT INTO outfit_feedback (outfit_items, theme, rating, feedback_text, date_added) VALUES (%s, %s, %s, %s, %s)',
        (outfit_items, theme, rating, feedback_text, datetime.now().isoformat())
    )
    
    conn.commit()
    conn.close()

def get_outfit_feedback(theme=None):
    """
    Get outfit feedback, optionally filtered by theme
    
    Args:
        theme (str, optional): Theme to filter by
        
    Returns:
        list: List of feedback records
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if theme:
        cursor.execute('SELECT * FROM outfit_feedback WHERE theme = %s ORDER BY date_added DESC', (theme,))
    else:
        cursor.execute('SELECT * FROM outfit_feedback ORDER BY date_added DESC')
        
    items = cursor.fetchall()
    
    conn.close()
    return items

def get_top_rated_outfits(theme=None, limit=5):
    """
    Get the top-rated outfits, optionally filtered by theme
    
    Args:
        theme (str, optional): Theme to filter by
        limit (int, optional): Maximum number of outfits to return
        
    Returns:
        list: List of top-rated outfit records
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if theme:
        cursor.execute(
            'SELECT * FROM outfit_feedback WHERE theme = %s ORDER BY rating DESC, date_added DESC LIMIT %s', 
            (theme, limit)
        )
    else:
        cursor.execute(
            'SELECT * FROM outfit_feedback ORDER BY rating DESC, date_added DESC LIMIT %s',
            (limit,)
        )
        
    items = cursor.fetchall()
    
    conn.close()
    return items
