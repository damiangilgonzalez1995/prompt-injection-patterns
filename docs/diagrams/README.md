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
BASE="$(pwd -W)/docs/diagrams"   # pwd -W: git bash must emit C:/... not /c/...
for n in 05 06; do
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --allow-file-access-from-files \
    --virtual-time-budget=2500 --screenshot="$BASE/patterns/$n.png" \
    --window-size=1120,640 "file:///$BASE/src/sketch.html#$n"
done
```

Patterns 01-04 are drawn at their own canvas sizes:

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
BASE="$(pwd -W)/docs/diagrams"
# the pattern itself
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --allow-file-access-from-files \
  --virtual-time-budget=3000 --screenshot="$BASE/patterns/01.png" \
  --window-size=1280,780 "file:///$BASE/src/sketch.html#01"
# the threat it defends against
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --allow-file-access-from-files \
  --virtual-time-budget=3000 --screenshot="$BASE/patterns/01-threat.png" \
  --window-size=1280,820 "file:///$BASE/src/sketch.html#01t"
# pattern 02
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \n  --force-device-scale-factor=2 --allow-file-access-from-files \n  --virtual-time-budget=3000 --screenshot="$BASE/patterns/02.png" \n  --window-size=1280,880 "file:///$BASE/src/sketch.html#02"
# pattern 02, the binding mechanism on its own
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --allow-file-access-from-files \
  --virtual-time-budget=3000 --screenshot="$BASE/patterns/02-bindings.png" \
  --window-size=1280,880 "file:///$BASE/src/sketch.html#02b"
# pattern 03
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \n  --force-device-scale-factor=2 --allow-file-access-from-files \n  --virtual-time-budget=3000 --screenshot="$BASE/patterns/03.png" \n  --window-size=1400,980 "file:///$BASE/src/sketch.html#03"
# pattern 04
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \n  --force-device-scale-factor=2 --allow-file-access-from-files \n  --virtual-time-budget=3000 --screenshot="$BASE/patterns/04.png" \n  --window-size=1400,800 "file:///$BASE/src/sketch.html#04"
```

`01-threat.png` (scene `01t`) draws the attack the pattern exists to stop: a
third party writes instructions into a data source, the agent fetches them, and
they land in the context window with the same authority as the system prompt.
`01.png` (scene `01`) draws the pattern. `02.png` draws Plan-Then-Execute:
the plan frozen above the line, the executor walking it below, and the one
declared binding that carries a value from step 1 into step 2. `02-bindings.png` (scene `02b`) zooms in on
the binding itself: the declaration on the left, the returned record on the
right, and `resolve()` checking the named field against the whitelist before
it becomes an argument. `03.png` draws the three isolated lanes, the claim one poisoned document
makes about a *different* document, and the lane wall that claim cannot cross. `04.png` draws the wall between the model that reads and the
model that acts: the typed card that is the only thing passing through it, and
`resolve()` joining a reference to its real value outside every prompt. All
of them are
generic — no notebook-specific ids or amounts — so they explain the shape,
not one example. Notebook 02 reuses `01-threat.png`, since the threat is the
same one.

Edit the `SCENES` object in `src/sketch.html` to change a drawing.
