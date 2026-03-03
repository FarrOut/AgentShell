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
    
    def generate(self, prompt, model="llama3", stream=False, timeout=60):
        """Send prompt to Ollama and return response."""
        if self.use_cli and not stream:
            return self._generate_cli(prompt, model, timeout)
        return self._generate_http(prompt, model, stream)
    
    def _generate_cli(self, prompt, model, timeout=60):
        """Use Ollama CLI (faster, native)."""
        import sys
        import time
        import signal
        import re
        
        # Regex to strip ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        try:
            print("⏳ Waiting for Ollama response...", flush=True)
            start_time = time.time()
            
            # Stream output to show progress
            process = subprocess.Popen(
                ["ollama", "run", model, prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Show dots and elapsed time while waiting
            output_lines = []
            last_update = start_time
            
            try:
                while True:
                    # Check if process finished
                    if process.poll() is not None:
                        # Read remaining output
                        remaining = process.stdout.read()
                        if remaining:
                            # Strip ANSI codes from remaining output
                            clean_remaining = ansi_escape.sub('', remaining.strip())
                            if clean_remaining:
                                output_lines.extend(clean_remaining.split('\n'))
                        break
                    
                    # Check timeout
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                        
                        raise TimeoutError(
                            f"⏱️  Generation timed out after {timeout}s\n\n"
                            f"Possible causes:\n"
                            f"  - Model is too large/slow\n"
                            f"  - Ollama is busy with another request\n"
                            f"  - Try a smaller model: --model llama3.2:3b\n\n"
                            f"Tip: Increase timeout with --timeout {timeout * 2}"
                        )
                    
                    # Read available output
                    import select
                    if select.select([process.stdout], [], [], 0.1)[0]:
                        line = process.stdout.readline()
                        if line:
                            # Strip ANSI escape codes
                            clean_line = ansi_escape.sub('', line.rstrip())
                            if clean_line:  # Only add non-empty lines
                                output_lines.append(clean_line)
                    
                    # Update progress every 2 seconds
                    if time.time() - last_update >= 2:
                        print(f" ({int(elapsed)}s)", end="", flush=True)
                        last_update = time.time()
                    else:
                        print(".", end="", flush=True)
                        
            except KeyboardInterrupt:
                print("\n\n⚠️  Cancelled by user", flush=True)
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                raise
            
            print()  # New line after progress
            
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
        
        # System context - teach the LLM about available tools
        system_info = """You are a Linux system assistant generating bash scripts.

AVAILABLE TOOLS:
- Ollama: 
  * ollama list (show downloaded models)
  * ollama ps (show running models)
  * ollama run <model> (run a model)
  * ollama pull <model> (download a model)
- Docker: docker ps, docker logs, docker stats, docker exec
- Git: git status, git log, git diff, git branch
- System: systemctl, journalctl, ps, top, htop, free, df, du
- Files: ls, find, grep, cat, tail, head, less, wc
- Network: curl, wget, ping, netstat, ss
- Package: apt, snap, pip, npm

ENVIRONMENT:
- OS: Ubuntu/Linux
- Shell: bash
- User: standard user (use sudo for system changes)
- Current directory: {pwd}

""".format(pwd=pwd or "unknown")
        
        prompt = system_info + f"TASK: {task}\n"
        
        if last_cmd:
            prompt += f"\nLAST COMMAND EXECUTED: {last_cmd}\n"
        
        if context:
            prompt += f"\nPREVIOUS INTERACTIONS:\n{context}\n"
        
        prompt += """
OUTPUT REQUIREMENTS:
1. Output ONLY valid bash script code
2. Start with #!/bin/bash
3. Include error handling (set -e)
4. Add brief comments ONLY when necessary
5. Use the appropriate tool from the AVAILABLE TOOLS list
6. Keep it simple - don't add unnecessary error checking
7. No explanatory text outside the script
8. Be direct - if the task is "list X", just run the command to list X

Generate the script now:"""
        
        return prompt
    
    def analyze_risk(self, script, original_task, model="llama3"):
        """Analyze the risk of a generated script using the LLM."""
        
        analysis_prompt = f"""You generated this bash script:

{script}

Original task: {original_task}

Analyze this script for risk. Be concise and direct.

1. What does it do? (one sentence)
2. What could go wrong? (one sentence)
3. Risk level: LOW, MEDIUM, HIGH, or CRITICAL
4. Recommendation: host or container?

Output format (exactly):
DOES: [what it does]
RISK: [LOW/MEDIUM/HIGH/CRITICAL]
DANGER: [what could go wrong]
RECOMMEND: [host/container]
"""
        
        try:
            response = self.generate(analysis_prompt, model=model, timeout=30)
            return self._parse_risk_analysis(response)
        except Exception as e:
            # Fallback to safe default if analysis fails
            return {
                "does": "Unknown operation",
                "risk": "MEDIUM",
                "danger": "Unable to analyze risk",
                "recommend": "container"
            }
    
    def _parse_risk_analysis(self, response):
        """Parse the risk analysis response."""
        result = {
            "does": "Unknown",
            "risk": "MEDIUM",
            "danger": "Unknown",
            "recommend": "container"
        }
        
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('DOES:'):
                result["does"] = line.replace('DOES:', '').strip()
            elif line.startswith('RISK:'):
                risk = line.replace('RISK:', '').strip().upper()
                if risk in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
                    result["risk"] = risk
            elif line.startswith('DANGER:'):
                result["danger"] = line.replace('DANGER:', '').strip()
            elif line.startswith('RECOMMEND:'):
                rec = line.replace('RECOMMEND:', '').strip().lower()
                if rec in ['host', 'container']:
                    result["recommend"] = rec
        
        return result
