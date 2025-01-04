from typing import Dict, Any
from openai import OpenAI
import os
import dotenv
import google.generativeai as genai

dotenv.load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")

model = "gemini"
def analyze_chess_game(game_data: Dict[Any, Any], model=model) -> str:
    """
    Analyzes a chess game using either GPT-4 or Gemini
    Args:
        game_data: Dictionary containing game information
        model: "gpt-4o" for GPT-4 or "gemini" for Google's Gemini
    """
    prompt = f"""
    Analyze this chess game and provide a response in EXACTLY this format with NO deviations:

    • Opening: [Opening name with ECO code if available]
    • Key Moments:
      - [Move number + notation] [Brief description of the key moment]
      - [Move number + notation] [Brief description of the key moment]
      - [Move number + notation] [Brief description of the key moment]
    • Final Outcome: [Concise description of how the game ended]
    • Recommendations:
      - [Specific move or position] [Concrete improvement suggestion]
      - [Specific move or position] [Concrete improvement suggestion]
      - [Specific move or position] [Concrete improvement suggestion]

    Chess Game Details:
    White: {game_data['white_player']} ({game_data['white_rating']})
    Black: {game_data['black_player']} ({game_data['black_rating']})
    Result: {game_data['result']}
    PGN: {game_data['pgn']}

    Important formatting rules:
    1. Use EXACT bullet points and indentation shown above
    2. Use the player names instead of colors
    3. Include move numbers and notation in Key Moments
    4. Be specific with positions in Recommendations
    5. No extra line breaks or spacing
    6. No additional sections or text
    
    """

    try:
        if model == "gpt-4o":
            completion = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a chess analysis assistant. Follow the format EXACTLY."},
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content
        elif model == "gemini":
            response = gemini_model.generate_content(prompt)
            return response.text
        else:
            return f"Error: Unsupported model {model}. Use 'gpt-4o' or 'gemini'."
    except Exception as e:
        return f"An error occurred: {e}"
    




