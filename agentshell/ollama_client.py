import requests
import json
import subprocess
import shutil

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", use_cli=None):
        self.base_url = base_url
        self.generate_url = f"{base_url}/api/generate"
        
        # Auto-detect: prefer CLI if available
        if use_cli is None:
            self.use_cli = shutil.which("ollama") is not None
        else:
            self.use_cli = use_cli
    
    def generate(self, prompt, model="llama3", stream=False):
        """Send prompt to Ollama and return response."""
        if self.use_cli and not stream:
            return self._generate_cli(prompt, model)
        return self._generate_http(prompt, model, stream)
    
    def _generate_cli(self, prompt, model):
        """Use Ollama CLI (faster, native)."""
        import sys
        try:
            print("⏳ Waiting for Ollama response...", flush=True)
            
            # Stream output to show progress
            process = subprocess.Popen(
                ["ollama", "run", model, prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Show dots while waiting
            output_lines = []
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    output_lines.append(line.rstrip())
                    print(".", end="", flush=True)
            
            print()  # New line after dots
            
            _, stderr = process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"Ollama CLI error: {stderr}")
            
            return "\n".join(output_lines).strip()
        except FileNotFoundError:
            raise RuntimeError("Ollama CLI not found")
    
    def _generate_http(self, prompt, model, stream):
        """Use Ollama HTTP API (fallback)."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        try:
            response = requests.post(self.generate_url, json=payload, timeout=120)
            response.raise_for_status()
            
            if stream:
                return response.iter_lines()
            
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama HTTP request failed: {e}")
    
    def build_prompt(self, task, context=None, pwd=None, last_cmd=None):
        """Build a structured prompt for the LLM."""
        prompt = f"""You are a Linux system assistant. Generate a bash script to accomplish this task:

TASK: {task}
"""
        
        if pwd:
            prompt += f"\nCURRENT DIRECTORY: {pwd}"
        
        if last_cmd:
            prompt += f"\nLAST COMMAND: {last_cmd}"
        
        if context:
            prompt += f"\n\nPREVIOUS CONTEXT:\n{context}"
        
        prompt += """

REQUIREMENTS:
1. Output ONLY valid bash script code
2. Start with #!/bin/bash
3. Include error handling (set -e)
4. Add brief comments for each step
5. No explanatory text outside the script

Generate the script now:"""
        
        return prompt
