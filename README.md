# AgentShell

**Talk to your computer. It listens.**

Stop memorizing commands. Stop googling syntax. Just say what you want.

```bash
ash "find all docker containers using more than 2GB of memory"
```

AgentShell turns natural language into bash scripts, shows you what it's about to do, then executes it safely—either on your machine or in a disposable sandbox.

---

## Why This Exists

You shouldn't need to remember that `docker stats --format "table {{.Container}}\t{{.MemUsage}}"` exists. You shouldn't need to context-switch to Stack Overflow every time you need a one-liner. Your computer should understand intent, not just syntax.

AgentShell is built on a simple belief: **powerful tools should be accessible, transparent, and owned by the people who use them**—not locked behind proprietary APIs or cloud services that disappear when you stop paying.

### Local is Lekker

**Your commands are yours.** When you ask an AI assistant to help with system tasks, that conversation reveals a lot: your infrastructure, your workflows, your problems. We believe that data should stay on your machine.

**No recurring costs.** If you have a GPU, you already have everything you need. No subscriptions, no API fees, no rate limits.

**Works offline.** Secure environments, air-gapped networks, or just a flaky internet connection—AgentShell works regardless.

**Community-owned.** AGPL licensing means this tool can't be taken private or turned into a paid service. Improvements benefit everyone.

---

## Quick Start

```bash
# Install
pipx install git+https://github.com/FarrOut/AgentShell.git

# Use
ash "list all files modified in the last hour"
ash "check nginx logs for 500 errors" --run-container
```

That's it. No API keys. No cloud accounts. No tracking.

---

## How It Works

1. **You describe what you want** in plain English
2. **AI generates a bash script** (using Ollama running locally on your GPU)
3. **You review the script** before anything runs
4. **Execute safely**:
   - Read-only commands run on your host
   - Dangerous stuff runs in a disposable container that self-destructs

Everything runs locally. Your commands, your data, your machine.

---

## Features

### 🔒 Security First
- Never auto-executes without your approval
- Dangerous commands isolated in disposable LXD containers
- Read-only operations whitelisted for host execution
- No credentials stored in history

### 🧠 Context-Aware
- Remembers your last few interactions
- Knows your current directory
- Sees your shell history
- Learns from what you've done

### ⚡ GPU-Accelerated
- Uses Ollama with NVIDIA GPU support
- Fast inference on local hardware
- No rate limits, no API costs
- Works offline

### 🛠️ Shell Integration
- `ash` command available everywhere
- Ctrl+A keybinding for quick AI assist
- Works with your existing workflow

---

## Installation

### Prerequisites
- Ubuntu 22.04+ (or similar Linux)
- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- LXD (for sandboxing): `sudo snap install lxd && sudo lxd init --auto`
- Optional: NVIDIA GPU for faster inference

### Install with pipx
```bash
pipx install git+https://github.com/FarrOut/AgentShell.git
```

### Or install from source
```bash
git clone https://github.com/FarrOut/AgentShell.git
cd AgentShell
pipx install -e .
```

---

## Usage Examples

### Basic Tasks
```bash
# System inspection
ash "show me disk usage by directory"
ash "list all running services"
ash "find large files in /var/log"

# With specific models
ash "analyze this error log" --model llama3.2:3b

# Force container execution
ash "install and configure nginx" --run-container
```

### Interactive Mode
```bash
ash "restart docker"
# Shows generated script:
# #!/bin/bash
# set -e
# sudo systemctl restart docker
# sudo systemctl status docker

# Prompts: [h]ost / [c]ontainer / [N]o
```

### Zsh Integration
Press `Ctrl+A` after any command to ask the AI about it:
```bash
$ docker ps
# Press Ctrl+A
# Last command: docker ps
# Ask AI: why are these containers restarting?
```

---

## Configuration

### Session History
Located at `~/.agentshell/session.json`
- Stores last 10 interactions
- Used for context in future prompts
- No credentials or sensitive data

### Safe Commands Whitelist
Edit `SAFE_COMMANDS` in `agentshell/main.py` to customize which commands can run on host without sandboxing.

### Ollama Models
Default: `llama3`

