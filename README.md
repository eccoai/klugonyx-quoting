# Klugonyx Quoting Workflow

Klugonyx quoting workflow — transcript to proposal brief automation.

Read AI transcript → Claude skill → structured project brief → PandaDoc template population.

## Structure

- `/ontologies` - Domain ontologies and data models
- `/skills/klugonyx-quote-brief` - Claude skill for quote brief generation
- `/docs` - Documentation and guides
- `/config` - Configuration files
- `.env.example` - Environment variable template

## Setup

1. Copy `.env.example` to `.env` and fill in your API keys
2. Configure PandaDoc template IDs for light, classic, and premium tiers
3. Set up Read AI integration for transcript processing

## Workflow

1. Read AI captures and transcribes client meetings
2. Claude skill processes transcript into structured project brief
3. PandaDoc API populates appropriate template based on project tier
4. Generated proposal ready for client review