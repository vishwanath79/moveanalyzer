import unittest
from unittest.mock import patch, MagicMock
from main import ChessComAnalyzer

class TestChessComAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ChessComAnalyzer("test_user")
        
    @patch('requests.get')
    def test_get_player_info_success(self, mock_get):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "username": "test_user",
            "player_id": 12345,
            "title": None,
            "status": "premium"
        }
        mock_get.return_value = mock_response
        
        result = self.analyzer.get_player_info()
        self.assertEqual(result["username"], "test_user")
        
    @patch('requests.get')
    def test_get_player_info_failure(self, mock_get):
        # Mock failed API response
        mock_get.side_effect = Exception("API Error")
        
        result = self.analyzer.get_player_info()
        self.assertIn("error", result)
        
    @patch('requests.get')
    def test_get_all_games(self, mock_get):
        # Mock successful archives response
        mock_archives_response = MagicMock()
        mock_archives_response.json.return_value = {
            "archives": ["https://api.chess.com/pub/player/test_user/games/2024/01"]
        }
        
        # Mock successful games response
        mock_games_response = MagicMock()
        mock_games_response.json.return_value = {
            "games": [{
                "url": "https://www.chess.com/game/live/12345",
                "end_time": 1704067200,
                "white": {"username": "test_user", "rating": 1500},
                "black": {"username": "opponent", "rating": 1600},
                "time_control": "600",
                "pgn": "1. e4 e5"
            }]
        }
        
        # Configure mock to return different responses for different URLs
        def mock_get_side_effect(url, headers):
            if url.endswith("archives"):
                return mock_archives_response
            return mock_games_response
            
        mock_get.side_effect = mock_get_side_effect
        
        games = self.analyzer.get_all_games()
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]["white_player"], "test_user")

    def test_get_result(self):
        # Test win result
        game_data = {"white": {"result": "win"}}
        result = self.analyzer._get_result(game_data)
        self.assertEqual(result, "win")
        
        # Test draw result
        game_data = {"rules": "chess", "pgn": "1. e4 e5 1/2-1/2"}
        result = self.analyzer._get_result(game_data)
        self.assertEqual(result, "draw") 