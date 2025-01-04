import unittest
from unittest.mock import patch, MagicMock
import gradio as gr
from interface import format_results_as_html, analyze_and_format

class TestInterface(unittest.TestCase):
    def setUp(self):
        self.test_results = [{
            'date': '2024-01-01 12:00:00',
            'white_player': 'player1',
            'black_player': 'player2',
            'result': 'win',
            'analysis': '• Opening: Sicilian Defense'
        }]
    
    def test_format_results_as_html(self):
        html = format_results_as_html(self.test_results)
        self.assertIn('player1', html)
        self.assertIn('player2', html)
        self.assertIn('Sicilian Defense', html)
        
    @patch('main.ChessComAnalyzer')
    def test_analyze_and_format_success(self, mock_analyzer):
        # Mock successful game analysis
        mock_analyzer.return_value.get_all_games.return_value = [{
            'end_time': 1704067200,
            'white_player': 'player1',
            'black_player': 'player2',
            'result': 'win'
        }]
        
        status, results = analyze_and_format('test_user', 'All')
        self.assertEqual(status, '')
        self.assertIn('player1', results)
        
    @patch('main.ChessComAnalyzer')
    def test_analyze_and_format_no_games(self, mock_analyzer):
        # Mock no games found
        mock_analyzer.return_value.get_all_games.return_value = []
        
        status, results = analyze_and_format('test_user', 'All')
        self.assertIn('No games found', status)
        self.assertEqual(results, '') 