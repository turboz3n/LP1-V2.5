# LP1 – The Self-Evolving AI System

**LP1** is an autonomous, modular, self-improving AI assistant. It's designed to be:
- Kind, helpful, and ethical
- Modular and expandable
- Capable of introspection and evolution

## Setup

### 1. Clone the Repo
```bash
git clone https://github.com/YOURUSER/lp1.git
cd lp1
```

### 2. Configure API Keys
```bash
cp .env .env.local
```
Edit `.env.local`:
```
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf-...
```

### 3. Bootstrap Environment
```bash
bash init.sh
```

### 4. Run LP1
```bash
source venv/bin/activate
python lp1/main.py
```

---

## Features
- Semantic skill routing
- Self-rewriting + patch approval
- Feedback loop + evolution
- Memory, vision, introspection
- Theory of mind simulation
