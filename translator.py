import google.generativeai as genai
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup your API Key
# Get one here: https://aistudio.google.com/app/apikey
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
genai.configure(api_key=api_key)

def load_pet_rules():
    with open("pet_rules.txt", "r") as f:
        content = f.read()
    # Split into dog and cat rules
    if "CAT BODY LANGUAGE DECODER:" in content:
        parts = content.split("CAT BODY LANGUAGE DECODER:")
        dog_rules = parts[0].strip()
        cat_rules = "CAT BODY LANGUAGE DECODER:" + parts[1].strip()
    else:
        dog_rules = content
        cat_rules = ""
    return dog_rules, cat_rules

def analyze_pet_mood(pet_type, video_path):
    # Upload your Video
    print(f"Uploading {video_path}...")
    video_file = genai.upload_file(path=video_path)

    # CRITICAL STEP: Wait for video processing
    # Videos take a few seconds to be "ready" on Google's servers.
    while video_file.state.name == "PROCESSING":
        print("Analyzing video frames...")
        time.sleep(2)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(f"Video processing failed: {video_file.state.name}")

    # Load pet rules
    dog_rules, cat_rules = load_pet_rules()
    if pet_type.lower() == "dog":
        expert_rules = dog_rules
        pet_name = "dog"
    elif pet_type.lower() == "cat":
        expert_rules = cat_rules
        pet_name = "cat"
    else:
        raise ValueError("Unsupported pet type. Choose 'dog' or 'cat'.")

    # The Innovative Prompt
    # We give it the VIDEO + the RULES and ask it to be the bridge.
    prompt = f"""
ROLE: You are an expert Animal Behaviorist and a translator specializing in creating humorous, insightful interpretations of pet behavior.

CONTEXT:
Here is a guide to {pet_name} body language:
{expert_rules}

TASK:
Analyze the attached video and provide a structured response in the following format:

**Body Language Analysis:**
- List 2-4 key body language cues observed in the video, with timestamps if possible
- Briefly explain what each cue typically means according to the guide
- Note any combinations of cues that provide additional context

**Humorous Translation:**
Write a short, funny first-person quote (2-4 sentences) from the {pet_name}'s perspective that captures their mood and thoughts based on the analysis. Keep it light-hearted and engaging.

Ensure the analysis is accurate, the translation is creative but grounded in the observed behavior, and the overall response is concise yet informative.
"""

    # Generate
    print(f"\n--- 🐕 Translating {pet_name} mood... ---")
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    response = model.generate_content([video_file, prompt])

    # Optional: Delete file from cloud to save space
    # genai.delete_file(video_file.name)

    return response.text

# For standalone use
if __name__ == "__main__":
    video_path = "my_dog.mp4"  # Change this to your video filename
    pet_type = "dog"  # or "cat"
    result = analyze_pet_mood(pet_type, video_path)
    print(result)
