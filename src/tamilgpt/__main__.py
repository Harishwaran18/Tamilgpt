"""Command line entry point: ``python -m tamilgpt``."""

from __future__ import annotations

import argparse
import asyncio
import sys

from tamilgpt import __version__
from tamilgpt.core.config import get_settings
from tamilgpt.knowledge.validate import main as validate_main
from tamilgpt.services.chat import answer


def _serve(args: argparse.Namespace) -> int:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "tamilgpt.api.main:app",
        host=args.host or settings.host,
        port=args.port or settings.port,
        reload=args.reload,
        log_level=settings.log_level.lower(),
    )
    return 0


async def _chat_once(message: str, language: str) -> int:
    result = await answer(message, language=language)
    print(result.reply)
    return 0


def _repl(language: str) -> int:
    print(f"TamilGPT {__version__} — type 'exit' to quit.")
    while True:
        try:
            message = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if message.lower() in {"exit", "quit"}:
            return 0
        if not message:
            continue
        print(asyncio.run(answer(message, language=language)).reply)
        print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tamilgpt", description="TamilGPT 2.0")
    parser.add_argument("--version", action="version", version=f"TamilGPT {__version__}")
    sub = parser.add_subparsers(dest="command")

    serve = sub.add_parser("serve", help="Run the API and web UI")
    serve.add_argument("--host")
    serve.add_argument("--port", type=int)
    serve.add_argument("--reload", action="store_true")
    serve.set_defaults(func=_serve)

    chat = sub.add_parser("chat", help="Ask one question or open a REPL")
    chat.add_argument("-m", "--message")
    chat.add_argument("-l", "--language", choices=["auto", "ta", "en"], default="auto")

    sub.add_parser("validate", help="Validate the knowledge base")

    args = parser.parse_args(argv)
    if args.command is None:
        return _repl("auto")
    if args.command == "validate":
        return validate_main()
    if args.command == "chat":
        if args.message:
            return asyncio.run(_chat_once(args.message, args.language))
        return _repl(args.language)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
