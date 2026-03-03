"""Tests for Ollama client functionality."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from agentshell.ollama_client import OllamaClient


class TestOllamaClient(unittest.TestCase):
    """Test the Ollama client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = OllamaClient()
    
    def test_build_prompt_basic(self):
        """Test basic prompt building."""
        prompt = self.client.build_prompt("list files")
        
        self.assertIn("list files", prompt)
        self.assertIn("bash script", prompt.lower())
    
    def test_build_prompt_with_context(self):
        """Test prompt building with context."""
        context = "Previous output: file1.txt file2.txt"
        prompt = self.client.build_prompt("count the files", context=context)
        
        self.assertIn("count the files", prompt)
        self.assertIn(context, prompt)
    
    def test_build_prompt_with_pwd(self):
        """Test prompt building with working directory."""
        prompt = self.client.build_prompt("list files", pwd="/home/user/project")
        
        self.assertIn("/home/user/project", prompt)
    
    def test_build_prompt_with_last_command(self):
        """Test prompt building with last command."""
        prompt = self.client.build_prompt("show more", last_cmd="ls -la")
        
        self.assertIn("ls -la", prompt)
    
    def test_parse_risk_analysis_complete(self):
        """Test parsing complete risk analysis."""
        response = """
        DOES: Lists all files in the directory
        RISK: LOW
        DANGER: Could be slow on large directories
        RECOMMEND: host
        """
        
        result = self.client._parse_risk_analysis(response)
        
        self.assertEqual(result["does"], "Lists all files in the directory")
        self.assertEqual(result["risk"], "LOW")
        self.assertEqual(result["danger"], "Could be slow on large directories")
        self.assertEqual(result["recommend"], "host")
    
    def test_parse_risk_analysis_partial(self):
        """Test parsing partial risk analysis with defaults."""
        response = """
        DOES: Deletes files
        RISK: HIGH
        """
        
        result = self.client._parse_risk_analysis(response)
        
        self.assertEqual(result["does"], "Deletes files")
        self.assertEqual(result["risk"], "HIGH")
        self.assertEqual(result["recommend"], "container")  # Default
    
    def test_parse_risk_analysis_invalid_risk_level(self):
        """Test that invalid risk levels default to MEDIUM."""
        response = """
        DOES: Does something
        RISK: SUPER_DANGEROUS
        """
        
        result = self.client._parse_risk_analysis(response)
        
        self.assertEqual(result["risk"], "MEDIUM")  # Should default
    
    def test_parse_risk_analysis_case_insensitive(self):
        """Test that parsing is case-insensitive for risk levels."""
        response = """
        RISK: high
        RECOMMEND: Container
        """
        
        result = self.client._parse_risk_analysis(response)
        
        self.assertEqual(result["risk"], "HIGH")
        self.assertEqual(result["recommend"], "container")
    
    def test_parse_risk_analysis_empty(self):
        """Test parsing empty response uses defaults."""
        result = self.client._parse_risk_analysis("")
        
        self.assertEqual(result["risk"], "MEDIUM")
        self.assertEqual(result["recommend"], "container")
    
    def test_parse_risk_analysis_all_levels(self):
        """Test all valid risk levels are recognized."""
        for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            response = f"RISK: {level}"
            result = self.client._parse_risk_analysis(response)
            self.assertEqual(result["risk"], level)
    
    @patch('subprocess.run')
    def test_ollama_cli_detection(self, mock_run):
        """Test Ollama CLI detection."""
        mock_run.return_value = Mock(returncode=0)
        
        client = OllamaClient()
        self.assertTrue(client.has_ollama_cli)
    
    @patch('subprocess.run')
    def test_ollama_cli_not_found(self, mock_run):
        """Test fallback when Ollama CLI not found."""
        mock_run.side_effect = FileNotFoundError()
        
        client = OllamaClient()
        self.assertFalse(client.has_ollama_cli)
    
    @patch('subprocess.run')
    def test_generate_cli_timeout(self, mock_run):
        """Test CLI generation timeout handling."""
        mock_run.side_effect = TimeoutError("Command timed out")
        
        client = OllamaClient()
        
        with self.assertRaises(TimeoutError):
            client._generate_cli("test prompt", model="llama3", timeout=1)
    
    def test_strip_ansi_codes(self):
        """Test ANSI escape code stripping."""
        from agentshell.ollama_client import strip_ansi
        
        text_with_ansi = "\x1b[31mRed text\x1b[0m"
        clean_text = strip_ansi(text_with_ansi)
        
        self.assertEqual(clean_text, "Red text")
        self.assertNotIn("\x1b", clean_text)
    
    def test_strip_ansi_codes_complex(self):
        """Test stripping complex ANSI sequences."""
        from agentshell.ollama_client import strip_ansi
        
        text = "\x1b[1;32mBold Green\x1b[0m \x1b[4mUnderline\x1b[0m"
        clean = strip_ansi(text)
        
        self.assertEqual(clean, "Bold Green Underline")


class TestOllamaClientIntegration(unittest.TestCase):
    """Integration tests for Ollama client (require Ollama running)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = OllamaClient()
    
    @unittest.skipUnless(OllamaClient().has_ollama_cli, "Ollama CLI not available")
    def test_generate_real_response(self):
        """Test generating a real response (requires Ollama)."""
        try:
            response = self.client.generate(
                "Say 'test successful' and nothing else",
                model="llama3.2:3b",
                timeout=30
            )
            
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
        except Exception as e:
            self.skipTest(f"Ollama not available: {e}")
    
    @unittest.skipUnless(OllamaClient().has_ollama_cli, "Ollama CLI not available")
    def test_analyze_risk_real(self):
        """Test real risk analysis (requires Ollama)."""
        try:
            script = "ls -la"
            analysis = self.client.analyze_risk(
                script,
                "list files",
                model="llama3.2:3b"
            )
            
            self.assertIn("risk", analysis)
            self.assertIn("does", analysis)
            self.assertIn("danger", analysis)
            self.assertIn("recommend", analysis)
            
            self.assertIn(analysis["risk"], ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            self.assertIn(analysis["recommend"], ["host", "container"])
        except Exception as e:
            self.skipTest(f"Ollama not available: {e}")


if __name__ == '__main__':
    unittest.main()
