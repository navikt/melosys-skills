#!/usr/bin/env python3
"""
Validate PR title for squash merge commits.

Rules:
- Must contain a Jira number (e.g., 1234) or a reason code (TEK, DOK, VAKT, PRODFIX)
- TOGGLE and G4P never stand alone and come after the Jira number or reason code
- Dependency codes (DAPI, DWEB, DB, ...) may be added, before or after
- NOJIRA is no longer allowed: a missing Jira needs a stated reason
- Max 72 characters total (git recommendation)
"""

# Keeps `int | None` unevaluated, so the script runs on macOS /usr/bin/python3 (3.9).
from __future__ import annotations

import re
import sys

MAX_TITLE_LENGTH = 72
# Anchor codes say where the work comes from; a title needs one.
# - \d+ : Jira number (e.g., 1234, 7553)
# - REASON_CODES : why there is no Jira ticket. Add new reasons here.
# Other codes only qualify an anchor:
# - FLAG_CODES : TOGGLE (feature toggle), G4P (good for prod) — after the anchor,
#   so a number that starts the description ("G4P 2 nye felt") is not read as Jira
# - D[A-Z]+ : depends on another change (DAPI = melosys-api, DWEB, DB, DDOKGEN)
# NOJIRA is parsed only so it gets a targeted error: it gives no reason.
REASON_CODES = ('TEK', 'DOK', 'VAKT', 'PRODFIX')
FLAG_CODES = ('TOGGLE', 'G4P')
ANCHOR_PATTERN = rf"\d+|{'|'.join(REASON_CODES)}"
CODE_PATTERN = rf"(\d+|D[A-Z]+|NOJIRA|{'|'.join(REASON_CODES + FLAG_CODES)})"
# Only the leading run of codes is parsed; the rest is free description.
PREFIX_PATTERN = rf'^((?:{CODE_PATTERN}\s+)+)'


def prefix_errors(title: str) -> list[str]:
    """Return prefix errors for a title (empty list when valid)."""
    reasons = ', '.join(REASON_CODES)
    missing_anchor = [
        f"Tittel må starte med Jira-nummer eller en grunnkode ({reasons}).\n"
        f"  Valgfrie tilleggskoder: TOGGLE, G4P, DAPI/DWEB/DB (avhengighet).\n"
        f"  Eksempler: '1234 Beskrivelse', '1234 TOGGLE Beskrivelse', 'TEK Beskrivelse'\n"
        f"  Nåværende: {title}"
    ]
    match = re.match(PREFIX_PATTERN, title)
    if not match:
        return missing_anchor
    codes = match.group(1).split()
    if 'NOJIRA' in codes:
        return [
            f"NOJIRA brukes ikke lenger. Bruk Jira-nummer eller en grunnkode ({reasons}).\n"
            f"  Nåværende: {title}"
        ]
    anchor = next((i for i, c in enumerate(codes) if re.fullmatch(ANCHOR_PATTERN, c)), None)
    flags_before = [c for c in codes[:anchor] if c in FLAG_CODES]
    if anchor is None and not flags_before:
        return missing_anchor
    if flags_before:
        return [
            f"'{' '.join(flags_before)}' kan ikke stå alene, og skal stå etter Jira-nummer eller grunnkode ({reasons}).\n"
            f"  Eksempler: '1234 G4P Beskrivelse', 'VAKT G4P Beskrivelse'\n"
            f"  Nåværende: {title}"
        ]
    return []


def validate_pr_title(title: str, pr_number: int | None = None) -> tuple[bool, list[str]]:
    """
    Validate a PR title.

    Args:
        title: The PR title to validate
        pr_number: Optional PR number (will be appended as " (#123)")

    Returns:
        Tuple of (is_valid, list of error/warning messages)
    """
    errors = []
    warnings = []

    errors.extend(prefix_errors(title))

    # Calculate full title length (including PR number suffix)
    full_title = title
    if pr_number:
        full_title = f"{title} (#{pr_number})"

    if len(full_title) > MAX_TITLE_LENGTH:
        over_by = len(full_title) - MAX_TITLE_LENGTH
        errors.append(
            f"Tittel er {len(full_title)} tegn, maks er {MAX_TITLE_LENGTH} (over med {over_by}).\n"
            f"  Nåværende: {full_title}\n"
            f"  Tips: Forkort til maks {MAX_TITLE_LENGTH - (len(f' (#{pr_number})') if pr_number else 0)} tegn"
        )
    elif len(full_title) > MAX_TITLE_LENGTH - 10:
        warnings.append(
            f"Tittel er {len(full_title)} tegn, nær grensen på {MAX_TITLE_LENGTH}."
        )

    messages = []
    if errors:
        messages.extend([f"❌ {e}" for e in errors])
    if warnings:
        messages.extend([f"⚠️  {w}" for w in warnings])
    if not errors and not warnings:
        messages.append(f"✅ Tittel OK ({len(full_title)} tegn)")

    return len(errors) == 0, messages


def main():
    """CLI interface for validation."""
    if len(sys.argv) < 2:
        print("Usage: python validate_pr_title.py <title> [pr_number]")
        print()
        print("Examples:")
        print('  python validate_pr_title.py "MEL-1234 Add user validation"')
        print('  python validate_pr_title.py "MEL-1234 Add user validation" 456')
        sys.exit(1)

    title = sys.argv[1]
    pr_number = int(sys.argv[2]) if len(sys.argv) > 2 else None

    is_valid, messages = validate_pr_title(title, pr_number)

    for msg in messages:
        print(msg)

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
