# model-hierarchy-skill

Cost-optimize AI agent operations by routing tasks to appropriate models based on complexity.

## The Problem

Most AI agents run everything on expensive models. But 80% of agent tasks are routine: file reads, status checks, formatting, simple Q&A. You're paying $15-75/M tokens for work that $0.14/M tokens handles fine.

## The Solution

A skill that teaches agents to classify tasks and route them to the cheapest model that can handle them:

| Task Type | Model Tier | Cost | Examples |
|-----------|------------|------|----------|
| Routine (80%) | Cheap | $0.14-0.50/M | File ops, status checks, formatting |
| Moderate (15%) | Mid | $1-5/M | Code gen, summaries, drafts |
| Complex (5%) | Premium | $10-75/M | Debugging, architecture, novel problems |

**Result: ~10x cost reduction** with equivalent quality on the tasks that matter.

## Quick Start

### OpenClaw

```bash
# Copy SKILL.md to your skills directory
cp SKILL.md ~/.openclaw/skills/model-hierarchy/SKILL.md

# Restart gateway to pick up the skill
openclaw gateway restart
```

### Claude Code / Codex

Add to your `CLAUDE.md` or project instructions:

```markdown
## Model Routing

Before executing tasks, classify complexity:
- ROUTINE (file ops, lookups, formatting) → Use cheapest model
- MODERATE (code, summaries, analysis) → Use mid-tier model  
- COMPLEX (debugging, architecture, failures) → Use premium model

When spawning sub-agents, default to cheap models unless task requires more.
```

### Other Agent Systems

See [SKILL.md](SKILL.md) for the full classification rules and integration examples.

## Cost Math

Assuming 100K tokens/day:

| Strategy | Monthly Cost |
|----------|--------------|
| Pure Opus | ~$225 |
| Pure Sonnet | ~$45 |
| Hierarchy (80/15/5) | ~$19 |

## Testing

```bash
# Run classification tests
python -m pytest tests/ -v

# Test specific scenarios
python tests/test_classification.py
```

## Files

```
model-hierarchy-skill/
├── SKILL.md          # The skill (install this)
├── README.md         # You're here
├── tests/
│   ├── test_classification.py
│   └── scenarios.json
└── examples/
    ├── openclaw.md
    └── claude-code.md
```

## License

MIT
