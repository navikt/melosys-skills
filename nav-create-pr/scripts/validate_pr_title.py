#!/usr/bin/env python3
"""
Validate PR title for squash merge commits.

Rules:
- Must start with a Jira number (e.g., 1234) or a reason code (VAKT, PRODFIX)
- TOGGLE, G4P and Dependabot codes (DWEB, DAPI) may be added; TOGGLE and G4P
  never stand alone
- NOJIRA is no longer allowed: a missing Jira needs a stated reason
- Max 72 characters total (git recommendation)
"""

import re
import sys

MAX_TITLE_LENGTH = 72
# Anchor codes say where the work comes from; a title needs at least one.
# Modifier codes only qualify an anchor.
# - \d+     : Jira number (e.g., 1234, 7553)
# - D[A-Z]+ : Dependabot (DWEB, DAPI, etc.)
# - REASON_CODES : why there is no Jira ticket. Add new reasons here.
# - MODIFIER_CODES : TOGGLE (feature toggle), G4P (good for prod) — never alone
# NOJIRA is parsed only so it gets a targeted error: it gives no reason.
REASON_CODES = ('VAKT', 'PRODFIX', 'DOK')
MODIFIER_CODES = ('TOGGLE', 'G4P')
ANCHOR_PATTERN = rf"^(\d+|D[A-Z]+|{'|'.join(REASON_CODES)})$"
CODE_PATTERN = rf"(\d+|D[A-Z]+|NOJIRA|{'|'.join(REASON_CODES + MODIFIER_CODES)})"
# Only the leading run of codes is parsed; the rest is free description.
PREFIX_PATTERN = rf'^((?:{CODE_PATTERN}\s+)+)'


def prefix_errors(title: str) -> list[str]:
    """Return prefix errors for a title (empty list when valid)."""
    reasons = ', '.join(REASON_CODES)
    match = re.match(PREFIX_PATTERN, title)
    if not match:
        return [
            f"Tittel må starte med Jira-nummer eller en grunnkode ({reasons}).\n"
            f"  Valgfrie tilleggskoder: TOGGLE, G4P, DWEB/DAPI (Dependabot).\n"
            f"  Eksempler: '1234 Beskrivelse', '1234 TOGGLE Beskrivelse', 'VAKT Beskrivelse'\n"
            f"  Nåværende: {title}"
        ]
    codes = match.group(1).split()
    if 'NOJIRA' in codes:
        return [
            f"NOJIRA brukes ikke lenger. Bruk Jira-nummer eller en grunnkode ({reasons}).\n"
            f"  Nåværende: {title}"
        ]
    if not any(re.match(ANCHOR_PATTERN, c) for c in codes):
        alone = ' '.join(c for c in codes if c in MODIFIER_CODES)
        return [
            f"'{alone}' kan ikke stå alene. Legg til Jira-nummer eller en grunnkode ({reasons}).\n"
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
