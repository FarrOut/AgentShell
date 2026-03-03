#!/usr/bin/env python3
# Copyright (C) 2026 AgentShell Contributors
# This file is part of AgentShell.
#
# AgentShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AgentShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with AgentShell. If not, see <https://www.gnu.org/licenses/>.

import argparse
import os
import sys
import subprocess
from pathlib import Path

from .ollama_client import OllamaClient
from .lxd_executor import LXDExecutor
from .session import Session

# Whitelist of safe read-only commands
SAFE_COMMANDS = {
    'ls', 'cat', 'grep', 'find', 'head', 'tail', 'wc', 'echo', 'pwd',
    'whoami', 'date', 'df', 'du', 'ps', 'top', 'free', 'uname',
    'journalctl', 'docker', 'git', 'ollama', 'curl', 'wget', 'ping',
    'systemctl', 'which', 'type', 'file', 'stat', 'less', 'more'
}

# Dangerous commands that should never run on host
DANGEROUS_COMMANDS = {
    'rm', 'dd', 'mkfs', 'fdisk', 'parted', 'shutdown', 'reboot', 'init',
    'kill', 'killall', 'pkill', 'chmod', 'chown', 'useradd', 'userdel',
    'passwd', 'su', 'sudo', 'apt', 'apt-get', 'dpkg', 'snap', 'systemctl start',
    'systemctl stop', 'systemctl restart', 'systemctl enable', 'systemctl disable',
    'mv', 'cp', '>', '>>', 'tee', 'truncate', 'shred'
}

def is_script_safe(script):
    """Check if a bash script is safe to run on host."""
    import re
    
    lines = script.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Skip bash built-ins that are safe
        if line.startswith(('set ', 'export ', 'local ')):
            continue
        
        # Skip control flow keywords
        if line in ('then', 'else', 'elif', 'fi', 'do', 'done', 'esac'):
            continue
        
        # Check for dangerous commands anywhere in the line
        for dangerous in DANGEROUS_COMMANDS:
            if re.search(r'\b' + re.escape(dangerous) + r'\b', line):
                return False, f"Dangerous command '{dangerous}' detected"
        
        # Extract commands from command substitutions: $(command) or `command`
        cmd_subs = re.findall(r'\$\(([^)]+)\)|`([^`]+)`', line)
        for sub in cmd_subs:
            cmd_str = sub[0] or sub[1]  # Get whichever matched
            cmd = cmd_str.strip().split()[0] if cmd_str.strip() else ""
            if cmd and cmd not in SAFE_COMMANDS:
                return False, f"Unsafe command '{cmd}' in command substitution"
        
        # Handle pipes: command1 | command2
        if '|' in line:
            # Remove command substitutions first to avoid false positives
            line_no_subs = re.sub(r'\$\([^)]+\)', '', line)
            parts = line_no_subs.split('|')
            for part in parts:
                words = part.strip().split()
                if words:
                    cmd = words[0]
                    if cmd and cmd not in SAFE_COMMANDS and not cmd.startswith('$'):
                        return False, f"Unsafe command '{cmd}' in pipe"
        
        # Handle variable assignments: VAR=value or VAR=$(cmd)
        if '=' in line and not line.startswith(('if ', 'while ', 'for ', '[')):
            # Already checked command substitutions above
            continue
        
        # Handle if/while/for statements
        if line.startswith(('if ', 'while ', 'for ', '[ ', '[[ ')):
            # These are control structures, check commands inside them
            continue
        
        # Check the first word of the line (the actual command)
        words = line.split()
        if words:
            cmd = words[0]
            # Skip bash syntax
            if cmd in ('if', 'then', 'else', 'elif', 'fi', 'while', 'for', 'do', 'done', 'case', 'esac', '[', '[[', 'test'):
                continue
            # Check if command is safe
            if cmd not in SAFE_COMMANDS and not cmd.startswith('$'):
                return False, f"Unsafe command '{cmd}' not in whitelist"
    
    return True, "Script is safe"

