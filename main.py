import requests
import datetime
from typing import Dict, Any, List
import json
from ai_model import analyze_chess_game

class ChessComAnalyzer:
    def __init__(self, username: str):
        # Base URL for Chess.com API
        self.base_url = "https://api.chess.com/pub"  # Removed trailing slash
        self.username = username
        # Add headers for API requests
        self.headers = {
            'User-Agent': 'Chess Game Analyzer v1.0 (Contact: your@email.com)'
        }

    def get_player_info(self) -> Dict[Any, Any]:
        """
        Fetches the player information from Chess.com
        Returns the player data as a dictionary
        """
        # Construct the API endpoint for player info
        player_url = f"{self.base_url}/player/{self.username}"
        
        try:
            # Make the API request with headers
            response = requests.get(player_url, headers=self.headers)
            print(player_url)
            response.raise_for_status()
            
            # Get the player data
            player_data = response.json()
            return player_data
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch player info: {str(e)}"}

    def get_player_games(self) -> Dict[Any, Any]:
        """
        Fetches the player's games from Chess.com
        Returns the games data as a dictionary
        """
        # Get player info first to get the games archive URL
        player_info = self.get_player_info()
        
        if "error" in player_info:
            return player_info
            
        # Construct the API endpoint for games archives
        archives_url = f"{self.base_url}/player/{self.username}/games/archives"
        
        try:
            # Get the archives list with headers
            archives_response = requests.get(archives_url, headers=self.headers)
            archives_response.raise_for_status()
            archives_data = archives_response.json()
            
            
            # Get the most recent archive URL
            if archives_data["archives"]:
                latest_games_url = archives_data["archives"][-1]
                
                # Fetch the games from the latest archive with headers
                games_response = requests.get(latest_games_url, headers=self.headers)
                games_response.raise_for_status()
                games_data = games_response.json()
                
                # Get the last game
                if games_data["games"]:
                    last_game = games_data["games"][-1]
                    #print(last_game)
                    return self._format_game_for_llm(last_game)
            
            return {"error": "No games found"}
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch games: {str(e)}"}

    def get_all_games(self) -> List[Dict[Any, Any]]:
        """
        Fetches all games from the current month for a player
        Returns a list of game data dictionaries
        """
        # Get player info first to get the games archive URL
        player_info = self.get_player_info()
        
        if "error" in player_info:
            return []
            
        # Construct the API endpoint for games archives
        archives_url = f"{self.base_url}/player/{self.username}/games/archives"
        
        try:
            # Get the archives list
            archives_response = requests.get(archives_url, headers=self.headers)
            archives_response.raise_for_status()
            archives_data = archives_response.json()
            
            all_games = []
            # Get the most recent archive URL (last month's games)
            if archives_data["archives"]:
                latest_games_url = archives_data["archives"][-1]
                
                # Fetch the games from the latest archive
                games_response = requests.get(latest_games_url, headers=self.headers)
                games_response.raise_for_status()
                games_data = games_response.json()
                
                # Process each game
                for game in games_data.get("games", []):
                    game_data = {
                        'game_id': game['url'].split('/')[-1],
                        'end_time': game['end_time'],
                        'white_player': game['white']['username'],
                        'white_rating': game['white']['rating'],
                        'black_player': game['black']['username'],
                        'black_rating': game['black']['rating'],
                        'result': self._get_result(game),
                        'time_control': game['time_control'],
                        'pgn': game['pgn']
                    }
                    all_games.append(game_data)
                
                return all_games
            
            return []
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch games: {str(e)}"}

    def _get_result(self, game: Dict) -> str:
        """Helper method to determine game result"""
        if 'white' in game and game['white']['result'] == 'win':
            return 'win'
        elif 'black' in game and game['black']['result'] == 'win':
            return 'win'
        elif game.get('rules') == 'chess':
            if game.get('pgn', '').endswith('1/2-1/2'):
                return 'draw'
            else:
                return game.get('white', {}).get('result', 'unknown')
        return 'unknown'

    def _format_game_for_llm(self, game: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Formats the game data in a way that's more suitable for LLM analysis
        Handles missing fields gracefully
        """
        try:
            formatted_game = {
                "white_player": game.get("white", {}).get("username", "Unknown"),
                "black_player": game.get("black", {}).get("username", "Unknown"),
                # Some games might use 'status' instead of 'result'
                "result": game.get("result", game.get("status", "Unknown")),
                "pgn": game.get("pgn", "No PGN available"),
                "time_control": game.get("time_control", "Unknown"),
                "end_time": game.get("end_time", "Unknown"),
                "white_rating": game.get("white", {}).get("rating", "Unknown"),
                "black_rating": game.get("black", {}).get("rating", "Unknown")
            }
            
            # Debug print to see the raw game data
            print("Raw game data:", json.dumps(game, indent=2))
            
            return formatted_game
            
        except Exception as e:
            print(f"Error formatting game data: {str(e)}")
            return {
                "error": "Failed to format game data",
                "raw_game": game
            }

def analyze_with_llm(game_data: Dict[Any, Any]) -> str:
    """
    Sends the game data to the AI model for analysis
    """
    return analyze_chess_game(game_data)

def save_game_analysis(game_data: Dict[Any, Any], analysis: str) -> None:
    """
    Saves the game analysis to chessdb.csv in a structured format
    Checks for duplicates before saving
    """
    import csv
    
    # Create a unique identifier for the game
    game_id = f"{game_data['end_time']}_{game_data['white_player']}_{game_data['black_player']}"
    
    # Format timestamp
    game_date = datetime.datetime.fromtimestamp(game_data['end_time']).strftime('%Y-%m-%d %H:%M:%S')
    
    # Prepare the row data
    row_data = {
        'game_id': game_id,
        'date': game_date,
        'white_player': game_data['white_player'],
        'white_rating': game_data['white_rating'],
        'black_player': game_data['black_player'],
        'black_rating': game_data['black_rating'],
        'result': game_data['result'],
        'time_control': game_data['time_control'],
        'analysis': analysis.replace('\n', ' '),  # Remove newlines for CSV format
        'pgn': game_data['pgn'].replace('\n', ' ')  # Remove newlines for CSV format
    }
    
    # Define the CSV fields
    fields = ['game_id', 'date', 'white_player', 'white_rating', 'black_player', 
              'black_rating', 'result', 'time_control', 'analysis', 'pgn']
    
    # Check if file exists and if game is already in database
    try:
        existing_games = set()
        with open('chessdb.csv', 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_games.add(row['game_id'])
                
        if game_id in existing_games:
            print("Game already exists in database")
            return
            
    except FileNotFoundError:
        # Create new file with headers if it doesn't exist
        with open('chessdb.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
    
    # Append the new game analysis
    with open('chessdb.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writerow(row_data)
    
    print("Game analysis saved to chessdb.csv")

def main():
    # Using your username
    username = "ingvay7"
    
    # Initialize the analyzer
    analyzer = ChessComAnalyzer(username)
    
    # Get player info first
    player_info = analyzer.get_player_info()
    print("Player Info:", json.dumps(player_info, indent=2))
    
    # Get the last game
    game_data = analyzer.get_player_games()
    
    if "error" in game_data:
        print(f"Error: {game_data['error']}")
        return

    # Get the analysis
    analysis = analyze_with_llm(game_data)
    print("\nGame Analysis:")
    print(analysis)
    
    # Save the analysis to the database file
    save_game_analysis(game_data, analysis)

if __name__ == "__main__":
    main()
