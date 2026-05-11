#!/usr/bin/env python3
"""
Validate commit title.

Rules:
- Max 72 characters (git recommendation)
- No Jira number required (unlike PR titles)
"""

import sys

MAX_TITLE_LENGTH = 72


def validate_commit_title(title: str) -> tuple[bool, list[str]]:
    """
    Validate a commit title.

    Args:
        title: The commit title to validate

    Returns:
        Tuple of (is_valid, list of error/warning messages)
    """
    errors = []
    warnings = []

    if len(title) > MAX_TITLE_LENGTH:
        over_by = len(title) - MAX_TITLE_LENGTH
        errors.append(
            f"Tittel er {len(title)} tegn, maks er {MAX_TITLE_LENGTH} (over med {over_by}).\n"
            f"  Nåværende: {title}"
        )
    elif len(title) > MAX_TITLE_LENGTH - 10:
        warnings.append(
            f"Tittel er {len(title)} tegn, nær grensen på {MAX_TITLE_LENGTH}."
        )

    messages = []
    if errors:
        messages.extend([f"❌ {e}" for e in errors])
    if warnings:
        messages.extend([f"⚠️  {w}" for w in warnings])
    if not errors and not warnings:
        messages.append(f"✅ Tittel OK ({len(title)} tegn)")

    return len(errors) == 0, messages


def main():
    """CLI interface for validation."""
    if len(sys.argv) < 2:
        print("Usage: python validate_commit_title.py <title>")
        print()
        print("Examples:")
        print('  python validate_commit_title.py "Add user validation"')
        print('  python validate_commit_title.py "1234 Add user validation"')
        sys.exit(1)

    title = sys.argv[1]

    is_valid, messages = validate_commit_title(title)

    for msg in messages:
        print(msg)

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
