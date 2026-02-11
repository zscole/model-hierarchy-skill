# Claude Code / Codex Integration

## Add to CLAUDE.md

Add this section to your project's `CLAUDE.md` or global instructions:

```markdown
## Model Routing

Before executing tasks, classify by complexity:

### ROUTINE (spawn on haiku/cheap)
- File read/write operations
- Status checks and lookups
- Formatting and list operations
- Simple Q&A

### MODERATE (use current model)
- Code generation
- Summarization
- Draft writing
- Data analysis

### COMPLEX (request upgrade if needed)
- Multi-step debugging
- Architecture decisions
- Security reviews
- Tasks where previous attempt failed

When spawning background agents, default to claude-3-haiku for routine work.
When stuck on a problem, suggest upgrading to opus.
```

## Behavioral Examples

### Routine Task

User: "Read config.json and show me the port number"

Agent behavior:
- Classifies as ROUTINE (file read + simple lookup)
- If on expensive model, suggests: "This is routine - I can spawn a background agent for this"
- Executes on cheapest available

### Moderate Task

User: "Write a Python function to validate email addresses"

Agent behavior:
- Classifies as MODERATE (code generation)
- Uses current mid-tier model
- No model change needed

### Complex Task

User: "This test passes locally but fails in CI. Debug it."

Agent behavior:
- Classifies as COMPLEX (debugging)
- If on cheap model, requests: "This needs more reasoning power - switching to opus"
- Proceeds with premium model

## Sub-Agent Spawning

When using background agents:

```
# Good - routine work on cheap model
Spawn background agent (haiku): "Fetch these 20 URLs and extract titles"

# Good - complex work on appropriate model
Spawn background agent (sonnet): "Analyze this codebase and document the architecture"

# Bad - wasting money
Spawn background agent (opus): "Read all .md files in this directory"
```
