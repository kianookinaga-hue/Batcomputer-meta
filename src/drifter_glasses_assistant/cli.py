from __future__ import annotations

import json
from dataclasses import asdict
from typing import Optional

from src.data_logging.logger import DataLogger

from .config import DrifterAssistantConfig
from .persona import build_system_prompt
from .system import DrifterGlassesAssistant


class _LoggerConfig:
    """Local config adapter for existing DataLogger."""

    DATA_RETENTION_DAYS = 30
    BACKUP_ENABLED = True
    BACKUP_INTERVAL = 10


def _build_assistant(with_logger: bool = True) -> DrifterGlassesAssistant:
    config = DrifterAssistantConfig()
    data_logger: Optional[DataLogger] = DataLogger(_LoggerConfig()) if with_logger else None
    assistant = DrifterGlassesAssistant(config=config, data_logger=data_logger)
    assistant.start_operation()
    return assistant


def run_console(with_logger: bool = True) -> None:
    assistant = _build_assistant(with_logger=with_logger)
    print("== DRIFTER GLASSES CONSOLE ==")
    print("Type commands, 'prompt', 'objective <text>', 'mode <name>', or 'exit'.")

    while True:
        command = input("> ").strip()
        if not command:
            continue
        lower = command.lower()

        if lower in {"exit", "quit", "shutdown"}:
            summary = assistant.stop_operation()
            print(json.dumps(summary, indent=2))
            break

        if lower == "prompt":
            print(build_system_prompt(assistant.config, assistant.mode))
            continue

        if lower.startswith("objective "):
            response = assistant.set_objective(command.split(" ", 1)[1])
        else:
            response = assistant.handle_voice_command(command)

        print(json.dumps(asdict(response), indent=2))


if __name__ == "__main__":
    run_console()