def get_last_command():
    """Get last command from shell history."""
    try:
        # Try zsh history first
        history_file = Path.home() / ".zsh_history"
        if not history_file.exists():
            history_file = Path.home() / ".bash_history"
        
        if history_file.exists():
            with open(history_file, 'rb') as f:
                lines = f.readlines()
                if lines:
                    last = lines[-1].decode('utf-8', errors='ignore').strip()
                    # Clean zsh extended history format
                    if ':' in last and ';' in last:
                        last = last.split(';', 1)[1]
                    return last
    except Exception:
        pass
    return None

def extract_script(response):
    """Extract bash script from LLM response."""
    lines = response.strip().split('\n')
    
    # Remove markdown code fences if present
    if lines and lines[0].strip().startswith('```'):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith('```'):
        lines = lines[:-1]
    
    script = '\n'.join(lines).strip()
    
    # Ensure shebang
    if not script.startswith('#!'):
        script = '#!/bin/bash\nset -e\n\n' + script
    
    return script

def main():
    parser = argparse.ArgumentParser(description="AgentShell: Natural language system interface")
    parser.add_argument("task", nargs="+", help="Task description in natural language")
    parser.add_argument("--run-host", action="store_true", help="Run on host (safe commands only)")
    parser.add_argument("--run-container", action="store_true", help="Run in disposable LXD container")
    parser.add_argument("--model", default="llama3", help="Ollama model to use (default: llama3)")
    parser.add_argument("--no-context", action="store_true", help="Don't include session context")
    parser.add_argument("--use-http", action="store_true", help="Force HTTP API instead of CLI")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout for LLM generation in seconds (default: 60)")
    
    args = parser.parse_args()
    task = " ".join(args.task)
    
    # Initialize components
    ollama = OllamaClient(use_cli=not args.use_http)
    executor = LXDExecutor()
    session = Session()
    
    # Gather context
    pwd = os.getcwd()
    last_cmd = get_last_command()
    context = None if args.no_context else session.get_context()
    
    # Build prompt and get response
    method = "CLI" if ollama.use_cli else "HTTP"
    print(f"🤖 Task: {task}")
    print(f"📍 Directory: {pwd}")
    if last_cmd:
        print(f"⏮️  Last command: {last_cmd}")
    print(f"🔧 Using: Ollama {method} with {args.model}")
    print()
    
    try:
        prompt = ollama.build_prompt(task, context=context, pwd=pwd, last_cmd=last_cmd)
        response = ollama.generate(prompt, model=args.model, timeout=args.timeout)
        script = extract_script(response)
        print()  # Blank line after generation
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return 130  # Standard exit code for Ctrl+C
    except TimeoutError as e:
        print(f"\n{e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Error generating script: {e}", file=sys.stderr)
        return 1
    
    # Show script to user
    print("📜 Generated script:")
    print("=" * 60)
    print(script)
    print("=" * 60)
    print()
    
    # Determine execution mode
    if args.run_host:
        exec_mode = "host"
    elif args.run_container:
        exec_mode = "container"
    else:
        # Ask user
        print("Execution options:")
        print("  [h] Run on host (safe commands only)")
        print("  [c] Run in container (isolated)")
        print("  [n] Don't run (default)")
        choice = input("\nChoice [h/c/N]: ").strip().lower()
        
        if choice == 'h':
            exec_mode = "host"
        elif choice == 'c':
            exec_mode = "container"
        else:
            print("Script not executed.")
            session.save(task, script, "not_executed")
            return 0
    
    # Execute
    print()
    try:
        if exec_mode == "host":
            print("🏠 Executing on host (safe mode)...")
            result = executor.execute_on_host(script)
        else:
            print("🐳 Spinning up container...")
            result = executor.execute_in_container(script)
        
        # Show results
        if result["stdout"]:
            print("\n📤 Output:")
            print(result["stdout"])
        
        if result["stderr"]:
            print("\n⚠️  Errors:")
            print(result["stderr"])
        
        exit_code = result["exit_code"]
        print(f"\n✅ Exit code: {exit_code}")
        
        # Save to session
        outcome = f"success (exit {exit_code})" if exit_code == 0 else f"failed (exit {exit_code})"
        session.save(task, script, outcome)
        
        return exit_code
    
    except Exception as e:
        print(f"❌ Execution error: {e}", file=sys.stderr)
        session.save(task, script, f"error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
