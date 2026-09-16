# Jarvis-v2 — build notes (2026-09-16)

Clean-room rebuild. 100% original code, written from scratch for this reset.
Nothing was copied from the old Jarvis repo, the Ultron project, or anywhere else.

## What was built

- `jarvis/config.py` — `config.yaml` defaults + `config/local.yaml` overrides (gitignored).
- `jarvis/voice/speak.py` — TTS. Default engine `sapi` via pyttsx3 (Windows built-in,
  zero-config — this is the #1 fix for "it won't speak at all"). Optional `fish`
  engine: Fish Audio `POST https://api.fish.audio/v1/tts` with `reference_id`,
  WAV response played through `winsound` (Windows stdlib, no audio-player dep).
  `Speaker` wraps engine + on/off toggle; voice and typed input share one speak path.
- `jarvis/voice/listen.py` — Vosk offline STT. `vosk-model-small-en-us-0.15`
  (~40MB) auto-downloads from alphacephei.com on first mic use into `models/`
  (`.ready` sentinel so it never re-downloads). `capture_once()` for push-to-talk,
  `WakeWordListener` thread for "hey jarvis" (opt-in). All third-party imports are
  lazy; missing mic/packages produce clear messages, never crashes.
- `jarvis/brain.py` — offline-first: plugins → small talk → Groq (only with key).
  Without a key it answers time/apps/volume/small talk and says plainly when a
  question needs a Groq key.
- `jarvis/control/pc.py` — `open_app` (`os.startfile` on Windows), `type_text`,
  `press_key`, `volume_up/down/mute` via pynput media keys (no pycaw). Every
  function returns `(ok, message)`, never raises.
- `jarvis/plugins/` — tiny API (`Plugin`: `match`/`run`), auto-loads `*_plugin.py`.
  Ships 3 working examples: `time`, `apps` (open notepad/calculator/browser/...),
  `volume`.
- `jarvis/ui.py` — tkinter (stdlib): conversation log, Push-to-Talk button,
  type-in entry + Send (Return works too), voice on/off toggle, Quit, status bar.
  Listening/speaking run on worker threads; UI updates via `after()`. Every
  control is wired — no decorative buttons.
- `jarvis/setup_wizard.py` — first-run console wizard. All keys optional and
  skippable; ends with a live "Jarvis online." voice test.
- `jarvis/main.py` / `__main__.py` — entry point: speaks "Jarvis online." on boot
  (plus a spoken notice when no mic is found), then opens the UI.
- `JARVIS.bat` — checks python, pip-installs requirements, runs wizard on first
  launch, starts the app.
- `requirements.txt` — pinned (see below).
- `tests/test_smoke.py` — 27 mocked tests, no mic/speaker/network needed.
- `README.md` — honest: lists only what exists today.

## Deliberately left out

- pygame (no Python 3.14 wheel) — Fish Audio playback uses `winsound` instead.
- pycaw for volume — pynput media keys need no extra dep.
- Screenshot control — optional per spec, skipped to keep the reset lean.
- A web/Electron UI — tkinter is stdlib and always works.
- Dozens of plugins — 3 working ones beat 50 dead ones.
- Auto-start / installer EXE — out of scope for the reset; JARVIS.bat is the launcher.
- Wake word defaults to OFF (mic capture costs CPU); enable with `wake_word: true`.

## Exact pip versions (requirements.txt)

| Package | Version | Why this one |
|---|---|---|
| pyttsx3 | 2.99 | latest; pure-Python, SAPI via comtypes on Windows |
| vosk | 0.3.45 | py3-none-win_amd64 wheel (version-agnostic, 3.14-safe) |
| sounddevice | 0.5.6 | py3-none-win_amd64 wheel (bundles PortAudio) |
| pynput | 1.8.2 | latest; pure-Python |
| requests | 2.34.2 | pure-Python |
| pyyaml | 6.0.3 | has cp314-win_amd64 wheel |

Wheel availability verified against the PyPI JSON API on 2026-09-16.
`vosk`/`sounddevice` ship `py3-none-*` wheels, which install on any Python 3,
including 3.14.

## Test results

`python -m pytest tests/ -q` on the Linux build VM: **26/26 pass**
(see test file for the list). Also `py_compile` clean on all 19 source files.

## Could NOT verify on Linux (needs the user's Windows PC)

- Actual SAPI speech out of the speakers (pyttsx3 needs Windows SAPI).
- Fish Audio end-to-end (needs a real key + Windows `winsound`).
- Microphone capture + Vosk model download (no mic on this VM).
- `os.startfile`, media keys, and the tkinter window rendering on Windows 11.
- JARVIS.bat itself (Windows-only).
