from typing import Dict, Any
from openai import OpenAI
import os
import dotenv
dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model="gpt-4o"

# def generate_text(prompt, model="gpt-4o"):
#     try:
#         completion = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#             {"role": "developer", "content": "You are a helpful assistant."},
#             {
#                 "role": "user",
#                 "content":  prompt
#             }
#         ]
#     )
#         return completion.choices[0].message.content
#     except Exception as e:
#         return f"An error occurred: {e}"
    

def analyze_chess_game(game_data: Dict[Any, Any], model=model) -> str:
    """
    Analyzes a chess game and returns a summary in bulleted format
    """
    prompt = f"""
    Chess Game Summary:
    {game_data['white_player']} (White, {game_data['white_rating']}) vs 
    {game_data['black_player']} (Black, {game_data['black_rating']})
    
    Game PGN:
    {game_data['pgn']}
    
    Final Result: {game_data['result']}
    
    Please provide a brief summary of this game in the following format:

    • Opening: [Opening name]
    • Key Moments:
      - [First key moment]
      - [Second key moment]
      - [Third key moment if any]
    • Final Outcome: [How the game ended]
    • Recommendations:
      - [First recommendation]
      - [Second recommendation]
      - [Third recommendation if any]

    Note: When referring to players, use their names instead of colors.
    Format the response exactly as shown above with bullet points. NO spacing`
    """

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "developer", "content": "You are a helpful chess analysis assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"
    


