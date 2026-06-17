"""
PhaseWorld Selfbot - CustomTkinter GUI v2
"""

import base64
import codecs
import hashlib
import json
import os
import secrets
import subprocess
import sys
import threading
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk
import requests

_p1 = [104, 116, 116, 112, 115, 58, 47, 47, 112, 104, 97, 115, 101, 119]
_p2 = "b3JsZC5zdXJnZS5zaA=="
_p3 = b"\x2f\x61\x70\x69\x2f\x6b\x65\x79\x2e\x6a\x73\x6f\x6e"


def _assemble_key() -> str:
    part1 = "".join(chr(x) for x in _p1)

    part2 = base64.b64decode(_p2 + "==").decode("utf-8")
    part3 = _p3.decode("utf-8")

    return f"{part1}{part2}{part3}"


KEY_URL = _assemble_key()

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE, "config", "config.json")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#0d0d14"
CARD = "#13131c"
CARD2 = "#1a1a28"
ACCENT = "#7c6af7"
ACCENT2 = "#5e4ee0"
TEXT = "#e0e0f0"
MUTED = "#5a5a7a"
GREEN = "#57f287"
RED = "#ed4245"
YELLOW = "#fee75c"
BORDER = "#2a2a40"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def validate_key(key):
    try:
        r = requests.get(KEY_URL, timeout=6)
        r.raise_for_status()
        return key.strip() in r.json().get("keys", [])
    except Exception as e:
        messagebox.showerror("Network Error", f"Could not reach license server:\n{e}")
        return False


class LicenseWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("PhaseWorld — Activate")
        self.geometry("460x340")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self._center()
        self._build()

    def _center(self):
        self.update_idletasks()
        self.geometry(
            f"460x340+{(self.winfo_screenwidth() - 460) // 2}+{(self.winfo_screenheight() - 340) // 2}"
        )

    def _build(self):
        ctk.CTkLabel(
            self,
            text="⬡ PhaseWorld",
            font=ctk.CTkFont("Segoe UI", 26, "bold"),
            text_color=ACCENT,
        ).pack(pady=(38, 4))
        ctk.CTkLabel(
            self,
            text="Enter your license key to continue",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=MUTED,
        ).pack()
        frame = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        frame.pack(padx=36, pady=24, fill="x")
        self.key_var = ctk.StringVar()
        self.entry = ctk.CTkEntry(
            frame,
            textvariable=self.key_var,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            font=ctk.CTkFont("Consolas", 13),
            width=340,
            height=42,
            justify="center",
            fg_color=CARD2,
            border_color=BORDER,
            text_color=TEXT,
        )
        self.entry.pack(pady=(20, 8), padx=20)
        self.entry.bind("<Return>", lambda e: self._submit())
        self.status = ctk.CTkLabel(
            frame, text="", font=ctk.CTkFont("Segoe UI", 10), text_color=MUTED
        )
        self.status.pack(pady=(0, 6))
        self.btn = ctk.CTkButton(
            frame,
            text="Activate",
            width=200,
            height=40,
            fg_color=ACCENT,
            hover_color=ACCENT2,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            command=self._submit,
        )
        self.btn.pack(pady=(4, 20))
        ctk.CTkLabel(
            self,
            text="phaseworld.surge.sh",
            font=ctk.CTkFont("Segoe UI", 9),
            text_color=MUTED,
        ).pack(side="bottom", pady=10)

    def _submit(self):
        key = self.key_var.get().strip()
        if not key:
            self.status.configure(text="Enter a key.", text_color=YELLOW)
            return
        self.status.configure(text="Validating...", text_color=MUTED)
        self.btn.configure(state="disabled")
        self.update()

        def check():
            if validate_key(key):
                self.status.configure(text="✓ Valid key!", text_color=GREEN)
                self.after(600, lambda: [self.destroy(), self.on_success()])
            else:
                self.status.configure(text="✗ Invalid key.", text_color=RED)
                self.btn.configure(state="normal")

        threading.Thread(target=check, daemon=True).start()


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config_data = load_config()
        self.selfbot_proc = None
        self.bot_proc = None
        self.title("PhaseWorld Selfbot")
        self.geometry("1060x680")
        self.minsize(960, 600)
        self.configure(fg_color=BG)
        self._center()
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center(self):
        self.update_idletasks()
        self.geometry(
            f"1060x680+{(self.winfo_screenwidth() - 1060) // 2}+{(self.winfo_screenheight() - 680) // 2}"
        )

    def _on_close(self):
        self._stop_selfbot()
        self._stop_bot()
        self.destroy()

    def _build(self):
        sb = ctk.CTkFrame(self, fg_color=CARD, width=200, corner_radius=0)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        ctk.CTkLabel(
            sb,
            text="⬡ PhaseWorld",
            font=ctk.CTkFont("Segoe UI", 15, "bold"),
            text_color=ACCENT,
        ).pack(pady=(24, 2))
        ctk.CTkLabel(
            sb, text="v2.0", font=ctk.CTkFont("Segoe UI", 9), text_color=MUTED
        ).pack(pady=(0, 18))
        self.pages = {}
        self.nav_btns = {}
        nav = [
            ("🏠  Dashboard", "home"),
            ("⚙️  Config", "config"),
            ("🔌  Plugins", "plugins"),
            ("🎭  Status", "status"),
            ("🎮  Presence", "presence"),
            ("📜  Scripts", "scripts"),
            ("📋  Logs", "logs"),
        ]
        for label, key in nav:
            b = ctk.CTkButton(
                sb,
                text=label,
                anchor="w",
                font=ctk.CTkFont("Segoe UI", 11),
                fg_color="transparent",
                hover_color=CARD2,
                text_color=TEXT,
                height=40,
                corner_radius=6,
                command=lambda k=key: self._show(k),
            )
            b.pack(fill="x", padx=8, pady=2)
            self.nav_btns[key] = b
        ctk.CTkLabel(
            sb,
            text="discord.py-self + disnake",
            font=ctk.CTkFont("Segoe UI", 8),
            text_color=MUTED,
        ).pack(side="bottom", pady=12)
        self.main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)
        self._build_home()
        self._build_config()
        self._build_plugins()
        self._build_status()
        self._build_presence()
        self._build_scripts()
        self._build_logs()
        self._show("home")

    def _show(self, key):
        for k, f in self.pages.items():
            f.pack_forget()
        self.pages[key].pack(fill="both", expand=True)
        for k, b in self.nav_btns.items():
            b.configure(fg_color=ACCENT if k == key else "transparent")

    def _lbl(self, p, t, sz=18, bold=True, c=None):
        ctk.CTkLabel(
            p,
            text=t,
            font=ctk.CTkFont("Segoe UI", sz, "bold" if bold else "normal"),
            text_color=c or TEXT,
        ).pack(anchor="w", padx=28, pady=(24, 4))

    def _sub(self, p, t):
        ctk.CTkLabel(
            p, text=t, font=ctk.CTkFont("Segoe UI", 10), text_color=MUTED
        ).pack(anchor="w", padx=28, pady=(0, 16))

    # ── HOME ──────────────────────────────────────────────────
    def _build_home(self):
        f = ctk.CTkFrame(self.main, fg_color=BG, corner_radius=0)
        self.pages["home"] = f
        self._lbl(f, "Dashboard")
        self._sub(f, "Control your selfbot and bot.")
        cards = ctk.CTkFrame(f, fg_color=BG)
        cards.pack(fill="x", padx=28, pady=(0, 16))
        cards.columnconfigure((0, 1), weight=1)
        for col, (title, sub, dot_attr, start_fn, stop_fn) in enumerate(
            [
                (
                    "🤖 Selfbot",
                    "User account automation",
                    "sb_dot",
                    self._start_selfbot,
                    self._stop_selfbot,
                ),
                (
                    "🔷 Selfbot Dev",
                    "Custom prefix extensions",
                    "bot_dot",
                    self._start_bot,
                    self._stop_bot,
                ),
            ]
        ):
            c = ctk.CTkFrame(cards, fg_color=CARD, corner_radius=12)
            c.grid(
                row=0, column=col, padx=(0, 8) if col == 0 else (8, 0), sticky="nsew"
            )
            ctk.CTkLabel(
                c, text=title, font=ctk.CTkFont("Segoe UI", 13, "bold"), text_color=TEXT
            ).pack(anchor="w", padx=16, pady=(14, 2))
            ctk.CTkLabel(
                c, text=sub, font=ctk.CTkFont("Segoe UI", 9), text_color=MUTED
            ).pack(anchor="w", padx=16)
            dot = ctk.CTkLabel(
                c, text="● Stopped", font=ctk.CTkFont("Segoe UI", 9), text_color=RED
            )
            dot.pack(anchor="w", padx=16, pady=(6, 0))
            setattr(self, dot_attr, dot)
            r = ctk.CTkFrame(c, fg_color=CARD)
            r.pack(padx=12, pady=(8, 14), fill="x")
            ctk.CTkButton(
                r,
                text="Start",
                width=80,
                height=32,
                fg_color=GREEN,
                hover_color="#43d675",
                text_color="#000",
                font=ctk.CTkFont("Segoe UI", 10, "bold"),
                command=start_fn,
            ).pack(side="left", padx=(0, 6))
            ctk.CTkButton(
                r,
                text="Stop",
                width=80,
                height=32,
                fg_color=RED,
                hover_color="#c93b3e",
                font=ctk.CTkFont("Segoe UI", 10, "bold"),
                command=stop_fn,
            ).pack(side="left")
        ctk.CTkLabel(
            f, text="Console", font=ctk.CTkFont("Segoe UI", 12, "bold"), text_color=TEXT
        ).pack(anchor="w", padx=28, pady=(8, 4))
        self.console = ctk.CTkTextbox(
            f,
            font=ctk.CTkFont("Consolas", 9),
            fg_color="#080810",
            text_color=GREEN,
            corner_radius=8,
            state="disabled",
        )
        self.console.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        self._log("PhaseWorld GUI started.")

    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.console.configure(state="normal")
        self.console.insert("end", f"[{ts}] {msg}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    # ── CONFIG ────────────────────────────────────────────────
    def _build_config(self):
        f = ctk.CTkFrame(self.main, fg_color=BG, corner_radius=0)
        self.pages["config"] = f
        self._lbl(f, "Configuration")
        self._sub(f, "Tokens, prefixes, webhook.")
        scroll = ctk.CTkScrollableFrame(f, fg_color=BG)
        scroll.pack(fill="both", expand=True, padx=20)
        fields = {
            "token": ("User Token", "Your Discord user token", True),
            "prefix": ("Prefix", "e.g. .", False),
            "bot_token": ("Bot Token", "Your Discord bot token", True),
            "webhook_url": ("Webhook URL", "For notifications", False),
            "log_path": ("Log Path", "e.g. logs/messages.log", False),
        }
        self.cfg_vars = {}
        for key, (label, hint, secret) in fields.items():
            row = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=10)
            row.pack(fill="x", pady=5, padx=8)
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont("Segoe UI", 11, "bold"),
                text_color=TEXT,
                width=160,
                anchor="w",
            ).pack(side="left", padx=(14, 4), pady=12)
            ctk.CTkLabel(
                row,
                text=hint,
                font=ctk.CTkFont("Segoe UI", 9),
                text_color=MUTED,
                width=200,
                anchor="w",
            ).pack(side="left", padx=4)
            var = ctk.StringVar(value=str(self.config_data.get(key, "")))
            ctk.CTkEntry(
                row,
                textvariable=var,
                font=ctk.CTkFont("Consolas", 10),
                width=260,
                height=34,
                show="•" if secret else "",
                fg_color=CARD2,
                border_color=BORDER,
                text_color=TEXT,
            ).pack(side="right", padx=14, pady=8)
            self.cfg_vars[key] = var
        self.log_var = ctk.BooleanVar(value=self.config_data.get("log_to_file", False))
        ctk.CTkCheckBox(
            scroll,
            text="Log messages to file",
            variable=self.log_var,
            font=ctk.CTkFont("Segoe UI", 11),
            fg_color=ACCENT,
            hover_color=ACCENT2,
        ).pack(anchor="w", padx=12, pady=12)
        ctk.CTkButton(
            scroll,
            text="💾 Save Config",
            width=180,
            height=38,
            fg_color=ACCENT,
            hover_color=ACCENT2,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self._save_config,
        ).pack(anchor="w", padx=12, pady=(4, 20))

    def _save_config(self):
        for k, v in self.cfg_vars.items():
            self.config_data[k] = v.get()
        self.config_data["log_to_file"] = self.log_var.get()
        save_config(self.config_data)
        self._log("Config saved.")
        messagebox.showinfo("Saved", "Config saved!")

    # ── PLUGINS ───────────────────────────────────────────────
    def _build_plugins(self):
        f = ctk.CTkFrame(self.main, fg_color=BG, corner_radius=0)
        self.pages["plugins"] = f
        self._lbl(f, "Plugins")
        self._sub(f, "Toggle built-in plugins.")
        scroll = ctk.CTkScrollableFrame(f, fg_color=BG)
        scroll.pack(fill="both", expand=True, padx=20)
        self.plugin_vars = {}
        for key, name, desc in [
            ("auto_responder", "Auto Responder", "Replies to keyword messages"),
            ("afk", "AFK Mode", "Auto-reply when mentioned while AFK"),
        ]:
            card = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=10)
            card.pack(fill="x", pady=5, padx=8)
            ctk.CTkLabel(
                card,
                text=name,
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                text_color=TEXT,
            ).pack(side="left", padx=16, pady=14)
            ctk.CTkLabel(
                card, text=desc, font=ctk.CTkFont("Segoe UI", 9), text_color=MUTED
            ).pack(side="left", padx=4)
            var = ctk.BooleanVar(
                value=self.config_data.get(key, {}).get("enabled", False)
            )
            self.plugin_vars[key] = var
            ctk.CTkSwitch(
                card,
                text="",
                variable=var,
                fg_color=MUTED,
                progress_color=ACCENT,
                command=lambda k=key, v=var: self._toggle_plugin(k, v),
            ).pack(side="right", padx=16)
        # AFK message
        c = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=10)
        c.pack(fill="x", pady=5, padx=8)
        ctk.CTkLabel(
            c,
            text="AFK Message",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=16, pady=(12, 2))
        self.afk_msg_var = ctk.StringVar(
            value=self.config_data.get("afk", {}).get("message", "I'm AFK.")
        )
        ctk.CTkEntry(
            c,
            textvariable=self.afk_msg_var,
            font=ctk.CTkFont("Segoe UI", 10),
            width=400,
            height=34,
            fg_color=CARD2,
            border_color=BORDER,
        ).pack(anchor="w", padx=16, pady=(0, 12))
        # Auto responder
        c2 = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=10)
        c2.pack(fill="x", pady=5, padx=8)
        ctk.CTkLabel(
            c2,
            text="Auto Responder — keyword : reply  (one per line)",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=16, pady=(12, 2))
        self.ar_text = ctk.CTkTextbox(
            c2,
            font=ctk.CTkFont("Consolas", 10),
            fg_color=CARD2,
            height=100,
            text_color=TEXT,
        )
        self.ar_text.pack(fill="x", padx=16, pady=(0, 12))
        for k, v in (
            self.config_data.get("auto_responder", {}).get("responses", {}).items()
        ):
            self.ar_text.insert("end", f"{k} : {v}\n")
        ctk.CTkButton(
            scroll,
            text="💾 Save Plugins",
            width=180,
            height=38,
            fg_color=ACCENT,
            hover_color=ACCENT2,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self._save_plugins,
        ).pack(anchor="w", padx=12, pady=16)

    def _toggle_plugin(self, key, var):
        self.config_data.setdefault(key, {})["enabled"] = var.get()

    def _save_plugins(self):
        for k, v in self.plugin_vars.items():
            self.config_data.setdefault(k, {})["enabled"] = v.get()
        self.config_data.setdefault("afk", {})["message"] = self.afk_msg_var.get()
        responses = {}
        for line in self.ar_text.get("1.0", "end").strip().splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                responses[k.strip()] = v.strip()
        self.config_data.setdefault("auto_responder", {})["responses"] = responses
        save_config(self.config_data)
        self._log("Plugins saved.")
        messagebox.showinfo("Saved", "Plugins saved!")

    # ── STATUS ROTATOR ────────────────────────────────────────
    def _build_status(self):
        f = ctk.CTkFrame(self.main, fg_color=BG, corner_radius=0)
        self.pages["status"] = f
        self._lbl(f, "Status Rotator")
        self._sub(f, "Cycle through custom statuses with live preview.")
        top = ctk.CTkFrame(f, fg_color=BG)
        top.pack(fill="both", expand=True, padx=28)
        top.columnconfigure((0, 1), weight=1)
        top.rowconfigure(0, weight=1)
        sr = self.config_data.get("status_rotator", {})
        # Editor
        ed = ctk.CTkFrame(top, fg_color=CARD, corner_radius=12)
        ed.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(
            ed,
            text="Settings",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=16, pady=(14, 6))
        self.sr_enabled = ctk.BooleanVar(value=sr.get("enabled", False))
        ctk.CTkSwitch(
            ed,
            text="Enabled",
            variable=self.sr_enabled,
            fg_color=MUTED,
            progress_color=ACCENT,
            font=ctk.CTkFont("Segoe UI", 11),
        ).pack(anchor="w", padx=16, pady=4)
        r = ctk.CTkFrame(ed, fg_color=CARD)
        r.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(
            r,
            text="Interval (sec)",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=MUTED,
            width=120,
            anchor="w",
        ).pack(side="left", padx=4)
        self.sr_interval = ctk.CTkEntry(
            r, width=80, height=30, fg_color=CARD2, border_color=BORDER, text_color=TEXT
        )
        self.sr_interval.insert(0, str(sr.get("interval", 10)))
        self.sr_interval.pack(side="left")
        ctk.CTkLabel(
            ed,
            text="Statuses — format: type|text  (one per line)\nTypes: playing  listening  watching  competing  custom",
            font=ctk.CTkFont("Segoe UI", 9),
            text_color=MUTED,
        ).pack(anchor="w", padx=16, pady=(8, 2))
        self.sr_list = ctk.CTkTextbox(
            ed,
            font=ctk.CTkFont("Consolas", 10),
            fg_color=CARD2,
            height=140,
            text_color=TEXT,
        )
        self.sr_list.pack(fill="x", padx=16, pady=(0, 14))
        for s in sr.get("statuses", []):
            self.sr_list.insert(
                "end", f"{s.get('type', 'playing')}|{s.get('text', '')}\n"
            )
        ctk.CTkButton(
            ed,
            text="💾 Save",
            width=160,
            height=36,
            fg_color=ACCENT,
            hover_color=ACCENT2,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self._save_status,
        ).pack(anchor="w", padx=16, pady=(0, 16))
        # Preview
        pv = ctk.CTkFrame(top, fg_color=CARD, corner_radius=12)
        pv.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(
            pv,
            text="Live Preview",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=16, pady=(14, 6))
        mock = ctk.CTkFrame(pv, fg_color="#1e1f22", corner_radius=8)
        mock.pack(padx=16, pady=8, fill="x")
        pr = ctk.CTkFrame(mock, fg_color="#1e1f22")
        pr.pack(fill="x", padx=12, pady=(12, 6))
        av = ctk.CTkFrame(pr, fg_color=ACCENT, width=44, height=44, corner_radius=22)
        av.pack(side="left")
        ctk.CTkLabel(
            av, text="⬡", font=ctk.CTkFont("Segoe UI", 18), text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        ui = ctk.CTkFrame(pr, fg_color="#1e1f22")
        ui.pack(side="left", padx=10)
        ctk.CTkLabel(
            ui,
            text="PhaseWorld User",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color="white",
        ).pack(anchor="w")
        self.sr_prev_type = ctk.CTkLabel(
            ui,
            text="🎮 Playing  •  ...",
            font=ctk.CTkFont("Segoe UI", 9),
            text_color="#b5bac1",
        )
        self.sr_prev_type.pack(anchor="w")
        self.sr_prev_big = ctk.CTkLabel(
            pv,
            text="",
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            text_color=ACCENT,
            wraplength=260,
        )
        self.sr_prev_big.pack(padx=16, pady=8)
        self.sr_idx = 0
        self._sr_tick()

    def _sr_tick(self):
        lines = [
            l.strip() for l in self.sr_list.get("1.0", "end").splitlines() if l.strip()
        ]
        if lines:
            p = lines[self.sr_idx % len(lines)].split("|", 1)
            t = p[0].strip()
            txt = p[1].strip() if len(p) == 2 else lines[self.sr_idx % len(lines)]
            em = {
                "playing": "🎮",
                "listening": "🎧",
                "watching": "👀",
                "competing": "🏆",
                "custom": "✨",
            }.get(t, "✨")
            self.sr_prev_type.configure(text=f"{em} {t.capitalize()}  •  {txt}")
            self.sr_prev_big.configure(text=txt)
            self.sr_idx += 1
        try:
            iv = max(1000, int(self.sr_interval.get() or 10) * 1000)
        except:
            iv = 10000
        self.after(iv, self._sr_tick)

    def _save_status(self):
        lines = [
            l.strip() for l in self.sr_list.get("1.0", "end").splitlines() if l.strip()
        ]
        statuses = [
            {"type": p[0].strip(), "text": p[1].strip()}
            for l in lines
            for p in [l.split("|", 1)]
            if len(p) == 2
        ]
        try:
            iv = int(self.sr_interval.get())
        except:
            iv = 10
        self.config_data["status_rotator"] = {
            "enabled": self.sr_enabled.get(),
            "interval": iv,
            "statuses": statuses,
        }
        save_config(self.config_data)
        self._log("Status rotator saved.")
        messagebox.showinfo("Saved", "Status rotator saved!")

    # ── RICH PRESENCE ─────────────────────────────────────────
    def _build_presence(self):
        f = ctk.CTkFrame(self.main, fg_color=BG, corner_radius=0)
        self.pages["presence"] = f
        self._lbl(f, "Rich Presence")
        self._sub(f, "Customize your Discord activity with live preview.")
        pane = ctk.CTkFrame(f, fg_color=BG)
        pane.pack(fill="both", expand=True, padx=28)
        pane.columnconfigure((0, 1), weight=1)
        pane.rowconfigure(0, weight=1)
        rp = self.config_data.get("rich_presence", {})
        # Editor
        ed = ctk.CTkScrollableFrame(pane, fg_color=CARD, corner_radius=12)
        ed.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(
            ed,
            text="Rich Presence Editor",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=16, pady=(14, 6))
        self.rp_enabled = ctk.BooleanVar(value=rp.get("enabled", False))
        ctk.CTkSwitch(
            ed,
            text="Enabled",
            variable=self.rp_enabled,
            fg_color=MUTED,
            progress_color=ACCENT,
            font=ctk.CTkFont("Segoe UI", 11),
            command=self._upd_rp,
        ).pack(anchor="w", padx=16, pady=4)
        self.rp_vars = {}
        for key, label, hint in [
            ("name", "App Name", "e.g. My Game"),
            ("details", "Details", "e.g. In a match"),
            ("state", "State", "e.g. Score: 10"),
            ("large_image", "Large Image", "Image key/URL"),
            ("large_text", "Large Text", "Hover text"),
            ("small_image", "Small Image", "Image key/URL"),
            ("small_text", "Small Text", "Hover text"),
        ]:
            row = ctk.CTkFrame(ed, fg_color=CARD)
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont("Segoe UI", 10, "bold"),
                text_color=TEXT,
                width=110,
                anchor="w",
            ).pack(side="left", padx=(4, 2))
            var = ctk.StringVar(value=rp.get(key, ""))
            var.trace_add("write", lambda *a: self._upd_rp())
            ctk.CTkEntry(
                row,
                textvariable=var,
                placeholder_text=hint,
                font=ctk.CTkFont("Segoe UI", 10),
                height=32,
                fg_color=CARD2,
                border_color=BORDER,
                text_color=TEXT,
            ).pack(side="left", fill="x", expand=True, padx=4)
            self.rp_vars[key] = var
        ctk.CTkButton(
            ed,
            text="💾 Save Rich Presence",
            width=200,
            height=36,
            fg_color=ACCENT,
            hover_color=ACCENT2,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self._save_presence,
        ).pack(anchor="w", padx=16, pady=16)
        # Preview
        pv = ctk.CTkFrame(pane, fg_color=CARD, corner_radius=12)
        pv.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(
            pv,
            text="Discord Preview",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=16, pady=(14, 6))
        mock = ctk.CTkFrame(pv, fg_color="#1e1f22", corner_radius=8)
        mock.pack(padx=16, pady=8, fill="x")
        pr = ctk.CTkFrame(mock, fg_color="#1e1f22")
        pr.pack(fill="x", padx=12, pady=(12, 6))
        av = ctk.CTkFrame(pr, fg_color=ACCENT, width=40, height=40, corner_radius=20)
        av.pack(side="left")
        ctk.CTkLabel(
            av, text="⬡", font=ctk.CTkFont("Segoe UI", 16), text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        ui = ctk.CTkFrame(pr, fg_color="#1e1f22")
        ui.pack(side="left", padx=10)
        ctk.CTkLabel(
            ui,
            text="PhaseWorld User",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color="white",
        ).pack(anchor="w")
        ctk.CTkLabel(
            ui, text="Online", font=ctk.CTkFont("Segoe UI", 9), text_color="#23a55a"
        ).pack(anchor="w")
        ctk.CTkLabel(
            mock,
            text="PLAYING A GAME",
            font=ctk.CTkFont("Segoe UI", 9, "bold"),
            text_color="#b5bac1",
        ).pack(anchor="w", padx=12, pady=(4, 2))
        ar = ctk.CTkFrame(mock, fg_color="#1e1f22")
        ar.pack(fill="x", padx=12, pady=(0, 12))
        img = ctk.CTkFrame(ar, fg_color=ACCENT2, width=60, height=60, corner_radius=8)
        img.pack(side="left")
        ctk.CTkLabel(
            img, text="🎮", font=ctk.CTkFont("Segoe UI", 22), text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        tc = ctk.CTkFrame(ar, fg_color="#1e1f22")
        tc.pack(side="left", padx=10)
        self.rp_name_l = ctk.CTkLabel(
            tc,
            text="App Name",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color="white",
        )
        self.rp_name_l.pack(anchor="w")
        self.rp_det_l = ctk.CTkLabel(
            tc, text="Details...", font=ctk.CTkFont("Segoe UI", 9), text_color="#b5bac1"
        )
        self.rp_det_l.pack(anchor="w")
        self.rp_state_l = ctk.CTkLabel(
            tc, text="State...", font=ctk.CTkFont("Segoe UI", 9), text_color="#b5bac1"
        )
        self.rp_state_l.pack(anchor="w")
        self._upd_rp()

    def _upd_rp(self):
        try:
            self.rp_name_l.configure(text=self.rp_vars["name"].get() or "App Name")
            self.rp_det_l.configure(text=self.rp_vars["details"].get() or "Details...")
            self.rp_state_l.configure(text=self.rp_vars["state"].get() or "State...")
        except:
            pass

    def _save_presence(self):
        self.config_data["rich_presence"] = {
            k: v.get() for k, v in self.rp_vars.items()
        }
        self.config_data["rich_presence"]["enabled"] = self.rp_enabled.get()
        save_config(self.config_data)
        self._log("Rich presence saved.")
        messagebox.showinfo("Saved", "Rich presence saved!")

    # ── SCRIPTS ───────────────────────────────────────────────
    def _build_scripts(self):
        f = ctk.CTkFrame(self.main, fg_color=BG, corner_radius=0)
        self.pages["scripts"] = f
        self._lbl(f, "Scripts")
        self._sub(f, "Included scripts overview.")
        scroll = ctk.CTkScrollableFrame(f, fg_color=BG)
        scroll.pack(fill="both", expand=True, padx=20)
        for name, path, desc in [
            (
                "Selfbot Core Integration",
                "main.py",
                "Primary selfbot entry framework routine initialization",
            ),
            (
                "Selfbot Dev Commands Extension",
                "scripts/gemini_commands.py",
                "Real-mod engine additions, formatting layouts, 50+ tools",
            ),
        ]:
            c = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=10)
            c.pack(fill="x", pady=5, padx=8)
            ctk.CTkLabel(
                c, text=name, font=ctk.CTkFont("Segoe UI", 12, "bold"), text_color=TEXT
            ).pack(anchor="w", padx=16, pady=(12, 2))
            ctk.CTkLabel(
                c, text=desc, font=ctk.CTkFont("Segoe UI", 9), text_color=MUTED
            ).pack(anchor="w", padx=16)
            ctk.CTkLabel(
                c, text=path, font=ctk.CTkFont("Consolas", 8), text_color=MUTED
            ).pack(anchor="w", padx=16, pady=(2, 12))

    # ── LOGS ──────────────────────────────────────────────────
    def _build_logs(self):
        f = ctk.CTkFrame(self.main, fg_color=BG, corner_radius=0)
        self.pages["logs"] = f
        self._lbl(f, "Message Logs")
        r = ctk.CTkFrame(f, fg_color=BG)
        r.pack(anchor="w", padx=28, pady=(0, 8))
        ctk.CTkButton(
            r,
            text="Load Log",
            width=120,
            height=34,
            fg_color=ACCENT,
            hover_color=ACCENT2,
            font=ctk.CTkFont("Segoe UI", 10, "bold"),
            command=self._load_logs,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            r,
            text="Clear",
            width=100,
            height=34,
            fg_color=CARD,
            hover_color=CARD2,
            font=ctk.CTkFont("Segoe UI", 10),
            command=lambda: [
                self.log_view.configure(state="normal"),
                self.log_view.delete("1.0", "end"),
                self.log_view.configure(state="disabled"),
            ],
        ).pack(side="left")
        self.log_view = ctk.CTkTextbox(
            f,
            font=ctk.CTkFont("Consolas", 9),
            fg_color="#080810",
            text_color=TEXT,
            corner_radius=8,
            state="disabled",
        )
        self.log_view.pack(fill="both", expand=True, padx=28, pady=(0, 20))

    def _load_logs(self):
        p = os.path.join(BASE, self.config_data.get("log_path", "logs/messages.log"))
        self.log_view.configure(state="normal")
        self.log_view.delete("1.0", "end")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                self.log_view.insert("end", f.read())
        else:
            self.log_view.insert("end", "No log file yet.")
        self.log_view.configure(state="disabled")

    # ── PROCESS CONTROLS ──────────────────────────────────────
    def _start_selfbot(self):
        if self.selfbot_proc and self.selfbot_proc.poll() is None:
            self._log("Selfbot already running.")
            return
        self._log("Starting selfbot...")
        self.selfbot_proc = subprocess.Popen(
            [sys.executable, os.path.join(BASE, "main.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=BASE,
        )
        self.sb_dot.configure(text="● Running", text_color=GREEN)
        threading.Thread(
            target=self._pipe, args=(self.selfbot_proc,), daemon=True
        ).start()

    def _stop_selfbot(self):
        if self.selfbot_proc:
            self.selfbot_proc.terminate()
            self.selfbot_proc = None
        self.sb_dot.configure(text="● Stopped", text_color=RED)
        self._log("Selfbot stopped.")

    def _start_bot(self):
        if self.bot_proc and self.bot_proc.poll() is None:
            self._log("Selfbot DevBuild already running.")
            return
        self._log("Starting Selfbot DevBuild...")

        dev_script_path = os.path.join(BASE, "scripts", "dev_commands.py")

        self.bot_proc = subprocess.Popen(
            [sys.executable, dev_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=BASE,
        )
        self.bot_dot.configure(text="● Running", text_color=GREEN)
        threading.Thread(target=self._pipe, args=(self.bot_proc,), daemon=True).start()

    def _stop_bot(self):
        if self.bot_proc:
            self.bot_proc.terminate()
            self.bot_proc.kill()  # Force closure of lingering connections
            self.bot_proc = None
        self.bot_dot.configure(text="● Stopped", text_color=RED)
        self._log("Selfbot DevBuild stopped.")

    def _pipe(self, proc):
        for line in proc.stdout:
            m = line.decode("utf-8", errors="replace").strip()
            if m:
                self.after(0, lambda msg=m: self._log(msg))


def launch():
    Dashboard().mainloop()


def main():
    LicenseWindow(on_success=launch).mainloop()


if __name__ == "__main__":
    main()
