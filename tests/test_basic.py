"""
Basic unit tests for MynaAPI core functionality.
These tests don't require external API access.
"""
import unittest
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBasicFunctionality(unittest.TestCase):
    """Basic functionality tests that don't require external APIs."""
    
    def test_imports(self):
        """Test that basic imports work."""
        try:
            from app.main import app
            from app.config.settings import settings
            from app.utils.helpers import generate_session_id
            self.assertTrue(True)  # If imports work, test passes
        except ImportError as e:
            self.fail(f"Import failed: {str(e)}")
    
    def test_session_id_generation(self):
        """Test session ID generation utility."""
        try:
            from app.utils.helpers import generate_session_id
            session_id = generate_session_id()
            self.assertIsInstance(session_id, str)
            self.assertGreater(len(session_id), 0)
        except Exception as e:
            self.fail(f"Session ID generation failed: {str(e)}")
    
    def test_app_creation(self):
        """Test FastAPI app creation."""
        try:
            from app.main import app
            self.assertIsNotNone(app)
        except Exception as e:
            self.fail(f"App creation failed: {str(e)}")


if __name__ == '__main__':
    unittest.main()
