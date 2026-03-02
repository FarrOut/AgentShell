# AgentShell

🤖 AI-powered system interface: natural language → bash scripts → sandboxed execution. GPU-accelerated with Ollama.

## Features

- **GPU-Accelerated**: Uses Ollama with NVIDIA GPU support for fast inference
- **Secure by Design**: Sandboxes mutating commands in disposable LXD containers
- **Context-Aware**: Remembers recent interactions and current working directory
- **Interactive Approval**: Shows generated scripts before execution
- **Zsh Integration**: `ash` alias and Ctrl+A keybinding

## Prerequisites

- Ubuntu 22.04+ with NVIDIA GPU
- Docker with nvidia-docker support
- Python 3.10+
- Zsh (optional, for shell integration)

## Installation

```bash
cd ai-ui
chmod +x zsh_setup.sh
./zsh_setup.sh
source ~/.zshrc
```

This will:
1. Install the `agentshell` Python package
2. Configure Zsh aliases and keybindings

## Usage

### Basic Usage

```bash
# Interactive mode (asks for approval)
agentshell "list all running docker containers"

# Short alias
ash "show disk usage" --run-host

# Run in isolated container
ash "install nginx and start it" --run-container

# Use different model
ash "analyze system logs" --model mistral
```

### With Zsh Integration

Press `Ctrl+A` in Zsh to:
1. See your last command
2. Ask the AI about it
3. Get an automated solution

## How It Works

1. **Task Input**: You describe what you want in natural language
2. **Script Generation**: Ollama (running on GPU) generates a bash script
3. **User Approval**: The script is shown for review
4. **Execution**:
   - **Host mode**: Only whitelisted safe commands (ls, cat, grep, etc.)
   - **Container mode**: Full isolation in disposable LXD container
5. **Context Storage**: Interaction saved to `~/.agentshell/session.json`

## Security Model

- **Never auto-executes** destructive commands
- **Host execution** restricted to read-only whitelist
- **Container execution** uses disposable LXD containers (destroyed after use)
- **No credential storage** in session history

## Examples

```bash
# Safe read-only task (runs on host)
ash "find all Python files modified today" --run-host

# System modification (runs in container)
ash "install htop and show process tree" --run-container

# With context from previous interactions
ash "do the same for nginx logs"
```

## Configuration

- **Session history**: `~/.agentshell/session.json`
- **Max history entries**: 10 (configurable in `session.py`)
- **Safe commands whitelist**: Edit `SAFE_COMMANDS` in `main.py`
- **Ollama endpoint**: Default `http://localhost:11434`

## Troubleshooting

**Ollama not responding:**
```bash
systemctl status ollama
sudo systemctl restart ollama
```

**LXD not initialized:**
```bash
sudo snap install lxd
sudo lxd init --auto
sudo usermod -aG lxd $USER
newgrp lxd
```

**GPU not detected:**
```bash
nvidia-smi  # Verify drivers
```

## Architecture

```
agentshell/
├── main.py           # CLI entry point, approval workflow
├── ollama_client.py  # HTTP/CLI client for Ollama
├── lxd_executor.py   # Container sandboxing
└── session.py        # Context persistence
```

## License

MIT
