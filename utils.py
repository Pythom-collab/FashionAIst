import os
import io
import requests
from PIL import Image
import streamlit as st

# Hardcoded stock photo URLs (would normally be loaded from a database or external API)
STOCK_PHOTOS = {
    "fashion outfits": [
        "https://pixabay.com/get/gb37fd061d059d2660b75731a99edc20571f9d991dae4ea1bebb17a880cbec159dfc39a34caf9e0030fac92ddf2b5e5b063332837426a2ef21766b2229c5f9e44_1280.jpg",
        "https://pixabay.com/get/gf59a11004aa471fdc66d4178ee1b8ed8bef0afa85d8578f2c00bd7dddaee9a01882155de2758bb03fbb8b5ce16ea1ad52f64944010a1152134a3d9a7e395cf7d_1280.jpg",
        "https://pixabay.com/get/gfd9e7a6072c6f5c7f565c5b5e88c707efb1531cdce2f2a15ab6621c06def0017ffffb5cb1ac2ed576ea974470757bf81733a8ca315f2472b02c10acf96b05122_1280.jpg",
        "https://pixabay.com/get/g12ab7169070d5a5ed811fa60df74c413879abb2f25da8feed1f817317c325129c07e290d364dabc793c2ed5c6dd1f989747d957f6a4b05fd3ce36e11313e4426_1280.jpg",
        "https://pixabay.com/get/ged62c2dcc90fc38495ce01f2533928f5a42629770adea6dfddc64fa6f46013584eb88551edd0e14ce27a1f1a5b715d53542fc59d9779185017ab0aa763e0a11f_1280.jpg",
        "https://pixabay.com/get/g7684fa45ad24f0ab478e7b25b89d94d59c4ffa7f7a0499ea87e65ac1621cf24e9413bdf7e0a734b71292ed2bc39e58727cc51c2439d01951fa89b44774f87314_1280.jpg"
    ],
    "clothing items": [
        "https://pixabay.com/get/ge556d85b6367267b93753c878e755655156b2372abf9e30513eac1c01794e218736ffe76af076951e866d4a8d1bb026098f6e23d4b516ec235da71577c6af26b_1280.jpg",
        "https://pixabay.com/get/gfd0fb253ab4835768ecd6ac8c9d683064eeeaa1d40782a259953e010766af4f74f614153d12ead65e015aadec69920938e88fc980cc666cf3eb9ab1dba5c9ba4_1280.jpg",
        "https://pixabay.com/get/g6f80e42db97114e789188c6f82a1e4d2448b74e6a315651232858365ea1ce9f52f8cb6ec616256031cda6b476f97ee74dab4035477d5240dcf9466154108f84b_1280.jpg",
        "https://pixabay.com/get/gc76c21bdaae7da984664d71fa42616282dbce1dfe2f3168f31fe9c9d6405f7834f168b7cbeec936b879dda3245ed2827f09668316ba20f2c6eb28ceb062a2697_1280.jpg",
        "https://pixabay.com/get/g1036b10b32f0695625d4c0c6b7c0cfdddb45a209f1fabc8f1d4714016acbe2daba254feb5ad08c0fee4ae6fdf1db79b743f030745f6be4843432ec2b18560533_1280.jpg"
    ],
    "wardrobe organization": [
        "https://pixabay.com/get/gd743112b72e5fb817e48b37f07fe7a0b3e37eebc1c192c2c6c7fe3de55b9f4c2ecfb34961f2aae8ba718423541d8140bd54499bb762a14adc3c5be6fbdb2f086_1280.jpg",
        "https://pixabay.com/get/gfeb98eca0b88728452f8e26761961752619a17266de7932ad2ede13de6b83cf7577016ca28984d7cc5fbafb2f6354c6b0a1d1c0b277a5d7b198e08b34e080fd7_1280.jpg",
        "https://pixabay.com/get/ge8748f6af0c7dbc18a1ca1f4cabaa736ad6f07e796cbce99ea860cdf434df74e874e0bdfdc812a58c4519bc80adcd00a838dbeb966435781d9c9430f58e489b4_1280.jpg",
        "https://pixabay.com/get/g2c1ac84c81c4c45165562c44ca09a85495f74a877cc23420f9c4bdc021ce7073e5c06faeda360f3b75cbd031205c85b1b84607c37740e43b6b32d30c309b2fe9_1280.jpg"
    ]
}

@st.cache_data
def load_sample_images(category):
    """
    Load sample images for display
    
    Args:
        category (str): Category of images to load
        
    Returns:
        list: List of PIL Image objects
    """
    images = []
    
    if category in STOCK_PHOTOS:
        for url in STOCK_PHOTOS[category]:
            try:
                response = requests.get(url)
                image = Image.open(io.BytesIO(response.content))
                images.append(image)
            except Exception as e:
                print(f"Error loading image from {url}: {str(e)}")
    
    return images

def allowed_file(filename):
    """
    Check if a file is allowed based on its extension
    
    Args:
        filename (str): Filename to check
        
    Returns:
        bool: True if file is allowed, False otherwise
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
