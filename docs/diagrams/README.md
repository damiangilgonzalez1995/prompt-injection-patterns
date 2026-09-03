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

## Pattern sketches (hand-drawn)

`patterns/01.png … 06.png` are hand-drawn (pencil style) scenes that draw the
actual agents and how each pattern works, rendered from `src/sketch.html` with
[rough.js](https://roughjs.com) (vendored locally as `src/rough.js`) and the
Caveat/Kalam fonts (`src/*.ttf`).

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
BASE="$(pwd)/docs/diagrams"
for n in 01 02 03 04 05 06; do
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --allow-file-access-from-files \
    --virtual-time-budget=2500 --screenshot="$BASE/patterns/$n.png" \
    --window-size=1120,640 "file:///$BASE/src/sketch.html#$n"
done
```

Edit the `SCENES` object in `src/sketch.html` to change a drawing.
