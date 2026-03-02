#!/bin/bash
set -e

echo "🚀 Installing AgentShell..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ python3 required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ docker required"; exit 1; }
command -v zsh >/dev/null 2>&1 || { echo "⚠️  zsh not found, skipping shell integration"; }

# Install agentshell
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect if in virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    pip install -e "$SCRIPT_DIR"
else
    pip3 install --user -e "$SCRIPT_DIR"
fi

echo "✅ AgentShell installed"

# Check if Ollama is running
if command -v ollama >/dev/null 2>&1; then
    echo "✅ Ollama CLI found at $(which ollama)"
    
    if ollama list >/dev/null 2>&1; then
        echo "✅ Ollama service running"
        
        # Check if llama3 is available
        if ! ollama list | grep -q llama3; then
            echo "📥 Pulling llama3 model..."
            ollama pull llama3
        fi
    else
        echo "⚠️  Ollama service not running. Start with: sudo systemctl start ollama"
    fi
else
    echo "⚠️  Ollama not found. Install from: https://ollama.com/download"
fi

# Check LXD
if ! command -v lxc >/dev/null 2>&1; then
    echo ""
    echo "⚠️  LXD not found. Install with:"
    echo "   sudo snap install lxd"
    echo "   sudo lxd init --auto"
    echo "   sudo usermod -aG lxd $USER"
    echo "   newgrp lxd"
else
    if ! lxc list >/dev/null 2>&1; then
        echo "⚠️  LXD not initialized. Run: sudo lxd init --auto"
    else
        echo "✅ LXD ready"
    fi
fi

# Zsh integration
if command -v zsh >/dev/null 2>&1; then
    ZSHRC="$HOME/.zshrc"
    
    if ! grep -q "# AgentShell integration" "$ZSHRC" 2>/dev/null; then
        echo "" >> "$ZSHRC"
        echo "# AgentShell integration" >> "$ZSHRC"
        echo 'alias ash="agentshell"' >> "$ZSHRC"
        echo "" >> "$ZSHRC"
        echo "# Ctrl+A: Quick AI assist for last command" >> "$ZSHRC"
        echo 'agentshell-assist() {' >> "$ZSHRC"
        echo '    local last_cmd=$(fc -ln -1)' >> "$ZSHRC"
        echo '    echo "Last command: $last_cmd"' >> "$ZSHRC"
        echo '    echo -n "Ask AI: "' >> "$ZSHRC"
        echo '    read query' >> "$ZSHRC"
        echo '    agentshell "$query"' >> "$ZSHRC"
        echo '}' >> "$ZSHRC"
        echo 'zle -N agentshell-assist' >> "$ZSHRC"
        echo 'bindkey "^A" agentshell-assist' >> "$ZSHRC"
        
        echo "✅ Zsh integration added to ~/.zshrc"
        echo "   Run: source ~/.zshrc"
    else
        echo "✅ Zsh already configured"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Usage examples:"
echo "  agentshell 'list all docker containers and their status'"
echo "  agentshell 'check nginx logs for errors' --run-container"
echo "  ash 'restart nginx' --run-container"
echo ""
echo "Test GPU acceleration:"
echo "  docker exec ollama nvidia-smi"
