# digdir-roadmap-util

Verktøy som henter roadmap-saker fra Digdirs GitHub-prosjekt ([digdir, prosjekt 8](https://github.com/orgs/digdir/projects/8)) og lager en rapport som CSV eller JSON. Rapporten publiseres ukentlig som en GitHub-release, og mottakerne får en e-post med lenke til den.

Bare saker med en `product/...`-label som står i `projects` i konfigurasjonen kommer med i rapporten.

## Innhold

| Fil / mappe | Beskrivelse |
|---|---|
| `GithubRelease.py` | Brukes av GitHub Actions. Lager `output/<report_name>.csv` ut fra `config.yml`. |
| `mail_notifier.py` | Brukes av GitHub Actions. Henter siste release og sender e-post med lenke til rapporten. |
| `DigdirRoadmap.Console.py` | Kommandolinjeverktøy for lokal kjøring. Bruker `config_test.yml`. |
| `DigdirRoadmap.py` | Bygger roadmap-elementene fra prosjektdataene. |
| `GithubGraphQL.py` | GraphQL-spørringer mot GitHub, med nye forsøk ved feil (`backoff`). |
| `Helpers.py` | Lager CSV og sender e-post via Gmail SMTP. |
| `DigdirRoadmapHttpTrigger/`, `DigdirRoadmapTimerTrigger/` | Azure Functions (HTTP og timer). |
| `config.yml` | Konfigurasjon for produksjon. |
| `config_test.yml` | Konfigurasjon for lokal kjøring og test. |
| `.github/workflows/` | GitHub Actions-jobber, se [GitHub Actions](#github-actions). |

## Kom i gang lokalt

### Forutsetninger

- Python 3.10 eller nyere. Jobben i GitHub Actions bruker 3.10.
- Et GitHub-token med lesetilgang til prosjektet, se [Tokens og secrets](#tokens-og-secrets).

### Installasjon

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Sett tokenet

Tokenet sendes uendret som `Authorization`-header, så verdien **må ha `Bearer ` foran**:

```bash
export DIGIDIR_ROADMAP_TOKEN="Bearer github_pat_xxxxxxxx"
```

Sjekk at tokenet fungerer og har tilgang til prosjektet:

```bash
curl -s -H "Authorization: $DIGIDIR_ROADMAP_TOKEN" https://api.github.com/graphql -d '{"query":"{ viewer { login } organization(login: \"digdir\") { projectV2(number: 8) { title } } }"}'
```

### Lag rapport slik jobben gjør

```bash
python GithubRelease.py
```

Rapporten havner i `output/<report_name>.csv`. Navnet hentes fra `config.yml`.

### Kommandolinjeverktøyet

`DigdirRoadmap.Console.py` leser `config_test.yml`:

```bash
python DigdirRoadmap.Console.py --type csv
```

| Valg | Beskrivelse |
|---|---|
| `--type screen` | Skriver JSON til skjermen. Dette er standard. |
| `--type csv` | Skriver `output/<report_name>.csv`. |
| `--type json` | Skriver `output/<report_name>.json`. |
| `--type mail` | Sender rapporten som vedlegg. Krever `SMTP_ACCOUNT` og `SMTP_PASSWORD`. |
| `--type all` | Gjør `csv`, `json` og `screen`. |
| `--save_binary` | Lagrer resultatet i `output/roadmap.pickle`. |
| `--testrun` | Henter ingenting fra GitHub, men leser `output/roadmap.pickle`. Krever en kjøring med `--save_binary` først. |

Med `devlop_mode: True` i `config_test.yml` lagres svarene fra GitHub i `output/<ddmmyy>/`. De brukes på nytt samme dag i stedet for å spørre GitHub igjen. Slett mappen hvis du vil ha ferske data.

### Tester

```bash
pytest test_DigdirRoadmap.py test_DigdirRoadmapItem.py
```

Testene mocker GitHub-kallene og trenger ikke token. CI-jobben kjører `pytest` uten argumenter. Da plukkes også andre `*_test.py`-filer i mappen opp, så lokale testfiler som ikke er committet kan få kjøringen til å feile.

## Konfigurasjon

`config.yml` og `config_test.yml` har samme struktur:

```yaml
mail:
  send_notification_mail: True   # sende e-post eller ikke
  mail_receipients:              # mottakere av e-posten
    - navn@digdir.no

projects:                        # product-labels som tas med i rapporten
  - product/autorisasjon

report_name: roadmap_report      # filnavn uten .csv

latest_release_url: 'https://api.github.com/repos/ekorra/digdir-roadmap-util/releases/latest'

devlop_mode: False               # lagre GitHub-svar lokalt (bare Console)
```

Nye produkter legges til ved å føye `product/<navn>`-labelen til `projects` i `config.yml`.

## GitHub Actions

| Workflow | Fil | Når | Hva |
|---|---|---|---|
| Roadmap report generator | `actions.yml` | Mandag 11:00 UTC, eller manuelt | Lager rapporten, oppretter release og sender e-post. |
| Roadmap report generator - TEST12 / TEST16 | `test.actions.yml`, `test2.actions.yml` | Tirsdag–fredag 12:00 / 16:00 UTC, eller manuelt | Lager rapporten og sender e-post, men oppretter ingen release. |
| continuous_integration | `CI.yml` | Hver push | Installerer avhengigheter og kjører `pytest`. |

Tidene i `cron` er i UTC. 11:00 UTC er 12:00 norsk vintertid og 13:00 sommertid. Bruk [crontab.guru](https://crontab.guru/) for hjelp med formatet (`minutt time dag måned ukedag`).

Releasen får taggen `<uke>_<år>`, for eksempel `42_2026`. Finnes taggen fra før, legges et tidsstempel til (`42_2026_103015`). `output/roadmap_report.csv` legges ved som fil.

Du kan kjøre jobben manuelt under **Actions → Roadmap report generator → Run workflow**.

### Tokens og secrets

Legges inn under **Settings → Secrets and variables → Actions**.

| Secret | Brukes til | Format og tilganger |
|---|---|---|
| `DIGIDIR_ROADMAP_TOKEN` | Lese prosjektet og issues i `digdir/roadmap` | Verdien må være `Bearer <token>`. **Fine-grained:** resource owner `digdir`, lesetilgang til *Organization → Projects* og *Repository → Issues* for `digdir/roadmap`. Kan kreve godkjenning fra en org-admin. **Classic:** `read:project` og `repo`. |
| `RELEASE_TOKEN` | Opprette release i dette repoet | Bare tokenet, uten prefiks. Fine-grained med *Contents: Read and write* og *Metadata: Read* for `ekorra/digdir-roadmap-util`. |
| `SMTP_ACCOUNT` | Avsenderadresse | Gmail-adressen e-posten sendes fra. |
| `SMTP_PASSWORD` | Innlogging mot `smtp.gmail.com` | Et [app-passord](https://myaccount.google.com/apppasswords) for kontoen, ikke det vanlige passordet. |

Tokens utløper. Sett en påminnelse i kalenderen før utløpsdatoen.

## Azure Functions

Prosjektet kan også kjøres som Azure Function App:

- **`DigdirRoadmapHttpTrigger`** returnerer roadmapen som JSON. Bruker `config.yml`.
- **`DigdirRoadmapTimerTrigger`** sender rapporten som CSV-vedlegg på e-post. Henter prosjekter fra `config_test.yml` og mottakere fra `config.yml`. Tidsplanen står i `function.json`, med sekunder først: `0 0 12 * * 1` betyr mandag 12:00.

Kjør lokalt med [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local) og [Azurite](https://learn.microsoft.com/azure/storage/common/storage-use-azurite). Fyll inn `DIGIDIR_ROADMAP_TOKEN`, `SMTP_ACCOUNT` og `SMTP_PASSWORD` i `local.settings.json`, men **ikke commit verdiene**. Start så:

```bash
func host start
```

I Azure settes de samme verdiene som Application settings.

## Feilsøking

| Feil | Årsak og løsning |
|---|---|
| `401 Unauthorized` fra `api.github.com/graphql` | Tokenet er ugyldig, utløpt eller mangler `Bearer ` foran. Test med `curl`-kommandoen over. |
| `projectV2` er `null`, eller svaret har `errors` | Tokenet er gyldig, men har ikke tilgang til prosjektet i digdir-organisasjonen. |
| `ModuleNotFoundError` | En avhengighet mangler i `requirements.txt`. Pakker som importeres direkte i koden må stå der, ikke bare komme med som avhengighet av en annen pakke. |
| `Token not available!` i `status.log` | `DIGIDIR_ROADMAP_TOKEN` er ikke satt. |
| E-post sendes ikke | Sjekk `SMTP_ACCOUNT`, `SMTP_PASSWORD` (app-passord) og `send_notification_mail` i `config.yml`. |
