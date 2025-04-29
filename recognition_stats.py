import os
from PIL import Image
import requests
import json
from datetime import datetime

# Path to the images folder
images_folder = "images"

# API URL
api_url = "https://api2.magic-sorter.com/image/mtg"

# Placeholder for API key
api_key = "c385152ffc1210b9cfd5b03ffb32dcf4"  # Enter your API key here

def load_images():
    """Load all images from the images folder"""
    image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpeg', '.jpg'))]
    loaded_images = []
    
    for image_file in image_files:
        image_path = os.path.join(images_folder, image_file)
        try:
            # Just check if the image can be opened
            with Image.open(image_path) as img:
                loaded_images.append((image_file, image_path))
                print(f"Successfully loaded: {image_file}")
        except Exception as e:
            print(f"Error loading {image_file}: {e}")
    
    return loaded_images

def send_to_api(image_name, image_path):
    """Send image to API and return the response"""
    if not api_key:
        print("API key is missing. Please enter your API key.")
        return None

    try:
        with open(image_path, 'rb') as image_file:
            files = [('image', (image_name, image_file, 'image/jpeg'))]
            data = {'api_key': api_key}
            response = requests.post(api_url, data=data, files=files)
            print(f"Successfully sent: {image_name}")
            # Print the response
            print(f"API Response for {image_name}: {response.text}")
            return response.text
    except Exception as e:
        print(f"Error sending {image_name} to API: {e}")
        return None

def is_card_recognized(response_text):
    """Check if a card was recognized based on API response"""
    # If the response is "error", the card was not recognized
    if response_text.strip().lower() == "error":
        print("API returned 'error' - Card not recognized")
        return False
    
    # Try to parse the response as JSON
    try:
        response_data = json.loads(response_text)
        # Check if the response contains an error field indicating unauthorized
        if "error" in response_data and response_data["error"] == "Unauthorized":
            print("API returned 'Unauthorized' error - Authentication problem")
            return False
        # If the API returns a valid JSON without unauthorized error, consider it recognized
        print("Card successfully recognized")
        return True
    except json.JSONDecodeError:
        # If we can't parse as JSON, it's likely an error
        print(f"Cannot parse response as JSON: '{response_text}' - Card not recognized")
        return False

def main():
    """Main function to process all images and generate statistics"""
    if not api_key:
        print("Please set your API key in the script before running.")
        return
    
    images = load_images()
    total_images = len(images)
    recognized = 0
    not_recognized = 0
    failed_requests = 0
    
    # Create a results list to store detailed information
    results = []
    
    print(f"\nProcessing {total_images} images...")
    
    for image_name, image_path in images:
        response_text = send_to_api(image_name, image_path)
        
        if response_text is None:
            failed_requests += 1
            results.append({
                'image': image_name,
                'status': 'request_failed',
                'response': None
            })
        else:
            is_recognized = is_card_recognized(response_text)
            if is_recognized:
                recognized += 1
                results.append({
                    'image': image_name,
                    'status': 'recognized',
                    'response': response_text
                })
            else:
                not_recognized += 1
                results.append({
                    'image': image_name,
                    'status': 'not_recognized',
                    'response': response_text
                })
    
    # Print statistics
    print("\n" + "="*50)
    print("CARD RECOGNITION STATISTICS")
    print("="*50)
    print(f"Total images processed: {total_images}")
    print(f"Successfully recognized: {recognized} ({(recognized/total_images*100):.1f}%)")
    print(f"Not recognized: {not_recognized} ({(not_recognized/total_images*100):.1f}%)")
    print(f"Failed requests: {failed_requests} ({(failed_requests/total_images*100):.1f}%)")
    
    # Save results to a file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"recognition_results_{timestamp}.txt", "w") as f:
        f.write("CARD RECOGNITION RESULTS\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total images processed: {total_images}\n")
        f.write(f"Successfully recognized: {recognized} ({(recognized/total_images*100):.1f}%)\n")
        f.write(f"Not recognized: {not_recognized} ({(not_recognized/total_images*100):.1f}%)\n")
        f.write(f"Failed requests: {failed_requests} ({(failed_requests/total_images*100):.1f}%)\n\n")
        
        f.write("DETAILS:\n")
        for result in results:
            f.write(f"\nImage: {result['image']}\n")
            f.write(f"Status: {result['status']}\n")
            if result['response']:
                f.write(f"Response: {result['response'][:200]}...\n" if len(result['response']) > 200 else f"Response: {result['response']}\n")

if __name__ == "__main__":
    main()