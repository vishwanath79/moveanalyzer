import unittest
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from test_chess_analyzer import TestChessComAnalyzer
from test_ai_model import TestAIModel
from test_interface import TestInterface

def run_tests():
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestChessComAnalyzer))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAIModel))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestInterface))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)

if __name__ == '__main__':
    run_tests() 