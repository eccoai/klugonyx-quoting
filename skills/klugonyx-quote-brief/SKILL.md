---
name: klugonyx-quote-brief
description: Processes a Klugonyx client discovery call transcript and generates a structured project brief that populates the correct PandaDoc proposal template. Use when Tad or Austin has completed a discovery call and needs to generate a proposal brief. Triggers on any request to process a transcript, generate a brief, create a proposal, or quote a new project.
argument-hint: "[transcript text or Read AI meeting ID]"
user-invocable: true
allowed-tools: "Read,Write,Bash"
---

# Klugonyx Quote Brief Skill

Processes a discovery call transcript and generates a structured project brief that maps directly to the correct PandaDoc proposal template.

## Dtree Classification

`SKILL_STANDALONE` — Low-medium autonomy (structured extraction workflow), no orchestration, single concern.

Path: HG-01 FAIL (3.5) → HG-04 PASS (5.5) → `SKILL_STANDALONE`

## What You Do

When invoked, follow these sections in order. Each section has a quality gate that must pass before proceeding.

---

### Section 1: Transcript Ingestion

Accept input as either:
- Raw transcript text pasted by the user
- Read AI meeting ID (format: fetch via Read AI MCP if connected)

Extract and confirm:
- Client full name
- Client company name (if any)
- Client location
- Client email (if mentioned)
- Sales rep who took the call (Tad Thornton or Austin Moss)
- Date of call
- Product name or working title

**Quality Gate G1 — Transcript Received:**
- [ ] Client name identified
- [ ] Product description captured
- [ ] Sales rep confirmed

---

### Section 2: Product Classification

Using the product-complexity-ontology, classify the product:

**PRODUCT TYPE** — identify ONE primary type:
- Hard good
- Soft good  
- Hard/Soft Hybrid
- Packaging
- Branding
- Graphic Exploration
- CMF Strategy

**COMPLEXITY SIGNALS** — scan transcript for ALL that apply:
- Universal fit required
- New mechanism to invent
- Novel multi-system mechanism (scope unknown)
- Modular/reconfigurable system
- Convertible/transforming product
- Hard good with significant soft component
- Electronics/Bluetooth component
- Electronics housing with complex internal architecture
- Miniaturized sealed enclosure
- Safety-critical (baby, medical, structural, load-bearing)
- Medical/healthcare-adjacent
- Food-safe/FDA-compliant materials required
- Children's toy (head entrapment, part separation standards)
- ASTM or industry standard compliance required
- Iterative rework/v2 of existing product
- Multi-SKU scope
- OEM base product customization
- Strong client reference or design doc provided
- Client has POC CAD or renders
- Future product ecosystem planned
- Standalone illustration only
- Standalone packaging/branding only

**COMPLEXITY TIER** — assign ONE:
- Low
- Medium
- Medium-High
- High
- Extreme/Novel

**TEMPLATE SELECTION** — based on product type:
- Hard good → PRODUCT DEVELOPMENT_HardGoods_101
- Soft good → PRODUCT DEVELOPMENT_SoftGoods_101
- Hard/Soft Hybrid → PRODUCT DEVELOPMENT_HardGoods_101 (primary)
- Packaging → Packaging_101
- Branding → Branding_101
- Supply chain only → Supply Chain Development Retainer Agreement_101

**Quality Gate G2 — Classification Complete:**
- [ ] Product type confirmed
- [ ] Complexity signals listed
- [ ] Template selected

---

### Section 3: Red Flag Detection

Using the proposal-red-flag-ontology, scan the transcript for ALL red flags. For each flag triggered output:
- Flag name
- Severity (low/medium/high/critical)
- Recommendation

**ALWAYS check for:**
- Universal fit → add hours, flag explicitly
- Electronics/Bluetooth → exclude electrical engineering, client must finalize hardware first
- Novel multi-system mechanism → use ID-gates-EFP pattern
- Safety-critical → add regulatory disclaimer
- Medical/healthcare-adjacent → FDA/CE/ISO is client responsibility
- Food-safe materials → call out explicitly
- Children's toy → head entrapment, part separation standards
- IP/patent risk → flag early, cannot reference competing products
- Hard/soft hybrid → split EFP line items required
- Multi-SKU → scale ID hours dramatically
- Future product ecosystem → scope into ID hours explicitly
- Iterative rework → use PER-only pattern
- Instruction manuals → scope by step count explicitly
- Retail packaging → higher hours than DTC

**Quality Gate G3 — Red Flags Documented:**
- [ ] All red flags identified and listed
- [ ] Severity assigned to each
- [ ] No flags missed from ontology

---

### Section 4: Phase Recommendations

Using the quoting-benchmark-ontology, recommend phases and hour ranges.

For each recommended phase output:
- Phase name
- Hour range (min-max)
- Hourly rate
- Estimated cost range (min-max)
- Rationale (1 sentence)

**RATE RULES** — apply strictly:
- ID/Design/Branding/Soft Goods/CMF/Graphic Exploration: $140/hr
- EFP mechanical hard good: $195/hr
- EFP documentation/CMF/soft goods only: $140/hr
- EFP soft component in hybrid: $140/hr
- PER mechanical: $195/hr
- PER predominantly documentation/tech pack: $140/hr
- Supply Chain Retainer: $3,500/mo standard
- Overage: $195/hr

