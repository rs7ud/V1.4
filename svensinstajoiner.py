import re
import time
import subprocess
import webbrowser
import threading
import sys
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog
from urllib.parse import urlparse, parse_qs

# configs
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"roblosecurity": "", "sound_path": ""}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)


def play_sound(path=None):
    def _play():
        try:
            if path and os.path.exists(path):
                if sys.platform == "win32":
                    import winsound
                    winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                elif sys.platform == "darwin":
                    subprocess.run(["afplay", path], check=False)
                else:
                    subprocess.run(["aplay", path], check=False)
            else:
                if sys.platform == "win32":
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass
    threading.Thread(target=_play, daemon=True).start()


def is_roblox_link(text):
    if not text:
        return False
    patterns = [
        r"https?://www\.roblox\.com/share\?.*type=Server",
        r"https?://www\.roblox\.com/games/\d+.*privateServerLinkCode=",
    ]
    return any(re.search(p, text) for p in patterns)

def resolve_share_link(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    code = params.get("code", [None])[0]
    if not code:
        return None, "i cant extract it"
    # api call
    deep_link = f"roblox://navigation/share_links?code={code}&type=Server"
    return deep_link, None

def extract_direct_link_params(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    link_code = params.get("privateServerLinkCode", [None])[0]
    match = re.search(r"/games/(\d+)", parsed.path)
    place_id = match.group(1) if match else None
    if place_id and link_code:
        return place_id, link_code
    return None

def launch_roblox(place_id, link_code=None):
    if link_code:
        deep_link = f"roblox://experiences/start?placeId={place_id}&privateServerLinkCode={link_code}"
    else:
        # xfxddoweoaf
        deep_link = place_id
    if sys.platform == "win32":
        os.startfile(deep_link)
    elif sys.platform == "darwin":
        subprocess.run(["open", deep_link])
    else:
        subprocess.run(["xdg-open", deep_link])
    return deep_link

# gui frame
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("sols insta joiner by svenbrg")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        self.config = load_config()
        self.watching = False
        self.last_clipboard = ""
        self._build_ui()

    def _build_ui(self):
        PAD = 16
        BG = "#1a1a2e"
        CARD = "#16213e"
        ACC = "#e94560"
        FG = "#eaeaea"
        GRAY = "#8888aa"
        FONT = ("Segoe UI", 10)
        FONT_BOLD = ("Segoe UI", 10, "bold")
        FONT_TITLE = ("Segoe UI", 13, "bold")

        # title
        tk.Label(self.root, text="instant joiner by svenbrg on discord", font=FONT_TITLE,
                 bg=BG, fg=FG).pack(pady=(PAD, 4), padx=PAD)
        tk.Label(self.root, text="insta joiner or uwp joiner in other terms",
                 font=("Segoe UI", 9), bg=BG, fg=GRAY).pack(padx=PAD, pady=(0, 8))

        # tabs for notebooks
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background="#0f3460", foreground=GRAY,
                        padding=[12, 5], font=FONT)
        style.map("TNotebook.Tab",
                  background=[("selected", CARD)],
                  foreground=[("selected", FG)])

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=PAD, pady=(0, PAD))

        # main tab or sum shi
        tab_main = tk.Frame(notebook, bg=BG)
        notebook.add(tab_main, text="  Main  ")

        # if u see this your gay lol
        frame_watch = tk.Frame(tab_main, bg=BG)
        frame_watch.pack(fill="x", pady=14)

        self.status_dot = tk.Label(frame_watch, text="⬤", font=("Segoe UI", 11),
                                   bg=BG, fg="#444466")
        self.status_dot.pack(side="left")

        self.status_label = tk.Label(frame_watch, text="  not watchin",
                                     font=FONT, bg=BG, fg=GRAY)
        self.status_label.pack(side="left")

        self.toggle_btn = tk.Button(frame_watch, text="start",
                                    font=FONT_BOLD, bg="#0f3460", fg=FG,
                                    relief="flat", cursor="hand2",
                                    command=self._toggle_watch, padx=14, pady=6)
        self.toggle_btn.pack(side="right")

        # sounds
        sound_frame = tk.Frame(tab_main, bg=CARD)
        sound_frame.pack(fill="x", pady=(0, 10))

        tk.Label(sound_frame, text="bleep bleep bop", font=FONT_BOLD,
                 bg=CARD, fg=FG).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(sound_frame, text="plays a sound when a server is found ( CUSTOM IS BROKEN )",
                 font=("Segoe UI", 8), bg=CARD, fg=GRAY).pack(anchor="w", padx=12)

        sound_row = tk.Frame(sound_frame, bg=CARD)
        sound_row.pack(fill="x", padx=12, pady=(6, 10))

        self.sound_var = tk.StringVar(value=self.config.get("sound_path", ""))
        tk.Entry(sound_row, textvariable=self.sound_var,
                 font=("Consolas", 8), bg="#0f3460", fg=FG,
                 insertbackground=FG, relief="flat",
                 highlightthickness=1, highlightbackground="#334",
                 highlightcolor=ACC).pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))

        tk.Button(sound_row, text="Browse", font=FONT, bg="#0f3460", fg=GRAY,
                  relief="flat", cursor="hand2", padx=8,
                  command=self._browse_sound).pack(side="left", padx=(0, 4))
        tk.Button(sound_row, text="Test", font=FONT, bg="#0f3460", fg=GRAY,
                  relief="flat", cursor="hand2", padx=8,
                  command=self._test_sound).pack(side="left", padx=(0, 4))
        tk.Button(sound_row, text="Save", font=FONT_BOLD, bg=ACC, fg="white",
                  relief="flat", cursor="hand2", padx=8,
                  command=self._save_sound).pack(side="left")

        # logs
        tk.Label(tab_main, text="Activity Log", font=FONT_BOLD,
                 bg=BG, fg=GRAY).pack(anchor="w")

        log_frame = tk.Frame(tab_main, bg=CARD)
        log_frame.pack(fill="both", expand=True, pady=(4, 0))

        self.log = tk.Text(log_frame, height=8, width=58, font=("Consolas", 9),
                           bg=CARD, fg="#aabbcc", relief="flat",
                           state="disabled", wrap="word",
                           insertbackground=FG)
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

        self.log.tag_config("ok",  foreground="#4ecca3")
        self.log.tag_config("err", foreground="#e94560")
        self.log.tag_config("inf", foreground="#aabbcc")

        self._log("click start then just copy a roblox ps link", "inf")

        # ── Tab 2: Read Me ──
        tab_readme = tk.Frame(notebook, bg=BG)
        notebook.add(tab_readme, text="  Read Me  ")

        readme_card = tk.Frame(tab_readme, bg=CARD)
        readme_card.pack(fill="both", expand=True, pady=10)

        tk.Label(readme_card, text="⚠️  WARNING", font=("Segoe UI", 13, "bold"),
                 bg=CARD, fg=ACC).pack(pady=(24, 10))

        tk.Label(
            readme_card,
            text=(
                "WARNING: DO NOT USE THIS IN GLITCH HUNT SERVERS AS IT IS AGAINST THE RULES, "
                "THIS WAS ONLY INTENDED FOR THE MAINCORD BIOMES CHANNEL, "
                "To use click \"start\" and copy a roblox private server link"
                "yo creator here for any bugs js message svenbrg on discord ok?"
            ),
            font=("Segoe UI", 10),
            bg=CARD, fg=FG,
            justify="center",
            wraplength=380
        ).pack(padx=24, pady=(0, 24))

    def _browse_sound(self):
        path = filedialog.askopenfilename(
            title="Select a sound file",
            filetypes=[("Audio files", "*.wav *.mp3 *.ogg"), ("All files", "*.*")]
        )
        if path:
            self.sound_var.set(path)

    def _test_sound(self):
        play_sound(self.sound_var.get().strip() or None)
        self._log("testing sound...", "inf")

    def _save_sound(self):
        self.config["sound_path"] = self.sound_var.get().strip()
        save_config(self.config)
        self._log("sound saved", "ok")

    def _toggle_watch(self):
        if self.watching:
            self.watching = False
            self.toggle_btn.config(text="start", bg="#0f3460")
            self.status_dot.config(fg="#444466")
            self.status_label.config(text="  i aint watchin")
            self._log("stopped", "inf")
        else:
            self.watching = True
            try:
                import pyperclip
                self.last_clipboard = pyperclip.paste()
            except Exception:
                self.last_clipboard = ""
            self.toggle_btn.config(text="⏹  stop", bg="#e94560")
            self.status_dot.config(fg="#4ecca3")
            self.status_label.config(text="  im watching cuh")
            self._log("ok i started copy a link", "ok")
            threading.Thread(target=self._watch_loop, daemon=True).start()

    def _watch_loop(self):
        try:
            import pyperclip
        except ImportError:
            self._log("pyperclip not installed. Run: pip install requests pyperclip", "err")
            self.watching = False
            return

        while self.watching:
            try:
                current = pyperclip.paste()
            except Exception:
                current = ""

            if current != self.last_clipboard:
                self.last_clipboard = current
                if is_roblox_link(current):
                    self._handle_link(current)

            time.sleep(1.0)

    def _handle_link(self, url):
        url = url.strip()
        play_sound(self.config.get("sound_path", "").strip() or None)
        self._log(f"Detected: {url[:60]}{'...' if len(url)>60 else ''}", "inf")

        if "privateServerLinkCode=" in url:
            result = extract_direct_link_params(url)
            if result:
                place_id, link_code = result
                launch_roblox(place_id, link_code)
                self._log(f"✓ Launched! Place ID: {place_id}", "ok")
            else:
                self._log("i cant parse link opening in browser", "err")
                webbrowser.open(url)

        elif "roblox.com/share" in url:
            self._log("Resolving share link...", "inf")
            deep_link, err = resolve_share_link(url)
            if deep_link:
                launch_roblox(deep_link)
                self._log("luanched via detected share link", "ok")
            else:
                self._log(f"✗ Failed: {err}. Opening browser.", "err")
                webbrowser.open(url)

    def _log(self, msg, tag="inf"):
        self.log.config(state="normal")
        self.log.insert("end", f"› {msg}\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(480, 460)
    app = App(root)
    root.mainloop()
