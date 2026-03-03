"""Tests for session management."""

import unittest
import tempfile
import json
import os
from pathlib import Path
from agentshell.session import Session


class TestSession(unittest.TestCase):
    """Test session management functionality."""
    
    def setUp(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.session = Session(session_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary files."""
        session_file = Path(self.temp_dir) / "session.json"
        if session_file.exists():
            session_file.unlink()
        os.rmdir(self.temp_dir)
    
    def test_save_interaction(self):
        """Test saving a single interaction."""
        self.session.save(
            task="list files",
            script="ls -la",
            outcome="Success: Listed 5 files"
        )
        
        history = self.session.load()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["task"], "list files")
        self.assertEqual(history[0]["script"], "ls -la")
    
    def test_save_multiple_interactions(self):
        """Test saving multiple interactions."""
        for i in range(5):
            self.session.save(
                task=f"task {i}",
                script=f"script {i}",
                outcome=f"outcome {i}"
            )
        
        history = self.session.load()
        self.assertEqual(len(history), 5)
    
    def test_max_history_limit(self):
        """Test that history is limited to max_history entries."""
        # Save more than max_history (default 10)
        for i in range(15):
            self.session.save(
                task=f"task {i}",
                script=f"script {i}",
                outcome=f"outcome {i}"
            )
        
        history = self.session.load()
        self.assertEqual(len(history), 10)
        
        # Should keep the most recent ones
        self.assertEqual(history[0]["task"], "task 5")
        self.assertEqual(history[-1]["task"], "task 14")
    
    def test_get_context(self):
        """Test getting formatted context."""
        self.session.save(
            task="list files",
            script="ls -la",
            outcome="Success: Listed files"
        )
        
        context = self.session.get_context()
        self.assertIn("list files", context)
        self.assertIn("Success", context)
    
    def test_get_context_empty(self):
        """Test getting context when history is empty."""
        context = self.session.get_context()
        self.assertIsNone(context)
    
    def test_get_context_limit(self):
        """Test getting context with limit."""
        for i in range(5):
            self.session.save(
                task=f"task {i}",
                script=f"script {i}",
                outcome=f"outcome {i}"
            )
        
        context = self.session.get_context(last_n=2)
        
        # Should only include last 2
        self.assertIn("task 3", context)
        self.assertIn("task 4", context)
        self.assertNotIn("task 0", context)
        self.assertNotIn("task 1", context)
    
    def test_persistence(self):
        """Test that sessions persist across instances."""
        # Save with first instance
        self.session.save(
            task="persistent task",
            script="persistent script",
            outcome="persistent outcome"
        )
        
        # Load with new instance
        new_session = Session(session_dir=self.temp_dir)
        history = new_session.load()
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["task"], "persistent task")
    
    def test_timestamp_recorded(self):
        """Test that timestamps are recorded."""
        self.session.save(
            task="test",
            script="test",
            outcome="test"
        )
        
        history = self.session.load()
        self.assertIn("timestamp", history[0])
        self.assertIsInstance(history[0]["timestamp"], str)
    
    def test_corrupted_session_file(self):
        """Test handling of corrupted session file."""
        session_file = Path(self.temp_dir) / "session.json"
        
        # Write invalid JSON
        with open(session_file, 'w') as f:
            f.write("not valid json{{{")
        
        # Should handle gracefully and start fresh
        session = Session(session_dir=self.temp_dir)
        history = session.load()
        self.assertEqual(len(history), 0)
    
    def test_long_script_truncation(self):
        """Test that long scripts are truncated."""
        long_script = "echo " + "x" * 1000
        
        self.session.save(
            task="test",
            script=long_script,
            outcome="test"
        )
        
        history = self.session.load()
        # Should be truncated to 500 chars
        self.assertLessEqual(len(history[0]["script"]), 500)


if __name__ == '__main__':
    unittest.main()
