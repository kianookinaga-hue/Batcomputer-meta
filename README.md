# Drifter Glasses Assistant System

This repository now includes a themed, operations-focused assistant system for Meta Ray-Ban style smart glasses workflows.

## What this adds

- **Mode-based assistant runtime** with tactical responses:
  - stealth
  - recon
  - transit
  - analysis
  - emergency
- **Voice command routing** for:
  - status reports
  - navigation directives
  - scan/analyze actions
  - comms actions
  - objective management
- **Safety guardrails** that block disallowed command intent.
- **LLM system prompt builder** for connecting an external model backend.
- **Console simulation** to run the system locally.
- **Integration** with the existing `DataLogger`.

## Files

- `src/drifter_glasses_assistant/system.py` - assistant logic and command handling
- `src/drifter_glasses_assistant/persona.py` - system prompt builder for model backends
- `src/drifter_glasses_assistant/config.py` - runtime config defaults
- `src/drifter_glasses_assistant/models.py` - core datatypes
- `src/drifter_glasses_assistant/cli.py` - local interactive console demo
- `tests/test_drifter_glasses_assistant.py` - baseline tests

## Quick start

From repo root:

```bash
python -m src.drifter_glasses_assistant.cli
```

Example commands:

- `status`
- `scan sector`
- `navigate to harbor checkpoint`
- `mode stealth`
- `objective watch rooftop access`
- `prompt` (prints current model system prompt)
- `exit`

## Integrating with a model backend

Use `build_system_prompt` and feed it to your LLM provider as system instruction:

```python
from src.drifter_glasses_assistant.config import DrifterAssistantConfig
from src.drifter_glasses_assistant.models import OperationMode
from src.drifter_glasses_assistant.persona import build_system_prompt

config = DrifterAssistantConfig()
prompt = build_system_prompt(config, OperationMode.RECON)
```

Then route model outputs through your voice/HUD pipeline.

## Notes

- This implementation is a **starter system architecture** suitable for simulation and integration.
- Hardware integrations (camera frames, microphones, GPS, on-device inference) should be added via adapters around `DrifterGlassesAssistant`.
