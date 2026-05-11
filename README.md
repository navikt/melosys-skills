# melosys-skills

Delte agent skills for Team Melosys.

Hver skill er en mappe med en `SKILL.md` (frontmatter med `name` + `description`, deretter
instruksjonene) og eventuelt `scripts/` og `references/`. Formatet er agnostisk og kan brukes
av enhver agent som støtter skill-/verktøy-mapper.

## Installasjon

Gjør hver skill-mappe tilgjengelig for agenten din — typisk ved å symlinke eller kopiere
mappene inn i katalogen agenten leser skills fra (sjekk dokumentasjonen til agenten din for
hvor det er):

```bash
# fra rota av dette repoet, til agentens skill-katalog
for d in */; do
  ln -sfn "$PWD/${d%/}" /sti/til/agents/skills/"${d%/}"
done
```

Skills med `disable-model-invocation: true` i frontmatteren kjøres bare når du eksplisitt
ber om dem (`/<navn>`). Resten kan agenten velge selv basert på `description`.

## Skills

### Melosys-spesifikke
| Skill | Hva |
|-------|-----|
| `eux-rina-mock` | Legge til SED/BUC/XSD i melosys-mock sin RINA/EUX-implementasjon |
| `eux-rina-sed-mapping` | NAV SED → RINA-mapping (CDM 4.4), templates og kodeverk |
| `melosys-sed-debugging` | Debugge SED-flyt: melosys-eessi → eux-rina-api → mock, XSD-validering |
| `local-api-tokens` | OAuth-tokens og kall mot lokale Melosys-tjenester |

### Git / PR-arbeidsflyt (NAV-konvensjoner)
| Skill | Hva |
|-------|-----|
| `nav-commit` | `/nav-commit` — commit med norsk format, valgfritt Jira-nummer |
| `nav-create-pr` | `/nav-create-pr` — PR med Jira-nummer-krav og norsk beskrivelse |
| `nav-squash-pr-message` | `/nav-squash-pr-message` — squash-merge-melding med Jira-prefiks |
| `review-loop` | Selv-review-loop på gjeldende PR til den er ren |

### Generelle dev-verktøy
| Skill | Hva |
|-------|-----|
| `docker-build-push` | Bygge/pushe multi-plattform Docker-images til Google Artifact Registry |

## Bidra

Legg til en ny skill som en egen mappe med `SKILL.md` (+ evt. `scripts/` og `references/`).
Bruk relative stier i `SKILL.md` (relativt til skill-mappen) — ikke hardkod absolutte stier
som `~/.claude/skills/...` eller `/Users/...`.
