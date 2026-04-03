#!/usr/bin/env python3
"""
Klugonyx quote brief skill runner.
Accepts transcript input, calls Claude API with SKILL.md as system prompt,
processes the output, and creates a PandaDoc document.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from anthropic import Anthropic
from populate_pandadoc import populate_pandadoc

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

class KlugunyxSkillRunner:
    def __init__(self):
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.anthropic_api_key)
        self.skill_content = self._load_skill_content()

    def _load_skill_content(self) -> str:
        """Load the SKILL.md content to use as system prompt."""
        skill_path = Path(__file__).parent.parent / "skills" / "klugonyx-quote-brief" / "SKILL.md"

        if not skill_path.exists():
            raise FileNotFoundError(f"SKILL.md not found at: {skill_path}")

        with open(skill_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_transcript_input(self) -> str:
        """Get transcript input from user (paste or file path)."""
        print("Klugonyx Quote Brief Generator")
        print("=" * 40)
        print()
        print("Enter transcript input:")
        print("1. Paste transcript text directly, then press Ctrl+D (or Ctrl+Z on Windows)")
        print("2. Or provide file path starting with 'file:'")
        print()

        # Read input
        input_lines = []
        try:
            while True:
                line = input()
                input_lines.append(line)
        except EOFError:
            pass

        transcript_input = '\n'.join(input_lines).strip()

        # Check if it's a file path
        if transcript_input.startswith('file:'):
            file_path = transcript_input[5:].strip()
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                raise ValueError(f"File not found: {file_path}")
            except Exception as e:
                raise ValueError(f"Error reading file {file_path}: {str(e)}")

        return transcript_input

    def call_claude_api(self, transcript: str) -> Dict[str, Any]:
        """Call Claude API with SKILL.md as system prompt and transcript as user message."""
        try:
            print("Calling Claude API to process transcript...")

            # Prepare system prompt
            system_prompt = f"""You are the Klugonyx Quote Brief Skill. Follow the exact workflow defined in this SKILL.md:

{self.skill_content}

Process the provided transcript through all 6 sections with quality gates. Output the final JSON from Section 6 at the end of your response."""

            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please process this discovery call transcript:\n\n{transcript}"
                    }
                ]
            )

            # Extract response content
            response_text = response.content[0].text

            print("[OK] Claude API response received")
            print()

            # Extract JSON from response
            json_output = self._extract_json_from_response(response_text)

            if json_output:
                print("[OK] JSON output extracted successfully")
                return {"success": True, "response": response_text, "json": json_output}
            else:
                print("[ERROR] No valid JSON found in response")
                return {"success": False, "error": "No JSON output found", "response": response_text}

        except Exception as e:
            return {"success": False, "error": f"Claude API error: {str(e)}"}

    def _extract_json_from_response(self, response_text: str) -> Optional[str]:
        """Extract JSON from Claude's response text."""
        # Look for JSON blocks
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, response_text, re.DOTALL)

        if matches:
            return matches[-1]  # Return the last JSON block

        # Look for JSON objects without markdown blocks
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)

        # Try to find the most complete JSON (likely the PandaDoc payload)
        for match in reversed(matches):
            try:
                json.loads(match)
                if 'template_id' in match or 'fields' in match:
                    return match
            except json.JSONDecodeError:
                continue

        return None

    def run_complete_workflow(self) -> Optional[str]:
        """Run the complete workflow: transcript → Claude → PandaDoc."""
        try:
            # Get transcript input
            transcript = self.get_transcript_input()

            if not transcript.strip():
                print("[ERROR] No transcript provided")
                return None

            print(f"[BRIEF] Transcript received ({len(transcript)} characters)")
            print()

            # Call Claude API
            claude_result = self.call_claude_api(transcript)

            if not claude_result['success']:
                print(f"[ERROR] Claude API failed: {claude_result['error']}")
                if 'response' in claude_result:
                    print("Response received:")
                    print(claude_result['response'][:500] + "..." if len(claude_result['response']) > 500 else claude_result['response'])
                return None

            # Show Claude's full response for review
            print("Claude's Analysis:")
            print("-" * 40)
            print(claude_result['response'])
            print("-" * 40)
            print()

            # Call PandaDoc API
            print("Creating PandaDoc document...")
            document_url = populate_pandadoc(claude_result['json'])

            return document_url

        except KeyboardInterrupt:
            print("\n\nProcess interrupted by user")
            return None
        except Exception as e:
            print(f"[ERROR] Workflow error: {str(e)}")
            return None

def main():
    """Main entry point."""
    try:
        runner = KlugunyxSkillRunner()
        document_url = runner.run_complete_workflow()

        if document_url:
            print()
            print("[SUCCESS] Klugonyx quote brief automation complete!")
            print(f"[LINK] PandaDoc Document URL: {document_url}")
            print()
            print("Next steps:")
            print("1. Review the generated proposal in PandaDoc")
            print("2. Make any necessary adjustments")
            print("3. Send to client for signature")
        else:
            print()
            print("[ERROR] Workflow failed. Check the errors above.")
            sys.exit(1)

    except ValueError as e:
        print(f"[ERROR] Configuration error: {str(e)}")
        print("Make sure your .env file contains:")
        print("- ANTHROPIC_API_KEY")
        print("- PANDADOC_API_KEY")
        print("- PANDADOC_TEMPLATE_LIGHT")
        print("- PANDADOC_TEMPLATE_CLASSIC")
        print("- PANDADOC_TEMPLATE_PREMIUM")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()