import unittest
from unittest.mock import patch, MagicMock
from ai_model import analyze_chess_game

class TestAIModel(unittest.TestCase):
    def setUp(self):
        self.test_game_data = {
            'white_player': 'player1',
            'white_rating': 1500,
            'black_player': 'player2',
            'black_rating': 1600,
            'pgn': '1. e4 e5 2. Nf3 Nc6',
            'result': 'win'
        }
    
    @patch('openai.OpenAI')
    def test_analyze_chess_game_success(self, mock_openai):
        # Mock successful API response
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "• Opening: Italian Game"
        mock_openai.return_value.chat.completions.create.return_value = mock_completion
        
        result = analyze_chess_game(self.test_game_data)
        self.assertIn("Opening", result)
        
    @patch('openai.OpenAI')
    def test_analyze_chess_game_failure(self, mock_openai):
        # Mock API error
        mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
        
        result = analyze_chess_game(self.test_game_data)
        self.assertIn("An error occurred", result) 