# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StrainHub is a multi-agent AI platform built on LangGraph for the biotech/pharmaceutical industry, supporting 5 business domains: R&D, Quality Control, Customer Support, Equipment Maintenance, and Knowledge Management.

## Architecture

```
User Input → Intent Router → Specialist Agents (LangGraph StateGraph)
                                  ↓
                    ┌─────────────┼─────────────┐
                    R&D Agent    QC Agent   Support/Maint/Knowledge
                    (10 nodes)               (incomplete)
```

- **Orchestrator** (`src/workflows/orchestrator.py`): Routes requests to specialist agents
- **Intent Router** (`src/agents/intent_router.py`): LLM-based intent classification + keyword fallback
- **R&D Agent** (`src/agents/rnd_agent.py`): 10-node workflow for literature search, data analysis, formulation
- **BaseAgent** (`src/agents/base.py`): Abstract base class defining the agent interface

## Common Commands

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests -v
pytest tests/test_agents/test_rnd_agent.py -v

# Start development server
uvicorn src.main:app --reload --port 8000

# Docker Compose (full stack)
docker-compose up -d
```

## Key Patterns

- Agents inherit from `BaseAgent` and implement `define_nodes()` and `define_edges()`
- State classes extend `TypedDict` (e.g., `RNDState extends BaseState`)
- Tools use `@tool` decorator from LangChain
- Configuration via `Settings` class (Pydantic BaseSettings) loaded from `.env`
- All agent outputs must include citations (`citation_required=True`)

## State Schemas

| Agent | State Schema | Status |
|-------|--------------|--------|
| Router | `RouterState` | Done |
| R&D | `RNDState` | Done |
| QC | `QCState` | Incomplete |
| Support | `SupportState` | Incomplete |
| Maintenance | `MaintState` | Incomplete |
| Knowledge | `KnowledgeState` | Incomplete |

## Environment Variables

Required in `backend/.env`:
- `OPENAI_API_KEY` - OpenAI API key
- `POSTGRES_URL` - PostgreSQL connection string
- `MILVUS_URL` - Milvus vector database address
- `REDIS_URL` - Redis cache address