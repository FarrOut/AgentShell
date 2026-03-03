"""Integration tests for the full AgentShell workflow."""

import unittest
import subprocess
import tempfile
import os
from pathlib import Path


class TestAgentShellCLI(unittest.TestCase):
    """Integration tests for the AgentShell CLI."""
    
    def test_cli_help(self):
        """Test that CLI help works."""
        result = subprocess.run(
            ["ash", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("AgentShell", result.stdout)
    
    def test_cli_version(self):
        """Test that version flag works."""
        result = subprocess.run(
            ["ash", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("0.1.0", result.stdout)
    
    def test_cli_requires_task(self):
        """Test that CLI requires a task argument."""
        result = subprocess.run(
            ["ash"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        self.assertNotEqual(result.returncode, 0)


class TestEndToEndWorkflow(unittest.TestCase):
    """End-to-end workflow tests (require Ollama)."""
    
    @unittest.skipUnless(
        subprocess.run(["which", "ollama"], capture_output=True).returncode == 0,
        "Ollama not available"
    )
    def test_simple_safe_command(self):
        """Test executing a simple safe command."""
        result = subprocess.run(
            ["ash", "echo hello world", "--model", "llama3.2:3b", "--run-host"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Should complete successfully
        self.assertEqual(result.returncode, 0)
        
        # Should show the workflow
        self.assertIn("Generated script", result.stdout)
        self.assertIn("Analyzing risk", result.stdout)
        self.assertIn("Executing", result.stdout)
    
    @unittest.skipUnless(
        subprocess.run(["which", "ollama"], capture_output=True).returncode == 0,
        "Ollama not available"
    )
    def test_dangerous_command_blocked(self):
        """Test that dangerous commands are blocked on host."""
        result = subprocess.run(
            ["ash", "delete everything", "--model", "llama3.2:3b", "--run-host"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Should show risk analysis
        self.assertIn("Analyzing risk", result.stdout)
        
        # Should either block or recommend container
        output = result.stdout.lower()
        self.assertTrue(
            "blocked" in output or 
            "container" in output or
            "dangerous" in output
        )


class TestSafetyIntegration(unittest.TestCase):
    """Integration tests for safety features."""
    
    def test_safety_checker_integration(self):
        """Test that safety checker is properly integrated."""
        from agentshell.main import is_script_safe
        from agentshell.lxd_executor import execute_on_host
        
        # Safe command should work
        safe_script = "echo 'test'"
        result = execute_on_host(safe_script)
        self.assertEqual(result["exit_code"], 0)
        
        # Dangerous command should be blocked
        dangerous_script = "rm -rf /"
        result = execute_on_host(dangerous_script)
        self.assertNotEqual(result["exit_code"], 0)
        self.assertIn("blocked", result["output"].lower())


if __name__ == '__main__':
    unittest.main()