**PHASE PATTERNS** — select the right one:
- **Standard:** ID → EFP → PER → Retainer
- **ID-gates-EFP:** Quote ID only, EFP/PER TBD pending design validation. Use when mechanism feasibility is unknown.
- **PER-only:** Use for iterative reworks of existing CAD.
- **No-ID:** Skip ID when client has detailed design doc, POC CAD, or Klugonyx completed the design already.

ALWAYS include Supply Chain Retainer as placeholder line item.

ALWAYS include High-level Production Costs at $0 if EFP is included.

**Quality Gate G4 — Phases Scoped:**
- [ ] All phases listed with hours and rates
- [ ] Rate rules applied correctly
- [ ] Phase pattern selected with rationale
- [ ] Total range calculated

---

### Section 5: Brief Generation

Generate the complete project brief output in this exact structure for PandaDoc population:

**PROJECT TITLE:** [Product Name] // Product Development

**PREPARED FOR:** [Client Name]
**PREPARED BY:** [Tad Thornton or Austin Moss]
**DATE:** [Call date]

**PRODUCT OVERVIEW:**
[Single paragraph. Describe what the product is, who it is for, what makes it unique, and how it works. Written in client-facing proposal language. Match Austin's Mazi Bibs style exactly.]

**OBJECTIVES:**
[Bullet points grouped by component or system. Each bullet is one clear action-oriented sentence using verbs: Design, Explore, Engineer, Ensure, Validate, Confirm, Evaluate, Develop. No paragraphs. No numbering. Product-specific only.]

**PROJECT SCOPE:**
[Standard Klugonyx scope bullets — create concept designs, develop initial assets for prototype, facilitate production, make engineering adjustments, create documentation, acquire high-level pricing.]

**DELIVERABLES:**
[Deliverables specific to this project based on phases recommended.]

**CONTRACT BUDGET TABLE:**
[One row per phase with: Phase name, Price/hr, Hours estimated, Estimated phase price. Include Supply Chain Retainer placeholder.]

**NEXT STEP:**
[2-3 sentences personalized to the client. Reference their product and the opportunity. Match tone of completed Bully Stick Holder doc.]

**STANDARD EXCLUSIONS:**
This proposal does not include prototype costs, testing materials, reference products, tooling costs, production samples, production costs, electrical engineering, and renderings.

**CLIENT SIGNATURE FIELDS:**
COMPANY: [Client company or blank]
CLIENTS NAME: [Client full name]
TITLE: [Client title if known]
EMAIL: [Client email if mentioned]

**Quality Gate G5 — Brief Complete:**
- [ ] All sections populated
- [ ] Product overview written in proposal language
- [ ] Objectives grouped by component with action verbs
- [ ] Budget table complete with correct rates
- [ ] No generic filler — everything product-specific

---

### Section 6: PandaDoc Mapping Output

Output a clean JSON object ready for PandaDoc API:

```json
{
  "template_id": "[selected template ID from .env]",
  "recipients": [
    {
      "email": "[client email]",
      "first_name": "[client first name]",
      "last_name": "[client last name]",
      "role": "Client"
    }
  ],
  "fields": {
    "client_name": "[client full name]",
    "reps_name": "[Tad Thornton or Austin Moss]",
    "project_title": "[product name] // Product Development",
    "project_overview": "[product overview paragraph]",
    "objectives": "[formatted objectives]",
    "deliverables": "[deliverables list]",
    "company": "[client company]",
    "clients_name": "[client name]",
    "title": "[client title]",
    "email": "[client email]"
  },
  "pricing_tables": [
    {
      "name": "Product Dev Scope",
      "sections": [
        {
          "title": "[phase name]",
          "price": "[hourly rate]",
          "qty": "[hour range]",
          "subtotal": "[estimated phase price]"
        }
      ]
    }
  ]
}
```

**Quality Gate G6 — JSON Ready:**
- [ ] Template ID mapped correctly to product type
- [ ] All fields populated
- [ ] Pricing table complete
- [ ] Ready for PandaDoc API call

---

## Error Handling

If transcript is unclear on product type → ask one clarifying question before proceeding.

If client email not found in transcript → note as missing, continue with blank field.

If mechanism feasibility is genuinely unknown → automatically select ID-gates-EFP pattern, flag in output.

If non-standard rate detected in transcript discussion → flag for team review, do not apply without confirmation.

## Ontology References

| Ontology | Role | Namespace |
|----------|------|-----------|
| product-complexity-ontology v1.0.0 | Product classification and complexity assessment | `complexity:` |
| quoting-benchmark-ontology v1.0.0 | Phase recommendations and rate rules | `benchmark:` |
| project-brief-ontology v1.0.0 | Brief structure and template mapping | `brief:` |
| proposal-red-flag-ontology v1.0.0 | Risk detection and exclusions | `redflag:` |

## Join Patterns

| Pattern | Description |
|---------|-------------|
| JP-KLG-001 | ProductType.complexitySignals → determines ComplexityTier → influences hour estimates |
| JP-KLG-002 | ComplexitySignal.redFlag → triggers RedFlag.recommendation → modifies phase pattern |
| JP-KLG-003 | ProjectBrief.templateDecision → maps to PandaDoc template ID → populates correct fields |