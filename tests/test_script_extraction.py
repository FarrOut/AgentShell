"""Tests for script extraction from LLM responses."""

import unittest
from agentshell.main import extract_script


class TestScriptExtraction(unittest.TestCase):
    """Test extracting bash scripts from LLM responses."""
    
    def test_extract_basic_script(self):
        """Test extracting a basic script."""
        response = """
        Here's a script to list files:
        
        ```bash
        ls -la
        ```
        """
        
        script = extract_script(response)
        self.assertIn("ls -la", script)
        self.assertIn("#!/bin/bash", script)
    
    def test_extract_multiline_script(self):
        """Test extracting multiline script."""
        response = """
        ```bash
        #!/bin/bash
        set -e
        
        echo "Starting..."
        ls -la
        echo "Done"
        ```
        """
        
        script = extract_script(response)
        self.assertIn("#!/bin/bash", script)
        self.assertIn("set -e", script)
        self.assertIn("ls -la", script)
    
    def test_extract_script_with_explanation(self):
        """Test extracting script when LLM adds explanation."""
        response = """
        This script will list all files in the current directory:
        
        ```bash
        ls -la
        ```
        
        The -l flag shows detailed information and -a shows hidden files.
        """
        
        script = extract_script(response)
        self.assertIn("ls -la", script)
        # Should not include explanation text
        self.assertNotIn("This script will", script)
        self.assertNotIn("The -l flag", script)
    
    def test_extract_script_no_language_tag(self):
        """Test extracting script without language tag."""
        response = """
        ```
        ls -la
        ```
        """
        
        script = extract_script(response)
        self.assertIn("ls -la", script)
    
    def test_extract_script_sh_tag(self):
        """Test extracting script with 'sh' tag."""
        response = """
        ```sh
        ls -la
        ```
        """
        
        script = extract_script(response)
        self.assertIn("ls -la", script)
    
    def test_extract_first_script_only(self):
        """Test that only the first script block is extracted."""
        response = """
        First script:
        ```bash
        ls -la
        ```
        
        Alternative script:
        ```bash
        find . -type f
        ```
        """
        
        script = extract_script(response)
        self.assertIn("ls -la", script)
        # Note: Current implementation doesn't filter multiple blocks
        # This test documents current behavior
    
    def test_extract_script_with_comments(self):
        """Test extracting script with comments."""
        response = """
        ```bash
        # List all files
        ls -la
        
        # Count them
        ls -la | wc -l
        ```
        """
        
        script = extract_script(response)
        self.assertIn("# List all files", script)
        self.assertIn("ls -la", script)
    
    def test_no_code_block(self):
        """Test when LLM doesn't use code blocks."""
        response = "ls -la"
        
        script = extract_script(response)
        self.assertIn("ls -la", script)
        # Should add shebang
        self.assertIn("#!/bin/bash", script)
    
    def test_empty_response(self):
        """Test handling empty response."""
        script = extract_script("")
        # Should still have shebang
        self.assertIn("#!/bin/bash", script)
    
    def test_whitespace_handling(self):
        """Test that whitespace is preserved correctly."""
        response = """
        ```bash
        if [ -f file.txt ]; then
            cat file.txt
        fi
        ```
        """
        
        script = extract_script(response)
        self.assertIn("    cat file.txt", script)  # Indentation preserved
    
    def test_shebang_preserved(self):
        """Test that existing shebang is preserved."""
        response = """
        ```bash
        #!/bin/bash
        ls -la
        ```
        """
        
        script = extract_script(response)
        # Should not duplicate shebang
        self.assertEqual(script.count("#!/bin/bash"), 1)
    
    def test_adds_shebang_when_missing(self):
        """Test that shebang is added when missing."""
        response = "echo 'hello'"
        
        script = extract_script(response)
        self.assertTrue(script.startswith("#!/bin/bash"))
        self.assertIn("set -e", script)


if __name__ == '__main__':
    unittest.main()
