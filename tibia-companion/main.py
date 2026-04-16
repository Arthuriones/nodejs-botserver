"""
Combo Companion v2 - UI + WebSocket direto, sem leitura de memória.
Usa Elf Bot pra interagir com o jogo (2 hotkeys).
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
import time

from network import BotServerClient

CONFIG_FILE = "companion-config.json"

DEFAULT_CONFIG = {
    "server_url": "wss://SEU-APP.railway.app/",
    "channel": "1",
    "player_name": "",
    "leaders": [],
    "enemies": [],
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
    return {**DEFAULT_CONFIG}


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


class ComboCompanion:
    def __init__(self):
        self.config = load_config()
        self.ws = BotServerClient()

        self.combo_enabled = False
        self.connected_members = {}
        self.leader_target_name = ""

        self._build_ui()
        self._load_lists()

        if self.config["player_name"] and "SEU-APP" not in self.config["server_url"]:
            self.root.after(500, self._try_auto_connect)

        self.root.after(300, self._tick)

    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("Combo Companion v2.0")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)
        self.root.geometry("560x500")

        style = {"bg": "#1e1e1e", "fg": "#e0e0e0", "font": ("Consolas", 10)}
        style_title = {"bg": "#1e1e1e", "fg": "#66b3ff", "font": ("Consolas", 11, "bold")}
        style_btn = {"bg": "#333", "fg": "#e0e0e0", "font": ("Consolas", 9),
                     "activebackground": "#555", "activeforeground": "#fff",
                     "relief": "flat", "bd": 1}
        style_list = {"bg": "#2a2a2a", "fg": "#e0e0e0", "font": ("Consolas", 10),
                      "selectbackground": "#444", "selectforeground": "#fff",
                      "relief": "flat", "bd": 1}
        style_entry = {"bg": "#2a2a2a", "fg": "#e0e0e0", "font": ("Consolas", 10),
                       "insertbackground": "#e0e0e0", "relief": "flat", "bd": 1}

        # === TOP: Server status ===
        top = tk.Frame(self.root, bg="#1e1e1e")
        top.pack(fill="x", padx=10, pady=(10, 5))

        self.lbl_server = tk.Label(top, text="Server: OFF", fg="#ff6666", **{k: v for k, v in style.items() if k != 'fg'})
        self.lbl_server.pack(side="right")

        self.lbl_status = tk.Label(top, text="", **style)
        self.lbl_status.pack(side="left")

        # === Nome do char ===
        name_frame = tk.Frame(self.root, bg="#1e1e1e")
        name_frame.pack(fill="x", padx=10, pady=(0, 5))

        tk.Label(name_frame, text="Nome:", **style).pack(side="left")
        self.entry_name = tk.Entry(name_frame, width=18, **style_entry)
        self.entry_name.pack(side="left", padx=(5, 10))
        self.entry_name.insert(0, self.config.get("player_name", ""))

        tk.Label(name_frame, text="URL:", **style).pack(side="left")
        self.entry_url = tk.Entry(name_frame, width=25, **style_entry)
        self.entry_url.pack(side="left", padx=(5, 5))
        self.entry_url.insert(0, self.config["server_url"])

        self.btn_connect = tk.Button(name_frame, text="Conectar", width=9,
                                     command=self._on_connect, **style_btn)
        self.btn_connect.pack(side="left")

        # === Separador ===
        tk.Frame(self.root, bg="#444", height=1).pack(fill="x", padx=10, pady=5)

        # === Listas: Lideres | Conectados | Inimigos ===
        lists_frame = tk.Frame(self.root, bg="#1e1e1e")
        lists_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # -- Lideres --
        left = tk.Frame(lists_frame, bg="#1e1e1e")
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        tk.Label(left, text="Lideres", **style_title).pack()
        self.list_leaders = tk.Listbox(left, height=12, **style_list)
        self.list_leaders.pack(fill="both", expand=True, pady=(3, 3))

        btn_row_l = tk.Frame(left, bg="#1e1e1e")
        btn_row_l.pack(fill="x")
        tk.Button(btn_row_l, text="Remover", command=self._remove_leader, **style_btn).pack(side="right")

        # -- Conectados --
        center = tk.Frame(lists_frame, bg="#1e1e1e")
        center.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(center, text="Conectados", **style_title).pack()
        self.list_connected = tk.Listbox(center, height=12, **style_list)
        self.list_connected.pack(fill="both", expand=True, pady=(3, 3))

        btn_row_c = tk.Frame(center, bg="#1e1e1e")
        btn_row_c.pack(fill="x")
        tk.Button(btn_row_c, text="< Lider", command=self._add_leader_from_connected, **style_btn).pack(side="left")
        tk.Button(btn_row_c, text="Inimigo >", command=self._add_enemy_from_connected, **style_btn).pack(side="right")

        # -- Inimigos --
        right = tk.Frame(lists_frame, bg="#1e1e1e")
        right.pack(side="left", fill="both", expand=True, padx=(5, 0))

        tk.Label(right, text="Inimigos", **style_title).pack()
        self.list_enemies = tk.Listbox(right, height=12, **style_list)
        self.list_enemies.pack(fill="both", expand=True, pady=(3, 3))

        enemy_add_frame = tk.Frame(right, bg="#1e1e1e")
        enemy_add_frame.pack(fill="x", pady=(3, 0))
        self.entry_enemy = tk.Entry(enemy_add_frame, width=12, **style_entry)
        self.entry_enemy.pack(side="left", fill="x", expand=True)
        tk.Button(enemy_add_frame, text="+", width=3, command=self._add_enemy_manual,
                  **style_btn).pack(side="right", padx=(3, 0))

        btn_row_r = tk.Frame(right, bg="#1e1e1e")
        btn_row_r.pack(fill="x", pady=(3, 0))
        tk.Button(btn_row_r, text="Remover", command=self._remove_enemy, **style_btn).pack(side="right")

        # === Separador ===
        tk.Frame(self.root, bg="#444", height=1).pack(fill="x", padx=10, pady=5)

        # === Bottom: Combo toggle + alvo ===
        bottom = tk.Frame(self.root, bg="#1e1e1e")
        bottom.pack(fill="x", padx=10, pady=(0, 5))

        self.btn_toggle = tk.Button(bottom, text="COMBO OFF", width=15,
                                    bg="#552222", fg="#ff6666",
                                    font=("Consolas", 11, "bold"),
                                    activebackground="#663333",
                                    relief="flat", bd=1,
                                    command=self._toggle_combo)
        self.btn_toggle.pack(side="left")

        self.lbl_target = tk.Label(bottom, text="", fg="#ffcc00", bg="#1e1e1e",
                                   font=("Consolas", 10, "bold"))
        self.lbl_target.pack(side="right")

        # === Info hotkeys ===
        info_frame = tk.Frame(self.root, bg="#1e1e1e")
        info_frame.pack(fill="x", padx=10, pady=(0, 10))
        tk.Label(info_frame, text="ElfBot: attack $fileline.'bridge_target_in.txt'.1  |  filewrite bridge_target_out.txt $target.name",
                 bg="#1e1e1e", fg="#666", font=("Consolas", 8)).pack()

    # === List management ===

    def _load_lists(self):
        for name in self.config.get("leaders", []):
            self.list_leaders.insert(tk.END, name)
        for name in self.config.get("enemies", []):
            self.list_enemies.insert(tk.END, name)

    def _save_lists(self):
        self.config["leaders"] = list(self.list_leaders.get(0, tk.END))
        self.config["enemies"] = list(self.list_enemies.get(0, tk.END))
        save_config(self.config)

    def _add_leader_from_connected(self):
        sel = self.list_connected.curselection()
        if not sel:
            return
        name = self.list_connected.get(sel[0])
        if name not in list(self.list_leaders.get(0, tk.END)):
            self.list_leaders.insert(tk.END, name)
            self._save_lists()

    def _remove_leader(self):
        sel = self.list_leaders.curselection()
        if sel:
            self.list_leaders.delete(sel[0])
            self._save_lists()

    def _add_enemy_from_connected(self):
        sel = self.list_connected.curselection()
        if not sel:
            return
        name = self.list_connected.get(sel[0])
        if name not in list(self.list_enemies.get(0, tk.END)):
            self.list_enemies.insert(tk.END, name)
            self._save_lists()

    def _add_enemy_manual(self):
        name = self.entry_enemy.get().strip()
        if name and name not in list(self.list_enemies.get(0, tk.END)):
            self.list_enemies.insert(tk.END, name)
            self.entry_enemy.delete(0, tk.END)
            self._save_lists()

    def _remove_enemy(self):
        sel = self.list_enemies.curselection()
        if sel:
            self.list_enemies.delete(sel[0])
            self._save_lists()

    # === Connection ===

    def _on_connect(self):
        url = self.entry_url.get().strip()
        name = self.entry_name.get().strip()
        if not url or not name:
            messagebox.showwarning("Erro", "Preencha nome e URL")
            return

        self.config["server_url"] = url
        self.config["player_name"] = name
        save_config(self.config)

        self.ws.disconnect()
        self.ws.connect(url, name, self.config["channel"])

    def _try_auto_connect(self):
        name = self.config.get("player_name", "")
        url = self.config.get("server_url", "")
        if name and url:
            self.ws.connect(url, name, self.config["channel"])

    # === Combo toggle ===

    def _toggle_combo(self):
        self.combo_enabled = not self.combo_enabled
        if self.combo_enabled:
            self.btn_toggle.config(text="COMBO ON", bg="#225522", fg="#66ff66")
        else:
            self.btn_toggle.config(text="COMBO OFF", bg="#552222", fg="#ff6666")
            self.leader_target_name = ""
            # Limpa arquivo de alvo
            try:
                with open("bridge_target_in.txt", "w") as f:
                    f.write("")
            except:
                pass

    # === Main tick ===

    def _tick(self):
        self._tick_network()
        self._tick_file_bridge()
        self._tick_ui()
        self.root.after(300, self._tick)

    def _tick_network(self):
        if not self.ws.connected:
            return

        # Heartbeat
        if self.combo_enabled:
            self.ws.send("ComboMember", self.config.get("player_name", ""))

        # Processar mensagens
        for msg in self.ws.get_messages():
            if msg.get("type") != "message":
                continue

            topic = msg.get("topic", "")
            sender = msg.get("name", "")
            payload = msg.get("message")

            if topic == "ComboMember":
                self.connected_members[sender] = time.time()

            elif topic == "LeaderTarget":
                leaders = list(self.list_leaders.get(0, tk.END))
                if sender in leaders and self.combo_enabled:
                    if payload is None:
                        self.leader_target_name = ""
                    elif isinstance(payload, dict):
                        self.leader_target_name = payload.get("name", "")
                    elif isinstance(payload, str):
                        self.leader_target_name = payload

                    # Escreve alvo no arquivo pro Elf Bot ler
                    try:
                        with open("bridge_target_in.txt", "w") as f:
                            f.write(self.leader_target_name)
                    except:
                        pass

        # Limpa membros offline
        now = time.time()
        stale = [n for n, t in self.connected_members.items() if now - t > 10]
        for n in stale:
            del self.connected_members[n]

    def _tick_file_bridge(self):
        """Se eu sou lider, le o alvo do Elf Bot e envia pro time."""
        if not self.combo_enabled or not self.ws.connected:
            return

        leaders = list(self.list_leaders.get(0, tk.END))
        my_name = self.config.get("player_name", "")

        if my_name in leaders:
            try:
                with open("bridge_target_out.txt", "r") as f:
                    target = f.read().strip()
                if target:
                    if not hasattr(self, '_last_sent_target') or target != self._last_sent_target:
                        self.ws.send("LeaderTarget", target)
                        self._last_sent_target = target
            except FileNotFoundError:
                pass

    def _tick_ui(self):
        # Server status
        if self.ws.connected:
            self.lbl_server.config(text="Server: ON", fg="#66ff66")
            self.btn_connect.config(text="Reconectar")
        else:
            self.lbl_server.config(text="Server: OFF", fg="#ff6666")
            self.btn_connect.config(text="Conectar")

        # Alvo do lider
        if self.leader_target_name:
            self.lbl_target.config(text=f"Alvo: {self.leader_target_name}")
        else:
            self.lbl_target.config(text="")

        # Status
        n = len(self.connected_members)
        self.lbl_status.config(text=f"{n} online" if n > 0 else "")

        # Lista de conectados
        current = set(self.list_connected.get(0, tk.END))
        members = set(self.connected_members.keys())
        if current != members:
            self.list_connected.delete(0, tk.END)
            for name in sorted(members):
                self.list_connected.insert(tk.END, name)

    def run(self):
        self.root.mainloop()
        self.ws.disconnect()


def main():
    app = ComboCompanion()
    app.run()


if __name__ == "__main__":
    main()
