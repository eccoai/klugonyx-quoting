#!/usr/bin/env python3
"""
PandaDoc API integration for Klugonyx quote brief automation.
Takes JSON output from klugonyx-quote-brief skill and creates a populated PandaDoc document.
"""

import os
import json
import requests
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
            "soft good": os.getenv("PANDADOC_TEMPLATE_SOFTGOODS"),
            "packaging": os.getenv("PANDADOC_TEMPLATE_PACKAGING"),
            "branding": os.getenv("PANDADOC_TEMPLATE_BRANDING"),
            "graphic exploration": os.getenv("PANDADOC_TEMPLATE_BRANDING"),
            "cmf strategy": os.getenv("PANDADOC_TEMPLATE_SOFTGOODS"),
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
        client = PandaDocClient()
        result = client.create_document(skill_data)

        if result['success']:
            print(f"PandaDoc document created successfully!")
            print(f"Document ID: {result['document_id']}")
            print(f"Document Name: {result['name']}")
            print(f"Status: {result['status']}")
            print(f"URL: {result['document_url']}")
            return result['document_url']
        else:
            print(f"Failed to create PandaDoc document:")
            print(f"Error: {result['error']}")
            if 'details' in result:
                print(f"Details: {result['details']}")
            return None

    except json.JSONDecodeError as e:
        print(f"Invalid JSON input: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python populate_pandadoc.py '<json_output>'")
        print("Example: python populate_pandadoc.py '{\"template_id\": \"...\", \"fields\": {...}}'")
        sys.exit(1)

    json_input = sys.argv[1]
    document_url = populate_pandadoc(json_input)

    if document_url:
        print(f"\nFinal Document URL: {document_url}")
        sys.exit(0)
    else:
        sys.exit(1)
