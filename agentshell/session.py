import json
import os
from pathlib import Path
from datetime import datetime

class Session:
    def __init__(self, session_dir=None):
        self.session_dir = session_dir or Path.home() / ".agentshell"
        self.session_file = self.session_dir / "session.json"
        self.max_history = 10
        self._ensure_dir()
    
    def _ensure_dir(self):
        self.session_dir.mkdir(exist_ok=True)
    
    def load(self):
        """Load session history."""
        if not self.session_file.exists():
            return []
        
        try:
            with open(self.session_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def save(self, task, script, outcome):
        """Save interaction to session history."""
        history = self.load()
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "script": script[:500],  # Truncate long scripts
            "outcome": outcome
        }
        
        history.append(entry)
        
        # Keep only last N entries
        if len(history) > self.max_history:
            history = history[-self.max_history:]
        
        with open(self.session_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_context(self, last_n=3):
        """Get recent context for prompt."""
        history = self.load()
        recent = history[-last_n:] if history else []
        
        if not recent:
            return None
        
        context = []
        for entry in recent:
            context.append(f"Task: {entry['task']}\nOutcome: {entry['outcome']}")
        
        return "\n\n".join(context)
