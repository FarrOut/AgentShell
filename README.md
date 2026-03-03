# AgentShell

**Your personal OODA loop for getting things done.**

Talk to your computer. It listens, learns, and keeps you safe.

```bash
ash "find all docker containers using more than 2GB of memory"
```

AgentShell turns natural language into actions, analyzes the risk, recommends the safest approach, then executes—learning from every interaction.

**Today:** Your intelligent system command interface  
**Tomorrow:** Your autonomous task executor  
**Always:** Local, private, and yours

---

## The OODA Loop

AgentShell implements a continuous learning cycle at two levels:

### Tactical OODA (Current Task)
**Observe** → Understand your request and system context  
**Orient** → Generate script and analyze risk  
**Decide** → Recommend safest approach, you approve  
**Act** → Execute and learn from the outcome  

### Strategic OODA (Long-term Goals)
**Observe** → Read roadmap, understand future capabilities needed  
**Orient** → Evaluate current task against strategic goals  
**Decide** → Identify transferable patterns and skills  
**Act** → Store learnings that prepare for next milestone  

Each interaction makes it smarter **tactically** (better at current tasks) and **strategically** (prepared for future capabilities).

**Example:**
```
Task: "find all Python files"

Tactical learning: "find command works for file discovery"
Strategic learning: "This prepares me for v0.2.0 code file operations"
```

This is **goal-directed learning**—not just learning from everything, but learning toward something.

---

## Why This Exists

You shouldn't need to remember that `docker stats --format "table {{.Container}}\t{{.MemUsage}}"` exists. You shouldn't need to context-switch to Stack Overflow every time you need a one-liner. Your computer should understand intent, not just syntax.

But more than that: **you need a tool you can trust.**

Traditional AI assistants ask you to trust them blindly. "Just approve this command." "Let me run with sudo." One mistake, and your system is compromised.

AgentShell is different. It's **self-aware**—it analyzes its own output for risk, explains what could go wrong, and recommends the safest approach. It's not just generating commands; it's thinking about consequences.

And because it runs locally, it's **yours**. It learns your preferences, adapts to your style, becomes your trusted co-pilot—without sending your data to corporations who profit from surveillance.

### Local is Lekker

**Your commands are yours.** When you ask an AI assistant to help with system tasks, that conversation reveals everything: your infrastructure, your workflows, your problems, your mistakes. We believe that data should stay on your machine.

**No recurring costs.** If you have a GPU, you already have everything you need. No subscriptions, no API fees, no rate limits.

**Works offline.** Secure environments, air-gapped networks, or just a flaky internet connection—AgentShell works regardless.

**Community-owned.** AGPL licensing means this tool can't be taken private or turned into a paid service. Improvements benefit everyone. Your OODA loop, not theirs.

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

## Where We Are (v0.1.0)

**System Command Mastery:**
- ✅ Natural language → bash scripts
- ✅ Intelligent safety checking (not blind approval)
- ✅ Self-aware risk analysis
- ✅ Disposable sandboxes for risky operations
- ✅ Learning from every interaction
- ✅ GPU-accelerated, runs completely local

**You're in control.** Every script is shown. Every risk is explained. Every decision is yours.

---

## Where We're Going

### v0.2.0: Task Assistant
```bash
ash "help me implement issue #15"
ash "analyze these logs and create a report"
ash "organize my project files by type"
```
- Reads context (GitHub, files, system state)
- Suggests approaches
- You approve each step
- Learns your preferences

### v0.3.0: Semi-Autonomous Executor
```bash
ash "implement issue #15" --supervised
ash "monitor system and alert on anomalies" --supervised
```
- Plans multi-step tasks
- Makes coordinated changes
- Validates results
- Asks when uncertain

### v0.4.0: Autonomous Agent
```bash
ash "work on documentation issues" --autonomous
ash "optimize docker images and update configs" --autonomous
```
- Handles complex, multi-part tasks
- Checks in at milestones
- Self-corrects errors
- You steer, ASH navigates

### v0.5.0: Trusted Partner
```bash
ash "implement v0.2.0 milestone" --autonomous
ash "maintain system health this week" --autonomous
```
- Works independently on entire projects
- Handles coding, ops, documentation, analysis
- Only asks when genuinely stuck
- Trust built through consistent results
- **Amplifies you, doesn't replace you**

**The goal:** Not to make you obsolete, but to make you unstoppable.

**The scope:** Whatever you need—code, ops, analysis, automation, research. Your agent, your tasks, your way.

---

## How It Works

AgentShell implements a continuous OODA loop (Observe, Orient, Decide, Act):

### 1. **Observe**
You describe what you want in plain English. AgentShell gathers context:
- Your current directory
- Recent command history
- Past interactions
- Available tools (Docker, Ollama, Git, etc.)

### 2. **Orient**
AI generates a bash script using local Ollama (GPU-accelerated). Then—critically—**it analyzes its own output**:
- What does this script do?
- What could go wrong?
- How risky is it?
- Should it run on host or in a container?

### 3. **Decide**
You see:
- The generated script
- Risk analysis and reasoning
- Recommended execution mode
- Clear explanation of consequences

You make an informed choice.

### 4. **Act**
Execute safely:
- **Host mode**: Read-only and safe commands run directly
- **Container mode**: Risky operations run in disposable LXD containers that self-destruct

The outcome is stored. The loop closes. AgentShell learns.

---

## Features

### 🔒 Self-Aware Safety
- AI analyzes its own output for risk
- Explains what could go wrong
- Recommends safest execution mode
- Intelligent command safety checker (not just blind approval)

### 🧠 Continuous Learning
- Remembers your last interactions
- Learns from successes and failures
- Adapts to your preferences over time
- Gets smarter with every command

### ⚡ GPU-Accelerated & Local
- Uses Ollama with NVIDIA GPU support
- Fast inference on your hardware
- No rate limits, no API costs
- Works completely offline

### 🛡️ Graduated Risk Response
- **Safe commands**: Auto-approved for host
- **Medium risk**: Warning + confirmation
- **Dangerous**: Strong recommendation for container
- **Critical**: Blocked on host, container-only

### 🐳 Disposable Sandboxes
- LXD containers for risky operations
- Test dangerous commands safely
- Automatic cleanup after execution
- "Detonation chamber" for experiments

### 🛠️ Shell Integration
- `ash` command available everywhere
- Ctrl+A keybinding for quick assist
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

**We're building a personal OODA loop for system control:**
- **Your loop**, not a corporation's
- **Your data**, not their training set
- **Your trust**, earned through transparency
- **Your agency**, respected at every step

This isn't about building a SaaS empire. It's about giving people tools they can trust—tools that get smarter without exploiting them, tools that respect sovereignty over convenience.

If you improve AgentShell, we hope you'll share those improvements—but the license ensures you will if you're running it as a service.

**Digital sovereignty through intelligent assistance.**

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
