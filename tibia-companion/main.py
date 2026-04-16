"""
Combo Companion - App para sincronizar combo entre Tibia 8.6 (ElfBot) e OTC.
Lê memória do Tibia, conecta no BotServer via WebSocket, UI com tkinter.
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
import time
import ctypes

from memory import TibiaMemoryReader
from network import BotServerClient

CONFIG_FILE = "companion-config.json"

DEFAULT_CONFIG = {
    "server_url": "wss://SEU-APP.railway.app/",
    "channel": "1",
    "process_name": "Tibia.exe",
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
        self.reader = TibiaMemoryReader(process_name=self.config["process_name"])
        self.ws = BotServerClient()

        # Estado
        self.combo_enabled = False
        self.connected_members = {}  # name -> timestamp
        self.leader_target_name = ""
        self.leader_target_id = 0
        self.last_sent_target_id = 0

        self._build_ui()
        self._load_lists()

        # Se o config já tem server_url válido, tenta conectar
        if "SEU-APP" not in self.config["server_url"]:
            self.root.after(500, self._try_auto_connect)

        self.root.after(300, self._tick)

    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("Combo Companion v1.0")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)
        self.root.geometry("560x480")

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

        # === TOP: Status ===
        top = tk.Frame(self.root, bg="#1e1e1e")
        top.pack(fill="x", padx=10, pady=(10, 5))

        self.lbl_tibia = tk.Label(top, text="Tibia: --", **style)
        self.lbl_tibia.pack(side="left")

        self.lbl_server = tk.Label(top, text="Server: --", **style)
        self.lbl_server.pack(side="right")

        # === Status player ===
        player_frame = tk.Frame(self.root, bg="#1e1e1e")
        player_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.lbl_player = tk.Label(player_frame, text="Player: --", **style)
        self.lbl_player.pack(side="left")

        self.lbl_target = tk.Label(player_frame, text="Alvo: --", fg="#ff6666", bg="#1e1e1e",
                                   font=("Consolas", 10, "bold"))
        self.lbl_target.pack(side="right")

        # === Server URL ===
        url_frame = tk.Frame(self.root, bg="#1e1e1e")
        url_frame.pack(fill="x", padx=10, pady=(0, 5))

        tk.Label(url_frame, text="URL:", **style).pack(side="left")
        self.entry_url = tk.Entry(url_frame, width=38, **style_entry)
        self.entry_url.pack(side="left", padx=(5, 5))
        self.entry_url.insert(0, self.config["server_url"])

        self.btn_connect = tk.Button(url_frame, text="Conectar", width=10,
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
        self.list_leaders = tk.Listbox(left, height=10, **style_list)
        self.list_leaders.pack(fill="both", expand=True, pady=(3, 3))

        btn_row_l = tk.Frame(left, bg="#1e1e1e")
        btn_row_l.pack(fill="x")
        tk.Button(btn_row_l, text="Remover", command=self._remove_leader, **style_btn).pack(side="right")

        # -- Conectados --
        center = tk.Frame(lists_frame, bg="#1e1e1e")
        center.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(center, text="Conectados", **style_title).pack()
        self.list_connected = tk.Listbox(center, height=10, **style_list)
        self.list_connected.pack(fill="both", expand=True, pady=(3, 3))

        btn_row_c = tk.Frame(center, bg="#1e1e1e")
        btn_row_c.pack(fill="x")
        tk.Button(btn_row_c, text="< Lider", command=self._add_leader_from_connected, **style_btn).pack(side="left")
        tk.Button(btn_row_c, text="Inimigo >", command=self._add_enemy_from_connected, **style_btn).pack(side="right")

        # -- Inimigos --
        right = tk.Frame(lists_frame, bg="#1e1e1e")
        right.pack(side="left", fill="both", expand=True, padx=(5, 0))

        tk.Label(right, text="Inimigos", **style_title).pack()
        self.list_enemies = tk.Listbox(right, height=10, **style_list)
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

        # === Bottom: Toggle + Info ===
        tk.Frame(self.root, bg="#444", height=1).pack(fill="x", padx=10, pady=5)

        bottom = tk.Frame(self.root, bg="#1e1e1e")
        bottom.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_toggle = tk.Button(bottom, text="COMBO OFF", width=15,
                                    bg="#552222", fg="#ff6666",
                                    font=("Consolas", 11, "bold"),
                                    activebackground="#663333",
                                    relief="flat", bd=1,
                                    command=self._toggle_combo)
        self.btn_toggle.pack(side="left")

        self.lbl_combo_target = tk.Label(bottom, text="", fg="#ffcc00", bg="#1e1e1e",
                                         font=("Consolas", 10))
        self.lbl_combo_target.pack(side="right")

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
        current = list(self.list_leaders.get(0, tk.END))
        if name not in current:
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
        current = list(self.list_enemies.get(0, tk.END))
        if name not in current:
            self.list_enemies.insert(tk.END, name)
            self._save_lists()

    def _add_enemy_manual(self):
        name = self.entry_enemy.get().strip()
        if not name:
            return
        current = list(self.list_enemies.get(0, tk.END))
        if name not in current:
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
        if not url:
            return

        self.config["server_url"] = url
        save_config(self.config)

        if not self.reader.connected:
            self.reader.attach()

        name = self.reader.player_name or "Unknown"
        self.ws.connect(url, name, self.config["channel"])

    def _try_auto_connect(self):
        if self.reader.attach():
            name = self.reader.player_name
            if name:
                self.ws.connect(self.config["server_url"], name, self.config["channel"])

    # === Combo toggle ===

    def _toggle_combo(self):
        self.combo_enabled = not self.combo_enabled
        if self.combo_enabled:
            self.btn_toggle.config(text="COMBO ON", bg="#225522", fg="#66ff66")
        else:
            self.btn_toggle.config(text="COMBO OFF", bg="#552222", fg="#ff6666")

    # === Main tick (200ms) ===

    def _tick(self):
        self._tick_memory()
        self._tick_network()
        self._tick_combo()
        self._tick_ui()
        self.root.after(300, self._tick)

    def _tick_memory(self):
        """Atualiza leitura da memória do Tibia."""
        self.reader.update()

    def _tick_network(self):
        """Processa mensagens do BotServer."""
        # Heartbeat
        if self.ws.connected and self.reader.connected and self.combo_enabled:
            self.ws.send("ComboMember", self.reader.player_name)

            # MapInfo
            self.ws.send("MapInfo", {
                "name": self.reader.player_name,
                "position": {
                    "x": self.reader.player_x,
                    "y": self.reader.player_y,
                    "z": self.reader.player_z
                },
                "outfit": {}
            })

        # Processar mensagens recebidas
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
                if sender in leaders:
                    if payload is None:
                        self.leader_target_name = ""
                        self.leader_target_id = 0
                    elif isinstance(payload, dict):
                        self.leader_target_name = payload.get("name", "")
                        self.leader_target_id = payload.get("id", 0)
                    elif isinstance(payload, str):
                        self.leader_target_name = payload
                        self.leader_target_id = 0

        # Limpa membros offline (10s timeout)
        now = time.time()
        stale = [n for n, t in self.connected_members.items() if now - t > 10]
        for n in stale:
            del self.connected_members[n]

    def _tick_combo(self):
        """Lógica de combo: seguir líder e/ou enviar alvo."""
        if not self.combo_enabled or not self.reader.connected:
            return

        leaders = list(self.list_leaders.get(0, tk.END))
        is_leader = self.reader.player_name in leaders

        # === SE EU SOU LÍDER: enviar meu alvo pro time ===
        if is_leader:
            current_target = self.reader.target_id
            if current_target != self.last_sent_target_id:
                self.last_sent_target_id = current_target
                if current_target != 0:
                    creature = self.reader.find_creature_by_id(current_target)
                    if creature:
                        self.ws.send("LeaderTarget", {
                            "id": creature.id,
                            "name": creature.name
                        })
                else:
                    self.ws.send("LeaderTarget", None)

        # === SE EU SIGO UM LÍDER: atacar o alvo dele ===
        if self.leader_target_name and not is_leader:
            # Tenta achar o alvo na battle list
            target = None
            if self.leader_target_id:
                target = self.reader.find_creature_by_id(self.leader_target_id)
            if not target and self.leader_target_name:
                target = self.reader.find_creature_by_name(self.leader_target_name)

            if target and target.id != self.reader.target_id:
                self.reader.attack_creature(target.id)

    def _tick_ui(self):
        """Atualiza a interface."""
        # Status Tibia
        if self.reader.connected and self.reader.player_name:
            self.lbl_tibia.config(text="Tibia: ON", fg="#66ff66")
            self.lbl_player.config(
                text=f"Player: {self.reader.player_name} | "
                     f"HP: {self.reader.hp_percent()}% | "
                     f"MP: {self.reader.mp_percent()}%"
            )
        else:
            self.lbl_tibia.config(text="Tibia: OFF", fg="#ff6666")
            self.lbl_player.config(text="Player: --")

        # Status Server
        if self.ws.connected:
            self.lbl_server.config(text="Server: ON", fg="#66ff66")
        else:
            self.lbl_server.config(text="Server: OFF", fg="#ff6666")

        # Alvo atual
        target = self.reader.get_current_target()
        if target:
            self.lbl_target.config(text=f"Alvo: {target.name} ({target.hp}%)")
        else:
            self.lbl_target.config(text="Alvo: --")

        # Alvo do líder
        if self.leader_target_name:
            self.lbl_combo_target.config(text=f"Lider -> {self.leader_target_name}")
        else:
            self.lbl_combo_target.config(text="")

        # Lista de conectados
        current_in_list = set(self.list_connected.get(0, tk.END))
        current_members = set(self.connected_members.keys())

        if current_in_list != current_members:
            self.list_connected.delete(0, tk.END)
            for name in sorted(current_members):
                self.list_connected.insert(tk.END, name)

    def run(self):
        self.root.mainloop()
        self.ws.disconnect()
        self.reader.detach()


def main():
    app = ComboCompanion()
    app.run()


if __name__ == "__main__":
    main()
