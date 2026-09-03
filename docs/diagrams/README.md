# Diagrams

Static, hand-designed infographics (PNG) embedded in the main README — not
interactive Mermaid, on purpose.

- `hero.png` — the agent loop and the six guards
- `architecture.png` — foundation layers → patterns → consumers
- `dual-llm.png` — security through state synchronisation

## Regenerate

Source is HTML/CSS in `src/`. Render with headless Chrome:

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
BASE="$(pwd)/docs/diagrams"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --allow-file-access-from-files \
  --screenshot="$BASE/hero.png" --window-size=1552,842 \
  "file:///$BASE/src/hero.html"
```

Adjust `--window-size` height to fit each poster (arch ~700, dual ~640).
