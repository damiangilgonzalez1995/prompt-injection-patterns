# Diagrams

Static, hand-designed infographics (PNG) embedded in the main README — not
interactive Mermaid, on purpose.

- `hero.png` — the agent loop and the six guards
- `architecture.png` — foundation layers → patterns → consumers
- `dual-llm.png` — security through state synchronisation

## Regenerate

All diagrams are hand-drawn scenes in `src/sketch.html` (rough.js). Render with headless Chrome — the loop below does the three overview diagrams:

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
BASE="$(pwd)/docs/diagrams"
render(){ "$CHROME" --headless=new --disable-gpu --hide-scrollbars   --force-device-scale-factor=2 --allow-file-access-from-files   --virtual-time-budget=2500 --screenshot="$BASE/$2"   --window-size=$3 "file:///$BASE/src/sketch.html#$1"; }
render hero hero.png 1460,860
render arch architecture.png 1360,620
render dual dual-llm.png 1120,640
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
