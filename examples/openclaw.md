# OpenClaw Integration

## Installation

Copy the skill to your OpenClaw skills directory:

```bash
cp SKILL.md ~/.openclaw/skills/model-hierarchy/SKILL.md
openclaw gateway restart
```

## Configuration

Set your default model to mid-tier in `config.yml`:

```yaml
model: anthropic/claude-sonnet-4
```

## Usage

### Switching Models in Session

```
# Upgrade to premium for complex task
/model opus

# Downgrade to cheap for routine work
/model deepseek
```

### Spawning Sub-Agents

When spawning sub-agents for bulk work, specify the model:

```python
sessions_spawn(
    task="Fetch and parse these 50 URLs",
    model="deepseek"  # Cheap model for routine work
)
```

### Heartbeat Configuration

Configure heartbeats to run on cheap models:

```yaml
# In your agent config
heartbeat:
  model: deepseek-v3
  interval: 30m
```

## Expected Behavior

After installing the skill, your agent should:

1. **Suggest downgrades** when doing routine work on expensive models
2. **Request upgrades** when stuck on complex problems
3. **Default sub-agents to cheap models** unless task requires more

## Cost Tracking

Use `/status` to monitor token usage and costs per session.
