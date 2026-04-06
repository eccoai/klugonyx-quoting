# Klugonyx Quoting Workflow

When the user asks to run the quoting skill or process
a transcript, follow these exact steps without stopping
or asking for confirmation between steps:

STEP 1: Read skills/klugonyx-quote-brief/SKILL.md
STEP 2: Read all four ontologies in ontologies/ folder
STEP 3: Process the transcript through all 6 sections
        of the skill workflow completely
STEP 4: Generate the complete PandaDoc JSON output
STEP 5: Immediately run:
        py scripts/populate_pandadoc.py
        with the JSON output
STEP 6: Return the PandaDoc URL to the user

IMPORTANT RULES:
- Do not stop between steps to ask for confirmation
- Do not ask clarifying questions
- Run all steps automatically in sequence
- Do not use Linear
- The user will provide transcript AND hours from the
  product team in their message
- When hours are provided by the user, use those exact
  hours instead of generating estimates from the ontology
- Client company name must always be populated -- if no
  company provided use the client full name as fallback
