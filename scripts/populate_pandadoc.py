#!/usr/bin/env python3
"""
PandaDoc API integration for Klugonyx quote brief automation.
Takes JSON output from klugonyx-quote-brief skill and creates a populated PandaDoc document.
"""

import os
import re
import json
import requests
from datetime import date
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PandaDocClient:
    def __init__(self):
        self.api_key = os.getenv('PANDADOC_API_KEY')
        if not self.api_key:
            raise ValueError("PANDADOC_API_KEY not found in environment variables")

        self.base_url = "https://api.pandadoc.com/public/v1"
        self.headers = {
            "Authorization": f"API-Key {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_template_id(self, product_type: str) -> str:
        """Get the appropriate PandaDoc template ID based on product type."""
        template_mapping = {
            "hard good": os.getenv("PANDADOC_TEMPLATE_HARDGOODS_API"),
            "hard/soft hybrid": os.getenv("PANDADOC_TEMPLATE_HARDGOODS_API"),
            "soft good": os.getenv("PANDADOC_TEMPLATE_SOFTGOODS_API"),
            "packaging": os.getenv("PANDADOC_TEMPLATE_PACKAGING"),
            "branding": os.getenv("PANDADOC_TEMPLATE_BRANDING"),
            "graphic exploration": os.getenv("PANDADOC_TEMPLATE_BRANDING"),
            "cmf strategy": os.getenv("PANDADOC_TEMPLATE_SOFTGOODS_API"),
            "supply chain": os.getenv("PANDADOC_TEMPLATE_BRANDING")
        }

        template_id = template_mapping.get(product_type.lower())
        if not template_id:
            template_id = os.getenv('PANDADOC_TEMPLATE_HARDGOODS_API')

        if not template_id:
            raise ValueError(f"Template ID not found for product type: {product_type}")

        return template_id

    def _build_tokens(self, skill_output: Dict[str, Any]) -> list:
        """
        Build PandaDoc tokens list from skill output fields and pricing tables.

        Token mapping:
          fields.project_overview    -> Project.Overview
          fields.objectives          -> Project.Objectives
          fields.project_title       -> project_title
          fields.client_name         -> client_name
          fields.clients_name        -> clients_name
          fields.reps_name           -> reps_name
          fields.company             -> company, Client.Company
          fields.title               -> client_title
          fields.email               -> client_email
          pricing_tables[0].sections (ID)  -> ID.Hours, ID.Price
          pricing_tables[0].sections (EFP) -> EFP.Hours, EFP.Price
          pricing_tables[0].sections (PER) -> PER.Hours, PER.Price
        """
        fields = skill_output.get('fields', {})

        tokens = [
            {"name": "Project.Overview",   "value": fields.get('project_overview', '')},
            {"name": "Project.Objectives", "value": fields.get('objectives', '')},
            {"name": "project_title",      "value": fields.get('project_title', '')},
            {"name": "client_name",        "value": fields.get('client_name', '')},
            {"name": "clients_name",       "value": fields.get('clients_name', '')},
            {"name": "reps_name",          "value": fields.get('reps_name', '')},
            {"name": "company",            "value": fields.get('company', '')},
            {"name": "Client.Company",     "value": fields.get('company', '')},
            {"name": "client_title",       "value": fields.get('title', '')},
            {"name": "client_email",       "value": fields.get('email', '')},
        ]

        # Extract phase hours and prices from pricing table sections
        try:
            sections = skill_output['pricing_tables'][0]['sections']
            phase_map = {
                'id':  ('ID.Hours',  'ID.Price'),
                'efp': ('EFP.Hours', 'EFP.Price'),
                'per': ('PER.Hours', 'PER.Price'),
            }
            for section in sections:
                title_lower = section.get('title', '').lower()
                for key, (hours_token, price_token) in phase_map.items():
                    if f'({key})' in title_lower or title_lower.startswith(key):
                        tokens.append({"name": hours_token, "value": section.get('qty', '')})
                        tokens.append({"name": price_token, "value": section.get('subtotal', '')})
                        break
        except (KeyError, IndexError, TypeError):
            pass

        return tokens

    def _build_recipients(self, skill_output: Dict[str, Any]) -> list:
        """Build recipients list with company field for Client.Company auto-population."""
        recipients = skill_output.get('recipients', [])
        enriched = []
        fields = skill_output.get('fields', {})
        company = fields.get('company', '')
        if not company or company.lower() in ('unknown', '', 'none'):
            company = fields.get('client_name', '')
        for r in recipients:
            recipient = dict(r)
            if company and 'company' not in recipient:
                recipient['company'] = company
            # Ensure role matches the template's client role name
            if 'role' not in recipient or recipient['role'].lower() == 'client':
                recipient['role'] = 'Role 2'
            enriched.append(recipient)
        return enriched

    def create_document(self, skill_output: Dict[str, Any]) -> Dict[str, Any]:
        """Create a PandaDoc document from the skill JSON output."""
        try:
            fields = skill_output.get('fields', {})
            product_type = self._extract_product_type(fields)
            template_id = self.get_template_id(product_type)

            document_data = {
                "name": fields.get('project_title', 'Klugonyx Proposal'),
                "template_uuid": template_id,
                "recipients": self._build_recipients(skill_output),
                "tokens": self._build_tokens(skill_output),
                "metadata": {
                    "source": "klugonyx-quote-brief-skill",
                    "product_type": product_type
                }
            }

            response = requests.post(
                f"{self.base_url}/documents",
                headers=self.headers,
                json=document_data,
                timeout=30
            )

            if response.status_code == 201:
                document = response.json()
                return {
                    "success": True,
                    "document_id": document.get('id'),
                    "document_url": document.get('url'),
                    "status": document.get('status'),
                    "name": document.get('name')
                }
            else:
                return {
                    "success": False,
                    "error": f"PandaDoc API error: {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create document: {str(e)}"
            }

    def _extract_product_type(self, fields: Dict[str, Any]) -> str:
        """Extract product type from fields to determine template."""
        project_title = fields.get('project_title', '').lower()

        if 'packaging' in project_title:
            return 'packaging'
        elif 'branding' in project_title:
            return 'branding'
        elif 'supply chain' in project_title:
            return 'supply chain'
        elif 'soft' in project_title:
            return 'soft good'
        elif 'hybrid' in project_title:
            return 'hard/soft hybrid'
        else:
            return 'hard good'

    def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """Get the current status of a PandaDoc document."""
        try:
            response = requests.get(
                f"{self.base_url}/documents/{document_id}",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get document status: {response.status_code}"}

        except Exception as e:
            return {"error": f"Failed to get document status: {str(e)}"}

_PRODUCT_TYPE_TO_SUBFOLDER = {
    'hard good': 'hard-goods',
    'hard/soft hybrid': 'hard-goods',
    'soft good': 'soft-goods',
    'cmf strategy': 'soft-goods',
    'packaging': 'packaging',
    'branding': 'branding',
    'graphic exploration': 'branding',
    'supply chain': 'branding',
}


def _slugify(text: str) -> str:
    """Convert text to a lowercase hyphenated slug."""
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text).strip().lower()
    return re.sub(r'\s+', '-', text)


def _extract_product_type_from_fields(fields: Dict[str, Any]) -> str:
    """Mirror of PandaDocClient._extract_product_type for standalone use."""
    project_title = fields.get('project_title', '').lower()
    if 'packaging' in project_title:
        return 'packaging'
    elif 'branding' in project_title:
        return 'branding'
    elif 'supply chain' in project_title:
        return 'supply chain'
    elif 'soft' in project_title:
        return 'soft good'
    elif 'hybrid' in project_title:
        return 'hard/soft hybrid'
    return 'hard good'


def save_brief_markdown(skill_data: Dict[str, Any], document_url: Optional[str]) -> Optional[str]:
    """
    Save a markdown brief to the appropriate /briefs subfolder.

    Returns the file path if saved successfully, None otherwise.
    """
    try:
        fields = skill_data.get('fields', {})
        recipients = skill_data.get('recipients', [])

        # Determine subfolder from product type
        product_type = _extract_product_type_from_fields(fields)
        subfolder = _PRODUCT_TYPE_TO_SUBFOLDER.get(product_type, 'hard-goods')

        # Client last name — prefer recipients list, fall back to last word of client_name
        client_last_name = ''
        if recipients:
            client_last_name = recipients[0].get('last_name', '')
        if not client_last_name:
            parts = fields.get('client_name', '').strip().split()
            client_last_name = parts[-1] if parts else 'client'

        # Product slug — strip "// ..." suffix from project title
        project_title = fields.get('project_title', 'untitled')
        slug_base = project_title.split('//')[0].strip()
        product_slug = _slugify(slug_base)

        today = date.today().strftime('%Y-%m-%d')
        filename = f"{client_last_name.lower()}-{product_slug}-{today}.md"

        # Resolve briefs directory relative to this script
        repo_root = Path(__file__).resolve().parent.parent
        briefs_dir = repo_root / 'briefs' / subfolder
        briefs_dir.mkdir(parents=True, exist_ok=True)
        filepath = briefs_dir / filename

        # Build phase recommendations table
        phase_lines = []
        try:
            sections = skill_data['pricing_tables'][0]['sections']
            phase_lines.append('| Phase | Price/hr | Hours Estimated | Estimated Phase Price |')
            phase_lines.append('|---|---|---|---|')
            for section in sections:
                title = section.get('title', '')
                price = section.get('price', '—')
                qty = section.get('qty', '—')
                subtotal = section.get('subtotal', '—')
                phase_lines.append(f'| {title} | {price} | {qty} | {subtotal} |')
        except (KeyError, IndexError, TypeError):
            phase_lines.append('_Phase data not available._')

        # Build red flags section
        red_flags = skill_data.get('red_flags', [])
        if red_flags:
            flag_lines = ['| Flag | Severity | Action Required |', '|---|---|---|']
            for flag in red_flags:
                name = flag.get('name', flag.get('flag', ''))
                severity = flag.get('severity', '')
                action = flag.get('recommendation', flag.get('action', ''))
                flag_lines.append(f'| {name} | {severity} | {action} |')
            red_flags_section = '\n'.join(flag_lines)
        else:
            red_flags_section = '_Red flag data not included in JSON output. See full brief analysis in conversation._'

        # Assemble client contact block
        client_name = fields.get('client_name', '')
        email = fields.get('email', '')
        company = fields.get('company', '')
        title = fields.get('title', '')
        reps_name = fields.get('reps_name', '')

        contact_lines = []
        if client_name:
            contact_lines.append(f'**Client:** {client_name}')
        if company:
            contact_lines.append(f'**Company:** {company}')
        if title:
            contact_lines.append(f'**Title:** {title}')
        if email:
            contact_lines.append(f'**Email:** {email}')
        if reps_name:
            contact_lines.append(f'**Rep:** {reps_name}')
        contact_block = '\n'.join(contact_lines)

        pandadoc_line = f'[View in PandaDoc]({document_url})' if document_url else '_PandaDoc document not created._'

        content = f"""# {project_title}

---

## CLIENT

{contact_block}

---

## PRODUCT OVERVIEW

{fields.get('project_overview', '_Not provided._')}

---

## OBJECTIVES

{fields.get('objectives', '_Not provided._')}

---

## DELIVERABLES

{fields.get('deliverables', '_Not provided._')}

---

## PHASE RECOMMENDATIONS

{chr(10).join(phase_lines)}

---

## RED FLAGS

{red_flags_section}

---

## PANDADOC

{pandadoc_line}
"""

        filepath.write_text(content, encoding='utf-8')
        return str(filepath)

    except Exception as e:
        print(f"Warning: Could not save brief markdown: {str(e)}")
        return None


def populate_pandadoc(skill_json_output: str) -> Optional[str]:
    """
    Main function to create a PandaDoc document from skill output.

    Args:
        skill_json_output: JSON string output from klugonyx-quote-brief skill

    Returns:
        PandaDoc document URL if successful, None if failed
    """
    try:
        skill_data = json.loads(skill_json_output)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON input: {str(e)}")
        return None

    document_url = None
    try:
        client = PandaDocClient()
        result = client.create_document(skill_data)

        if result['success']:
            print(f"PandaDoc document created successfully!")
            print(f"Document ID: {result['document_id']}")
            print(f"Document Name: {result['name']}")
            print(f"Status: {result['status']}")
            print(f"URL: {result['document_url']}")
            document_url = result['document_url']
        else:
            print(f"Failed to create PandaDoc document:")
            print(f"Error: {result['error']}")
            if 'details' in result:
                print(f"Details: {result['details']}")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")

    brief_path = save_brief_markdown(skill_data, document_url)
    if brief_path:
        print(f"Brief saved: {brief_path}")

    return document_url

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: py populate_pandadoc.py '<json_output>'")
        print("Example: py populate_pandadoc.py '{\"template_id\": \"...\", \"fields\": {...}}'")
        sys.exit(1)

    json_input = sys.argv[1]
    document_url = populate_pandadoc(json_input)

    if document_url:
        print(f"\nFinal Document URL: {document_url}")
        sys.exit(0)
    else:
        sys.exit(1)
