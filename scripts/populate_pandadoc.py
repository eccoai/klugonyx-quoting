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
            "hard good": os.getenv('PANDADOC_TEMPLATE_CLASSIC'),
            "soft good": os.getenv('PANDADOC_TEMPLATE_CLASSIC'),
            "hard/soft hybrid": os.getenv('PANDADOC_TEMPLATE_CLASSIC'),
            "packaging": os.getenv('PANDADOC_TEMPLATE_LIGHT'),
            "branding": os.getenv('PANDADOC_TEMPLATE_LIGHT'),
            "graphic exploration": os.getenv('PANDADOC_TEMPLATE_LIGHT'),
            "cmf strategy": os.getenv('PANDADOC_TEMPLATE_LIGHT'),
            "supply chain": os.getenv('PANDADOC_TEMPLATE_PREMIUM')
        }

        template_id = template_mapping.get(product_type.lower())
        if not template_id:
            # Default to classic template
            template_id = os.getenv('PANDADOC_TEMPLATE_CLASSIC')

        if not template_id:
            raise ValueError(f"Template ID not found for product type: {product_type}")

        return template_id

    def create_document(self, skill_output: Dict[str, Any]) -> Dict[str, Any]:
        """Create a PandaDoc document from the skill JSON output."""
        try:
            # Extract product type to determine template
            fields = skill_output.get('fields', {})
            product_type = self._extract_product_type(fields)
            template_id = self.get_template_id(product_type)

            # Prepare document payload
            document_data = {
                "name": f"{fields.get('project_title', 'Klugonyx Proposal')}",
                "template_uuid": template_id,
                "recipients": skill_output.get('recipients', []),
                "fields": fields,
                "metadata": {
                    "source": "klugonyx-quote-brief-skill",
                    "product_type": product_type
                }
            }

            # Add pricing tables if present
            if 'pricing_tables' in skill_output:
                document_data['pricing_tables'] = skill_output['pricing_tables']

            # Create document via API
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

        # Look for product type indicators in the title or other fields
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
            return 'hard good'  # Default to hard good

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
        # Parse JSON input
        skill_data = json.loads(skill_json_output)

        # Create PandaDoc client
        client = PandaDocClient()

        # Create document
        result = client.create_document(skill_data)

        if result['success']:
            print(f"✅ PandaDoc document created successfully!")
            print(f"Document ID: {result['document_id']}")
            print(f"Document Name: {result['name']}")
            print(f"Status: {result['status']}")
            print(f"URL: {result['document_url']}")
            return result['document_url']
        else:
            print(f"❌ Failed to create PandaDoc document:")
            print(f"Error: {result['error']}")
            if 'details' in result:
                print(f"Details: {result['details']}")
            return None

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON input: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
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
        print(f"\n🔗 Final Document URL: {document_url}")
        sys.exit(0)
    else:
        sys.exit(1)