"""Jarvis entry point: wire config -> brain -> voice -> UI."""
from .brain import Brain
from .config import load
from .ui import JarvisUI
from .voice.listen import mic_available
from .voice.speak import Speaker


def main():
    config = load()
    brain = Brain(config)
    speaker = Speaker(config)
    mic_ok = mic_available()

    print("Jarvis starting…")
    print("Mic:", "ready" if mic_ok else "not found — type-in mode")

    boot_line = "Jarvis online."
    if not mic_ok:
        boot_line += " No microphone detected. You can type instead."
    if speaker.enabled and speaker.ok:
        speaker.speak(boot_line)
    elif speaker.error:
        print("Voice unavailable:", speaker.error)

    ui = JarvisUI(brain, speaker, mic_ok, config)
    ui.log_line("Jarvis", boot_line)
    ui.run()


if __name__ == "__main__":
    main()
