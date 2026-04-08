# Honolulu Drifter Glasses Assistant System

This repository now includes a Honolulu-tailored, operations-focused assistant system for Meta Ray-Ban style smart glasses workflows.

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
- **Honolulu context defaults** including local waypoint aliases and ETA profiles.
- **Island profile packs** with live switching:
  - Waikiki Nightlife
  - Windward Daytime
  - North Shore Weather Watch

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
python3 -m src.drifter_glasses_assistant.cli
```

Example commands:

- `status`
- `scan waikiki sector`
- `navigate to ala moana`
- `navigate to hnl`
- `profiles`
- `profile windward daytime`
- `profile north shore weather watch`
- `mode stealth`
- `objective monitor Waikiki Beach corridor`
- `prompt` (prints current model system prompt)
- `exit`

## Honolulu defaults

`DrifterAssistantConfig` is preconfigured with:
- city: `Honolulu, Hawaii`
- operator: `Drifter Oahu`
- default objective focused on Honolulu corridor safety
- waypoint normalization for aliases like:
  - `waikiki`
  - `ala moana`
  - `kakaako`
  - `downtown`
  - `chinatown`
  - `harbor` / `honolulu harbor`
  - `airport` / `hnl`
  - `diamond head`
  - `manoa`

This means commands like `navigate to harbor checkpoint` will normalize to `Honolulu Harbor` and return a local ETA.

## Island profile packs

The assistant now supports profile packs that tune operations behavior:

- `waikiki-nightlife`
  - crowd-heavy evening assumptions
  - higher congestion ETA multiplier
  - slight threat bias increase
- `windward-daytime`
  - daytime neighborhood and school-zone focus
  - mild ETA increase
  - slight threat bias reduction
- `north-shore-weather-watch`
  - weather and visibility hazard focus
  - highest ETA multiplier
  - elevated threat bias

Runtime commands:
- `profiles` (list available profile packs)
- `profile <name>` (switch profile, e.g. `profile windward daytime`)
- `status` now reports active profile

Profile effects:
- **Scan output** includes profile-specific focus areas
- **Navigation ETA** applies profile multiplier to local baseline ETAs
- **Threat assessment** uses profile bias

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
