# Jarvis-v2

A clean, minimal voice assistant for Windows. A full reset of the old Jarvis:
it talks out of the box, it listens, and every button in the window works.

## What it does today

- **Talks** — Windows built-in voice (SAPI), zero setup. Optional Fish Audio cloud voice.
- **Listens** — offline speech recognition (Vosk, ~40MB model auto-downloads once).
  Push-to-talk button, or say "hey jarvis" (opt-in via `wake_word: true`).
- **No mic?** Still runs — type in the box instead. It tells you that's what's happening.
- **Basic PC control** — open apps ("open notepad"), volume up/down/mute.
- **3 plugins** — time/date, open apps, volume. Adding one is a single small file.
- **AI answers (optional)** — Groq key for anything beyond the offline skills. Free tier, no card.

That's it. No "50+ plugins", no dead buttons.

## Install (Windows 11)

1. Install Python 3.12+ from https://www.python.org/downloads/
   (tick **"Add python.exe to PATH"**).
2. Unzip this folder anywhere, double-click **JARVIS.bat**.
3. First run: a setup wizard asks for optional keys (Groq, Fish Audio).
   Press Enter through all of it — offline mode works fine.
4. The Jarvis window opens and says "Jarvis online."

## Keys (all optional)

They go in `config/local.yaml` (created by the wizard, never committed):

```yaml
groq_api_key: "gsk_..."        # AI answers. Free at console.groq.com
fish_api_key: "..."            # cloud voice
fish_reference_id: "..."      # your Fish Audio voice
tts_engine: "fish"            # switch voice from "sapi" to "fish"
```

## Project layout

```
JARVIS.bat            Windows launcher
config.yaml           defaults (safe to read, no secrets)
config/local.yaml     your keys (gitignored)
jarvis/voice/speak.py TTS: SAPI default, Fish Audio optional
jarvis/voice/listen.py Vosk STT, push-to-talk + wake word
jarvis/brain.py       offline brain, Groq when a key is set
jarvis/control/pc.py  open apps, type, keys, volume
jarvis/plugins/       tiny plugin API + 3 working examples
jarvis/ui.py          tkinter window
jarvis/setup_wizard.py first-run console wizard
tests/                mocked smoke tests (pytest)
```

## Running tests

```
pip install -r requirements.txt
python -m pytest tests/ -q
```

No mic, speaker, or network needed — everything is mocked.
