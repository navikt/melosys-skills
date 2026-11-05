#!/usr/bin/env python3
"""Kjør med: python3 -B tests/test_validate_pr_title.py"""

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
COPIES = [
    ROOT / "nav-create-pr/scripts/validate_pr_title.py",
    ROOT / "nav-squash-pr-message/scripts/validate_pr_title.py",
]

MANGLER_BESKRIVELSE = "mangler beskrivelse"
NOJIRA_FORBUDT = "NOJIRA brukes ikke"
DOBBEL_KODE = "to ganger"
KAN_IKKE_STAA_ALENE = "kan ikke stå alene"
MANGLER_ANKER = "mangler Jira-nummer"

REJECTED = [
    ("1234 TOGGLE", MANGLER_BESKRIVELSE),
    ("1234 DB", MANGLER_BESKRIVELSE),
    ("TEK G4P", MANGLER_BESKRIVELSE),
    ("TEK DOK", MANGLER_BESKRIVELSE),
    ("TEK 1234", MANGLER_BESKRIVELSE),
    ("TEK ", MANGLER_BESKRIVELSE),
    ("1234 ", MANGLER_BESKRIVELSE),
    ("TEK\n", MANGLER_BESKRIVELSE),
    ("TEK", MANGLER_BESKRIVELSE),
    ("1234", MANGLER_BESKRIVELSE),
    ("TEK -", MANGLER_BESKRIVELSE),
    ("TEK NOJIRA", NOJIRA_FORBUDT),
    ("1234 NOJIRA", NOJIRA_FORBUDT),
    ("TEK NOJIRA: Adminendepunkt", NOJIRA_FORBUDT),
    ("TEK NOJIRA:Adminendepunkt", NOJIRA_FORBUDT),
    ("1234 G4P NOJIRA: Rydd", NOJIRA_FORBUDT),
    ("NOJIRA: Adminendepunkt", NOJIRA_FORBUDT),
    ("NOJIRA", NOJIRA_FORBUDT),
    ("VAKT VAKT Legg til", DOBBEL_KODE),
    ("TEK 2 TEK Rydd", DOBBEL_KODE),
    ("1234 G4P G4P Rydd", DOBBEL_KODE),
    ("G4P", KAN_IKKE_STAA_ALENE),
    ("TOGGLE", KAN_IKKE_STAA_ALENE),
    ("DB migrering", MANGLER_ANKER),
    ("DAPI 7990 Rydd", MANGLER_ANKER),
    ("2 nye felt", MANGLER_ANKER),
    ("Legg til felt", MANGLER_ANKER),
    ("12 nye felt", MANGLER_ANKER),
    ("TEK NOJIRA Rydd", NOJIRA_FORBUDT),
    ("G4P NOJIRA: Rydd", NOJIRA_FORBUDT),
    ("G4P G4P Rydd", KAN_IKKE_STAA_ALENE),
    # Fix round 2: tegnsetting rundt NOJIRA
    ("TEK NOJIRA, Rydd", NOJIRA_FORBUDT),
    ("TEK NOJIRA; Rydd", NOJIRA_FORBUDT),
    ("TEK NOJIRA/Rydd", NOJIRA_FORBUDT),
    ("TEK NOJIRA.", NOJIRA_FORBUDT),
    ("TEK NOJIRA-", NOJIRA_FORBUDT),
    ("TEK NOJIRA– Rydd", NOJIRA_FORBUDT),
    ("TEK [NOJIRA] Rydd", NOJIRA_FORBUDT),
    ("TEK (NOJIRA) Rydd", NOJIRA_FORBUDT),
    ("TEK nojira: Rydd", NOJIRA_FORBUDT),
    ("TEK Nojira: Rydd", NOJIRA_FORBUDT),
    ("6539 / NOJIRA: Fiks feil", NOJIRA_FORBUDT),
    ("NOJIRA, Rydd", NOJIRA_FORBUDT),
    ("TEK NOJIRA-flagget fjernes", NOJIRA_FORBUDT),
    # Fix round 2: kode med tegnsetting er ikke en beskrivelse
    ("1234 TOGGLE:", MANGLER_BESKRIVELSE),
    ("TEK G4P:", MANGLER_BESKRIVELSE),
    ("TEK DB.", MANGLER_BESKRIVELSE),
    ("TEK 1234:", MANGLER_BESKRIVELSE),
    ("TEK _", MANGLER_BESKRIVELSE),
    ("TEK (#12)", MANGLER_BESKRIVELSE),
    ("1234 TOGGLE (#55)", MANGLER_BESKRIVELSE),
]

ACCEPTED = [
    "1234 Beskrivelse",
    "1234 TOGGLE G4P Beskrivelse",
    "TEK Fjern NOJIRA: krev Jira-nummer",
    "1234 Fjern NOJIRA",
    "TEK G4P Rydd",
    "8195 DB DWEB Noe",
    "1234 2 nye felt",
    "8293 TEK Rydd",
    "TEK Nojiraregel fjernes",
    "TEK RYDD",
    "TEK ÆØÅ",
    "TEK DB-migrering",
    "DOK Beskrivelse",
    "VAKT Rydd",
    "PRODFIX Rydd",
]


def load(path):
    spec = importlib.util.spec_from_file_location(path.parent.parent.name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidatePrTitle(unittest.TestCase):
    def test_rejected(self):
        for path in COPIES:
            module = load(path)
            for title, reason in REJECTED:
                with self.subTest(copy=path.parent.parent.name, title=title):
                    valid, messages = module.validate_pr_title(title)
                    self.assertFalse(valid, messages)
                    self.assertIn(reason, "\n".join(messages))

    def test_accepted(self):
        for path in COPIES:
            module = load(path)
            for title in ACCEPTED:
                with self.subTest(copy=path.parent.parent.name, title=title):
                    valid, messages = module.validate_pr_title(title)
                    self.assertTrue(valid, messages)

    def test_copies_are_identical(self):
        self.assertEqual(COPIES[0].read_bytes(), COPIES[1].read_bytes())


if __name__ == "__main__":
    unittest.main()