Change with `--model`:
```bash
ash "task" --model mistral
ash "task" --model llama3.2:3b
```

---

## Architecture

```
┌─────────────────┐
│   Natural       │
│   Language      │
│   Input         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Ollama        │
│   (Local GPU)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Generated     │
│   Bash Script   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   User          │
│   Approval      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│  Host  │ │Container │
│  (safe)│ │(isolated)│
└────────┘ └──────────┘
```

**Components:**
- `main.py` - CLI interface and approval workflow
- `ollama_client.py` - Local LLM communication (HTTP/CLI)
- `lxd_executor.py` - Container sandboxing
- `session.py` - Context persistence

---

## Philosophy

AgentShell is AGPL-licensed because we believe powerful tools should remain in the commons. If someone builds a service on top of this, users deserve access to the source code.

We're not interested in building a SaaS empire. We're interested in making computers more accessible to humans.

If you improve AgentShell, we hope you'll share those improvements—but the license ensures you will if you're running it as a service.

---

## Ollama Model Selection for RTX 4060 Laptop (8GB VRAM)

**Hardware Benchmark**: NVIDIA RTX 4060 Max-Q (8GB VRAM), Intel i7-13700HX (24 threads), 32GB RAM

### Recommended Model Stack

**Tier 1: Daily Driver**
qwen2.5:14b-instruct-q4_K_M # ~7.5GB VRAM - 90% of tasks (coding/sysadmin/reasoning)

**Tier 2: Category Specialists**

deepseek-r1:7b-q4_K_M # 🧠 Thinking (complex logic) ~4GB

llava:7b-q4_K_M # 👁️ Vision (image analysis) ~4.5GB

nomic-embed-text:1.5b # 📊 Embedding (RAG/search) ~1GB


### Model Categories Explained

| Category | Purpose | Example Use Case |
|----------|---------|------------------|
| 🧠 Thinking | Advanced reasoning, math, planning | "Step-by-step analyze security breach patterns" |
| 👁️ Vision | Image analysis, OCR, screenshot debugging | "What's unusual in this forensic screenshot?" |
| 🔧 Tools | Function calling, structured JSON output | Docker automation scripts |
| 📊 Embedding | Vector search, document clustering | Local bash script semantic search |

### When to Switch Models (Decision Tree)
┌─ Start with: qwen2.5:14b (handles 90%)
├─ Images/screenshots? → llava:7b
├─ Complex logic puzzles? → deepseek-r1:7b
├─ Document search? → nomic-embed-text
└─ Response garbage? → Check nvidia-smi → smaller quantization


**Hardware Feedback** (run `watch nvidia-smi`):

✅ 80-95% GPU util, <10s response → STAY

⚠️ 95-100% VRAM, slow tokens → smaller model

💥 OOM/crash → q4_0 → q4_K_S quantization


### Quick Commands
```bash
# Default (add to ~/.bashrc)
alias ollama="ollama run qwen2.5:14b-instruct-q4_K_M"

# Check loaded models
ollama ps

# Test specialist
ollama run llava:7b "/path/to/image.png Describe issues"
```

Total: ~16GB disk, never exceeds 8GB VRAM simultaneously. Qwen2.5 14B maximizes RTX 4060 capability for sysadmin/AI work.

---

## Troubleshooting

**Command not found:**
```bash
# Make sure pipx bin directory is in PATH
pipx ensurepath
source ~/.zshrc
```

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

**Slow inference:**
- Check GPU is detected: `nvidia-smi`
- Use smaller models: `--model llama3.2:3b`
- Ensure Ollama is using GPU (check with `ollama ps`)

---

## Contributing

Found a bug? Have an idea? PRs welcome.

This is a community project. No corporate overlords, no VC funding, no growth metrics. Just people making tools better.

---

## License

GNU Affero General Public License v3.0

**What this means:**
- ✅ Use it freely
- ✅ Modify it however you want
- ✅ Run it commercially
- ⚠️ If you offer it as a network service, you must share your source code

See [LICENSE](LICENSE) for full terms.

---

**Built with:** Python • Ollama • LXD • A belief that good tools should be free
