# How to Run a Quote Brief

This doc covers everything Tad needs to go from a finished discovery call to a
live PandaDoc proposal -- start to finish.

---

## What This Does Automatically

When you trigger the quoting skill, it will:

1. Read the transcript and extract all client details
2. Classify the product type and complexity
3. Detect red flags and scope risks
4. Apply the hours you provide from the product team
5. Write the full project brief
6. Create and push the PandaDoc document
7. Return you a live URL

You do not need to fill anything in manually. You paste the transcript and
provide hours -- everything else is handled.

---

## Before You Start (One-Time Setup)

These steps only need to be done once. If you are already set up and have run
a quote before, skip to the next section.

**1. Make sure Python is installed**

Open a terminal and run:
```
python --version
```
You should see Python 3.10 or higher. If not, download it from python.org.

**2. Clone the repo (if not already on your machine)**

```
git clone https://github.com/eccoai/klugonyx-quoting.git
cd klugonyx-quoting
```

**3. Install dependencies**

From inside the klugonyx-quoting folder:
```
pip install -r requirements.txt
```

**4. Set up your .env file**

Copy the example file:
```
cp .env.example .env
```

Then open `.env` and fill in your keys. All four are required:

```
ANTHROPIC_API_KEY=your-key-here
PANDADOC_API_KEY=your-key-here
PANDADOC_TEMPLATE_HARDGOODS_API=4qp3Xq5wkJUZGZUq5S9g4U
PANDADOC_TEMPLATE_SOFTGOODS_API=CkzwVrE7xUfkx8y2mxtFdd
PANDADOC_TEMPLATE_PACKAGING=8566d8kVMwPNrzq6JKVDm7
PANDADOC_TEMPLATE_BRANDING=XsWV6aveTxCnFgAivFLBVM
```

Your Anthropic and PandaDoc API keys are in the team 1Password vault.
The template IDs above are already correct -- do not change them.

**5. Make sure the repo is open in VS Code**

Open the klugonyx-quoting folder in VS Code. Claude Code (the extension in the
sidebar) needs to be running with the repo as the working directory.

---

## How to Run a Quote (Every Time)

### What You Need Before Starting

- The finished Read AI transcript from the discovery call
- The hours from the product team for this project:
  - Design (ID) hours -- example: 10-15 hrs
  - Engineering for prototype (EFP) hours -- example: 70-90 hrs
  - Engineering refinement (PER) hours -- example: 30-40 hrs

The product team provides these numbers after reviewing the transcript.
Do not make up hours -- always use the numbers they give you.

---

### Step 1 -- Open Claude Code

In VS Code, open the Claude Code panel from the sidebar. Make sure your
working directory is the klugonyx-quoting folder. You can confirm this by
looking at the folder name shown at the top of the panel.

---

### Step 2 -- Send Your Message

Paste the transcript and hours into Claude Code in a single message.
Format it like this:

```
Run the quoting skill on this transcript.

Hours from the product team:
- Design: 10-15 hrs
- Engineering for prototype: 70-90 hrs
- Engineering refinement: 30-40 hrs

[paste full transcript here]
```

That is all you need to send. Do not add anything else. Claude will
handle the rest automatically without asking you questions.

---

### Step 3 -- Wait for the PandaDoc URL

Claude will run all six steps of the skill workflow and return a URL like:

```
https://app.pandadoc.com/a/#/documents/WWJB8X9JsgD8zpGcyxZdLR
```

The document is created in draft status in PandaDoc. It is not sent to the
client yet.

The brief is also automatically saved to the briefs/ folder in the repo
and pushed to GitHub.

---

### Step 4 -- Review in PandaDoc

Open the URL and review the populated proposal. Check:

- Product overview reads naturally and matches what the client described
- Objectives match the product components discussed on the call
- Hours and prices in the budget table match what the product team gave you
- Client name, rep name, and title are correct
- No missing fields

Make any edits directly in PandaDoc before sending.

---

### Step 5 -- Send to Client

Once reviewed, send the proposal from PandaDoc as you normally would.
Add the client email if it was not captured from the transcript.

---

## Alternative: Run From Terminal Instead of Claude Code

If you want to run the skill without Claude Code -- for example from a
terminal on any machine -- you can use the Python script directly.

From inside the klugonyx-quoting folder:

```
cd scripts
python run_skill.py
```

The script will prompt you to paste the transcript. Paste it and press
Ctrl+Z (Windows) or Ctrl+D (Mac/Linux) when done. It calls the Claude API
automatically, extracts the JSON, and pushes to PandaDoc.

Note: This method does not accept hours as a separate input -- you would
need to include the hours in your transcript paste or modify the prompt.
The Claude Code method is recommended for day-to-day use.

---

## Red Flags and What They Mean

The skill automatically detects scope risks and includes them in the brief
analysis. Common ones for hard goods:

| Flag | What It Means |
|---|---|
| Electronics/Bluetooth (Critical) | Electrical engineering is excluded. Klugonyx handles housing and mounting only. |
| Novel Multi-System Mechanism (High) | The mechanism has not been validated. EFP hours may need adjustment after ID phase. |
| IP/Patent Risk (High) | Client has not done a patent search. Refer them to an IP attorney before prototype or public launch. |
| Multi-SKU Scope (Medium) | Only the hero SKU is in scope. Future variants are a separate engagement. |
| Future Ecosystem (Medium) | Scalability architecture is in scope for the hero SKU only. |

These do not block the proposal -- they are notes for your review and for
the team when scoping the engagement.

---

## If Something Goes Wrong

**GitHub push fails with "fetch first" error**

The remote has changes your local copy does not have. Run this from the
klugonyx-quoting folder and then re-run your quote:

```
git pull --rebase
git push
```

**PandaDoc returns an error**

Check that your PANDADOC_API_KEY in the .env file is correct and active.
Log into PandaDoc and confirm your API access is enabled under Settings.

**Claude Code does not find the skill files**

Make sure your working directory in VS Code is the klugonyx-quoting folder,
not a parent or child folder. The CLAUDE.md file must be at the root.

**Missing hours from product team**

Do not run the quote without hours. Send the transcript to the product team
first and wait for their hour estimates before triggering the skill.

---

## Files Produced After Each Run

| File | Location | Purpose |
|---|---|---|
| Brief markdown | briefs/hard-goods/ (or soft-goods/, etc.) | Permanent record of the quote, pushed to GitHub |
| PandaDoc JSON | output/ | The raw API payload used to create the document |
| PandaDoc document | app.pandadoc.com | Live draft proposal ready for review |
