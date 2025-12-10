# SageMaker + GitHub Setup Guide

This guide helps you connect your SageMaker Jupyter notebook environment to the team's GitHub repository.

**Repository URL:** https://github.com/bfisher-bah/BAH-Agentic-AI-Capstone

---

## For Repo Owner: Adding Team Members

*This section is for Brian (bfisher-bah) to grant teammates access.*

### Step 1: Add Collaborators to the Repository

1. Go to: https://github.com/bfisher-bah/BAH-Agentic-AI-Capstone/settings/access
2. Click **"Add people"** (or "Invite a collaborator")
3. Enter each teammate's **GitHub username** or **email address**
4. Select permission level:
   - **Write** (recommended) - Can push, pull, and manage issues
   - **Admin** - Full access including settings (only if needed)
5. Click **"Add [username] to this repository"**
6. Teammate will receive an email invitation to accept

### Step 2: Share This Information with Teammates

Send your teammates:
- Repository URL: `https://github.com/bfisher-bah/BAH-Agentic-AI-Capstone`
- This setup guide (or tell them it's in the repo)
- Reminder to **accept the GitHub invitation** before they can push

### Note: If Teammates Don't Have GitHub Accounts

They'll need to create one first:
1. Go to https://github.com/join
2. Create a free account
3. Send you their username so you can add them as collaborators

---

## For Teammates: Quick Start Checklist

*Follow these steps in order to get set up on your SageMaker instance.*

- [ ] **Accept the GitHub invitation** (check your email from GitHub)
- [ ] Create a Personal Access Token (Step 3 below)
- [ ] Clone the repo in SageMaker (Step 1 below)
- [ ] Configure your Git identity (Step 2 below)
- [ ] Set up authentication (Step 3 below)
- [ ] Install Python dependencies (Step 5 below)
- [ ] Set up OpenAI API key (Step 6 below)
- [ ] Test with `git pull` and a small test commit

---

## Step 1: Clone the Repository into SageMaker

1. Open your SageMaker notebook instance
2. Launch a **Terminal** (File → New → Terminal, or from the Launcher)
3. Navigate to the SageMaker directory and clone:

```bash
cd ~/SageMaker
git clone https://github.com/bfisher-bah/BAH-Agentic-AI-Capstone.git
cd BAH-Agentic-AI-Capstone
```

4. Verify the files are there:
```bash
ls -la
```

You should see `CAPSTONE_PROJECT_PLAN.md`, `ALTERNATIVE_PROJECT_IDEAS.md`, and the lab files.

---

## Step 2: Configure Git Identity

Set your Git identity (required for commits):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Step 3: Set Up GitHub Authentication (For Pushing)

Since you'll need to push code back to GitHub, you need authentication.

### Option A: Personal Access Token (Recommended - Simplest)

1. **Generate a PAT on GitHub:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Give it a name like "SageMaker Access"
   - Select scopes: `repo` (full control of private repositories)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again!)

2. **Store credentials in SageMaker** (so you don't have to enter them every time):
```bash
git config --global credential.helper store
```

3. **First push will prompt for credentials:**
   - Username: `bfisher-bah` (or your GitHub username)
   - Password: Paste your Personal Access Token (NOT your GitHub password)

### Option B: SSH Key (More Secure, More Setup)

1. **Generate SSH key in SageMaker:**
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
# Press Enter to accept default location
# Enter a passphrase (optional)
```

2. **Display your public key:**
```bash
cat ~/.ssh/id_ed25519.pub
```

3. **Add to GitHub:**
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste the public key
   - Save

4. **Switch repo to SSH URL:**
```bash
cd ~/SageMaker/BAH-Agentic-AI-Capstone
git remote set-url origin git@github.com:bfisher-bah/BAH-Agentic-AI-Capstone.git
```

---

## Step 4: Basic Git Workflow

### Pull Latest Changes (Before Starting Work)
```bash
cd ~/SageMaker/BAH-Agentic-AI-Capstone
git pull origin main
```

### Save Your Work (Commit and Push)
```bash
# Check what's changed
git status

# Add your changes
git add .

# Or add specific files
git add your-notebook.ipynb

# Commit with a message
git commit -m "Add ticket classification agent"

# Push to GitHub
git push origin main
```

### If Someone Else Pushed Changes
```bash
# Pull their changes first
git pull origin main

# Then push yours
git push origin main
```

---

## Step 5: Install Python Dependencies

In a SageMaker terminal or notebook cell:

```bash
pip install langchain==0.3.* langchain_openai==0.3.* langchain_community langgraph==0.4.* websockets==15.0.*
pip install "unstructured[md]==0.17.*"
pip install --only-binary=:all: tiktoken
```

Or in a notebook cell:
```python
!pip install langchain==0.3.* langchain_openai==0.3.* langchain_community langgraph==0.4.* websockets==15.0.*
!pip install "unstructured[md]==0.17.*"
!pip install --only-binary=:all: tiktoken
```

---

## Step 6: Set Up OpenAI API Key

### Option A: Environment Variable (Recommended)

In your notebook, add this cell at the top:
```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

**Important:** Don't commit this to Git! Use a separate config file or enter it manually each session.

### Option B: Using a .env File (Better for Teams)

1. Create a `.env` file (already in .gitignore):
```bash
echo 'OPENAI_API_KEY=your-api-key-here' > .env
```

2. Load it in your notebook:
```python
from dotenv import load_dotenv
load_dotenv()
```

(Requires: `pip install python-dotenv`)

---

## Troubleshooting

### "Permission denied" when pushing
- Your PAT may have expired or lacks `repo` scope
- Generate a new token and try again

### "Repository not found"
- Check the URL is correct
- Make sure you have access to the repo (collaborator or owner)

### Merge conflicts
```bash
# Pull and see conflicts
git pull origin main

# Edit the conflicting files to resolve
# Then:
git add .
git commit -m "Resolve merge conflicts"
git push origin main
```

### Reset to match GitHub (discard local changes)
```bash
git fetch origin
git reset --hard origin/main
```

---

## Quick Reference Card

| Action | Command |
|--------|---------|
| Clone repo | `git clone https://github.com/bfisher-bah/BAH-Agentic-AI-Capstone.git` |
| Check status | `git status` |
| Pull changes | `git pull origin main` |
| Add all files | `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push origin main` |
| View history | `git log --oneline` |

---

## Project File Locations

After cloning, your key files will be at:

```
~/SageMaker/BAH-Agentic-AI-Capstone/
├── CAPSTONE_PROJECT_PLAN.md          # Implementation plan
├── ALTERNATIVE_PROJECT_IDEAS.md       # Domain alternatives (FYI)
├── SAGEMAKER_SETUP_GUIDE.md          # This file
├── CapstoneMisc/
│   ├── LangChain_LangGraph_Chatbot_Template.py
│   └── BAH Team Presentation Template.pptx
└── GAI-3101-CAP-1-GAI-3101-CAP-1764171407/
    ├── GAI-3101-CAP-LabGuide.pdf
    └── LabFiles/capstone/
        ├── basic-ticket-agent.ipynb   # START HERE
        ├── ticketing-system/          # Node.js backend
        └── support-info/              # RAG knowledge base
```

---

## Team Collaboration Tips

1. **Communicate before pushing** - Let teammates know when you're about to push
2. **Pull before you start** - Always `git pull` before beginning work
3. **Commit often** - Small, frequent commits are easier to manage
4. **Use descriptive messages** - "Add classification logic" not "updates"
5. **Don't commit API keys** - Keep secrets out of the repo

---

*Setup guide created for BAH Agentic AI Capstone Project*