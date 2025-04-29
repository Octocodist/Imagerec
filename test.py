import os
from PIL import Image
import requests

# Path to the images folder
images_folder = "images"

# List all image files in the folder
image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpeg', '.jpg'))]

# API URL
api_url = "https://api2.magic-sorter.com/image/mtg"

# Placeholder for API key
api_key = "c385152ffc1210b9cfd5b03ffb32dcf4"  # Enter your API key here

# Load images as JPEGs
def load_images():
    loaded_images = []
    for image_file in image_files:
        image_path = os.path.join(images_folder, image_file)
        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")  # Convert to RGB if not already
                loaded_images.append((image_file, image_path))
                print(f"Successfully loaded: {image_file}")
        except Exception as e:
            print(f"Error loading {image_file}: {e}")
    return loaded_images

# Function to send images to an API endpoint using requests
def send_to_api(image_name, image_path):
    if not api_key:
        print("API key is missing. Please enter your API key.")
        return

    try:
        with open(image_path, 'rb') as image_file:
            files = [('image', (image_name, image_file, 'image/jpeg'))]
            data = {'api_key': api_key}
            response = requests.post(api_url, data=data, files=files)
            print(f"Successfully sent: {image_name}")
            print(f"Response for {image_name}: {response.text}")
    except Exception as e:
        print(f"Error sending {image_name} to API: {e}")

if __name__ == "__main__":
    images = load_images()
    if images:
        # Test with the first image only
        image_name, image_path = images[5]
        send_to_api(image_name, image_path)
    else:
        print("No images found to process.")