#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Save markdown content from stdin to a target file."
    )
    parser.add_argument("--path", required=True, help="Target markdown file path")
    parser.add_argument("--encoding", default="utf-8", help="File encoding")
    args = parser.parse_args()

    content = sys.stdin.read()
    if not content.strip():
        print(
            json.dumps(
                {"ok": False, "error": "empty_stdin", "message": "stdin is empty"},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    target = Path(args.path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding=args.encoding)

    print(
        json.dumps(
            {
                "ok": True,
                "path": str(target),
                "bytes": len(content.encode(args.encoding)),
                "lines": len(content.splitlines()),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
