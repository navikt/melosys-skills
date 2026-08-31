#!/usr/bin/env bash
# Mekanisk sjekk for kommentar-standard:
#   1) kommentarlinjer per fil, <base> → arbeidstre
#   2) er koden identisk når alle kommentarer strippes? (beviset for «kommentar-only»)
#   3) treff på sjargong-/review-historikk-ord i kommentarer og strenger
#
# Bruk:  kommentar-sjekk.sh [--base <ref>] [--ord <fil-med-ett-ord-per-linje>] [fil ...]
#   Uten filer: alle .kt/.java/.ts/.py-filer endret mot <base> (default HEAD).
set -uo pipefail

base=HEAD
ordfil=""
files=()
while [ $# -gt 0 ]; do
  case "$1" in
    --base) base="$2"; shift 2 ;;
    --ord) ordfil="$2"; shift 2 ;;
    *) files+=("$1"); shift ;;
  esac
done

if [ ${#files[@]} -eq 0 ]; then
  while IFS= read -r f; do files+=("$f"); done < <(git diff --name-only "$base" -- '*.kt' '*.java' '*.ts' '*.py' 2>/dev/null)
fi
[ ${#files[@]} -eq 0 ] && { echo "ingen filer"; exit 0; }

# Default-ordliste: intern sjargong fra tidligere runder + markører for review-arkeologi.
default_ord='sikkerhetssele|\bsele\b|\bselen\b|\bseler\b|kaprer|kapret|kapre|kvitter|proxy|frikjenn|myntkast|nyeste-plassen|review [0-9]{2}\.[0-9]{2}|Copilot|tidligere ble|slik den ble før|forrige runde|runde [0-9]|MELOSYS-[0-9]+'
if [ -n "$ordfil" ]; then
  ord=$(grep -v '^\s*$' "$ordfil" | paste -sd'|' -)
else
  ord="$default_ord"
fi

strip() { grep -v '^\s*\*' | grep -v '^\s*/\*\*' | grep -v '^\s*//' | sed 's|[[:space:]]*//.*||' | grep -v '^\s*$'; }
count() { grep -c '^\s*//\|^\s*/\*\*\|^\s*\*' 2>/dev/null || true; }

echo "== kommentarlinjer ($base → arbeidstre)"
for f in "${files[@]}"; do
  before=$(git show "$base:$f" 2>/dev/null | count)
  after=$(count < "$f")
  printf '  %-60s %4s → %4s\n' "$(basename "$f")" "${before:-0}" "$after"
done

echo "== kode identisk med kommentarer strippet?"
for f in "${files[@]}"; do
  if git cat-file -e "$base:$f" 2>/dev/null; then
    if diff -q <(git show "$base:$f" | strip) <(strip < "$f") >/dev/null; then
      echo "  identisk: $(basename "$f")"
    else
      echo "  ENDRET:   $(basename "$f")  (kjør: diff <(git show $base:$f | strip) <(strip < $f))"
    fi
  else
    echo "  ny fil:   $(basename "$f")"
  fi
done

echo "== sjargong / review-historikk (kommentarer, strenger, testnavn)"
hits=0
for f in "${files[@]}"; do
  while IFS= read -r line; do
    echo "  $(basename "$f"):$line"; hits=$((hits+1))
  done < <(grep -n -i -E "$ord" "$f" | grep -v -E '^\s*[0-9]+:\s*(SELECT|FROM|WHERE|JOIN|AND|OR|INSERT|UPDATE|DELETE|MERGE)\b')
done
[ $hits -eq 0 ] && echo "  ingen treff"
echo "  (ordliste: $ord)"
