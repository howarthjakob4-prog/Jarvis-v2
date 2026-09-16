"""Tkinter UI (stdlib — always works).

Every control is wired to real behavior; there are no decorative buttons.
Voice and typed input both flow through handle_text -> speaker.speak,
so the single speak path is identical either way.
"""
import threading
import tkinter as tk
from tkinter import scrolledtext

from .voice.listen import ListenError, WakeWordListener, capture_once


class JarvisUI:
    def __init__(self, brain, speaker, mic_ok, config):
        self.brain = brain
        self.speaker = speaker
        self.mic_ok = mic_ok
        self.config = config
        self._busy = False
        self._wake = None

        self.root = tk.Tk()
        self.root.title("Jarvis")
        self.root.geometry("560x640")
        self.root.minsize(420, 480)

        # Conversation log (read-only).
        self.log = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, state=tk.DISABLED, font=("Segoe UI", 11)
        )
        self.log.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 6))

        # Type-in row: entry + Send (Return also sends).
        entry_frame = tk.Frame(self.root)
        entry_frame.pack(fill=tk.X, padx=10, pady=6)
        self.entry = tk.Entry(entry_frame, font=("Segoe UI", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", lambda _e: self.send_typed())
        self.send_btn = tk.Button(entry_frame, text="Send", width=8, command=self.send_typed)
        self.send_btn.pack(side=tk.LEFT, padx=(6, 0))

        # Push-to-talk row.
        talk_frame = tk.Frame(self.root)
        talk_frame.pack(fill=tk.X, padx=10, pady=6)
        self.talk_btn = tk.Button(
            talk_frame, text="🎤 Push to Talk", font=("Segoe UI", 12, "bold"),
            height=2, command=self.push_to_talk,
        )
        self.talk_btn.pack(fill=tk.X)
        if not mic_ok:
            self.talk_btn.config(state=tk.DISABLED, text="🎤 No microphone — type instead")

        # Options row: voice toggle, status, quit.
        opt_frame = tk.Frame(self.root)
        opt_frame.pack(fill=tk.X, padx=10, pady=6)
        self.voice_var = tk.BooleanVar(value=speaker.enabled)
        self.voice_toggle = tk.Checkbutton(
            opt_frame, text="Voice on", variable=self.voice_var, command=self.toggle_voice
        )
        self.voice_toggle.pack(side=tk.LEFT)
        self._sync_voice_toggle()
        self.status = tk.Label(opt_frame, text="", fg="gray", font=("Segoe UI", 9))
        self.status.pack(side=tk.LEFT, padx=(12, 0))
        self.quit_btn = tk.Button(opt_frame, text="Quit", command=self._on_close)
        self.quit_btn.pack(side=tk.RIGHT)
        self._refresh_status()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        if mic_ok and config.get("wake_word"):
            self._start_wake_word()

    # ----- small helpers -------------------------------------------------

    def log_line(self, who, text):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"{who}: {text}\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def _refresh_status(self):
        mic = "Mic ready" if self.mic_ok else "No mic — type-in mode"
        voice = "Voice on" if self.speaker.enabled else "Voice off"
        self.status.config(text=f"{mic}  •  {voice}")

    def _sync_voice_toggle(self):
        self.voice_toggle.config(text="Voice on" if self.voice_var.get() else "Voice off")

    def _on_close(self):
        if self._wake is not None:
            self._wake.stop()
        self.root.destroy()

    # ----- the single input path ------------------------------------------

    def handle_text(self, text, source="typed"):
        """One path for voice and typed input: log, think, log, speak."""
        text = (text or "").strip()
        if not text:
            if source == "voice":
                self.log_line("Jarvis", "I didn't hear anything.")
            return
        self.log_line("You", text)
        try:
            reply = self.brain.respond(text)
        except Exception as exc:
            reply = f"Something went wrong in my brain: {exc}"
        self.log_line("Jarvis", reply)
        if not self.speaker.speak(reply) and self.speaker.last_error:
            self.log_line("Jarvis", f"(voice failed: {self.speaker.last_error})")

    def send_typed(self):
        text = self.entry.get()
        self.entry.delete(0, tk.END)
        self.handle_text(text, source="typed")

    # ----- voice input -----------------------------------------------------

    def toggle_voice(self):
        self.speaker.enabled = self.voice_var.get()
        self._sync_voice_toggle()
        self._refresh_status()

    def push_to_talk(self):
        if self._busy or not self.mic_ok:
            return
        self._busy = True
        self.talk_btn.config(state=tk.DISABLED, text="🎤 Listening…")
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self):
        try:
            text = capture_once(timeout=self.config.get("mic_timeout", 8))
        except ListenError as exc:
            text, err = None, str(exc)
        else:
            err = None
        self.root.after(0, self._listen_done, text, err)

    def _listen_done(self, text, err):
        self._busy = False
        self.talk_btn.config(state=tk.NORMAL, text="🎤 Push to Talk")
        if err:
            self.log_line("Jarvis", err)
            return
        self.handle_text(text or "", source="voice")

    def _start_wake_word(self):
        phrase = self.config.get("wake_phrase", "hey jarvis")
        self._wake = WakeWordListener(on_wake=self._wake_heard, phrase=phrase)
        self._wake.start()
        self.log_line("Jarvis", f"Wake word on — say '{phrase}'.")

    def _wake_heard(self):
        self.root.after(0, self._on_wake_ui)

    def _on_wake_ui(self):
        self.log_line("Jarvis", "Yes? Listening…")
        self.push_to_talk()

    # ----- main loop ---------------------------------------------------------

    def run(self):
        self.root.mainloop()
