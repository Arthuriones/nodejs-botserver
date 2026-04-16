"""
Combo Companion v3 - Combo + NavPotion + MapInfo
Sincroniza Tibia 8.6 (ElfBot) com OTC via BotServer.
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
import time
import ctypes

from network import BotServerClient

PLACEHOLDER = b"__COMBO__________________________"  # 30 chars
POT_PLACEHOLDER = b"__POT____________________________"  # 30 chars

CONFIG_FILE = "companion-config.json"

DEFAULT_CONFIG = {
    "server_url": "wss://SEU-APP.railway.app/",
    "channel": "1",
    "player_name": "",
    "elfbot_path": "",
    "my_voc": "EK",
    "mp_request_percent": 50,
    "mp_request_enabled": False,
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
        self._last_sent_target = ""
        self._last_pos = ""
        self._last_mp = 100
        self._pot_target = ""
        self._log_truncate_timer = 0

        self._build_ui()
        self._load_lists()
        self._init_memory_bridge()

        if self.config["player_name"] and "SEU-APP" not in self.config["server_url"]:
            self.root.after(500, self._try_auto_connect)

        self.root.after(300, self._tick)

    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("Combo Companion v3.0")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)
        self.root.geometry("560x560")

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

        self.lbl_server = tk.Label(top, text="Server: OFF", fg="#ff6666",
                                   bg="#1e1e1e", font=("Consolas", 10))
        self.lbl_server.pack(side="right")

        self.lbl_status = tk.Label(top, text="", **style)
        self.lbl_status.pack(side="left")

        # === Nome + URL ===
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

        tk.Frame(self.root, bg="#444", height=1).pack(fill="x", padx=10, pady=5)

        # === Listas ===
        lists_frame = tk.Frame(self.root, bg="#1e1e1e")
        lists_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Lideres
        left = tk.Frame(lists_frame, bg="#1e1e1e")
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tk.Label(left, text="Lideres", **style_title).pack()
        self.list_leaders = tk.Listbox(left, height=10, **style_list)
        self.list_leaders.pack(fill="both", expand=True, pady=(3, 3))
        btn_l = tk.Frame(left, bg="#1e1e1e")
        btn_l.pack(fill="x")
        tk.Button(btn_l, text="Remover", command=self._remove_leader, **style_btn).pack(side="right")

        # Conectados
        center = tk.Frame(lists_frame, bg="#1e1e1e")
        center.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(center, text="Conectados", **style_title).pack()
        self.list_connected = tk.Listbox(center, height=10, **style_list)
        self.list_connected.pack(fill="both", expand=True, pady=(3, 3))
        btn_c = tk.Frame(center, bg="#1e1e1e")
        btn_c.pack(fill="x")
        tk.Button(btn_c, text="< Lider", command=self._add_leader_from_connected, **style_btn).pack(side="left")
        tk.Button(btn_c, text="Inimigo >", command=self._add_enemy_from_connected, **style_btn).pack(side="right")

        # Inimigos
        right = tk.Frame(lists_frame, bg="#1e1e1e")
        right.pack(side="left", fill="both", expand=True, padx=(5, 0))
        tk.Label(right, text="Inimigos", **style_title).pack()
        self.list_enemies = tk.Listbox(right, height=10, **style_list)
        self.list_enemies.pack(fill="both", expand=True, pady=(3, 3))
        enemy_add = tk.Frame(right, bg="#1e1e1e")
        enemy_add.pack(fill="x", pady=(3, 0))
        self.entry_enemy = tk.Entry(enemy_add, width=12, **style_entry)
        self.entry_enemy.pack(side="left", fill="x", expand=True)
        tk.Button(enemy_add, text="+", width=3, command=self._add_enemy_manual, **style_btn).pack(side="right", padx=(3, 0))
        btn_r = tk.Frame(right, bg="#1e1e1e")
        btn_r.pack(fill="x", pady=(3, 0))
        tk.Button(btn_r, text="Remover", command=self._remove_enemy, **style_btn).pack(side="right")

        tk.Frame(self.root, bg="#444", height=1).pack(fill="x", padx=10, pady=5)

        # === Vocacao + Pot config ===
        voc_frame = tk.Frame(self.root, bg="#1e1e1e")
        voc_frame.pack(fill="x", padx=10, pady=(0, 5))

        tk.Label(voc_frame, text="Voc:", **style).pack(side="left")
        self.voc_var = tk.StringVar(value=self.config.get("my_voc", "EK"))
        for v in ["EK", "ED", "MS", "RP"]:
            tk.Radiobutton(voc_frame, text=v, variable=self.voc_var, value=v,
                          bg="#1e1e1e", fg="#e0e0e0", selectcolor="#333",
                          activebackground="#1e1e1e", activeforeground="#66b3ff",
                          font=("Consolas", 9),
                          command=self._save_voc).pack(side="left", padx=2)

        tk.Label(voc_frame, text="  |", **style).pack(side="left")

        self.mp_request_var = tk.BooleanVar(value=self.config.get("mp_request_enabled", False))
        tk.Checkbutton(voc_frame, text="Pedir Mana", variable=self.mp_request_var,
                      bg="#1e1e1e", fg="#e0e0e0", selectcolor="#333",
                      activebackground="#1e1e1e", font=("Consolas", 9),
                      command=self._save_voc).pack(side="left", padx=5)

        tk.Frame(self.root, bg="#444", height=1).pack(fill="x", padx=10, pady=5)

        # === Bottom: Combo + alvo ===
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

        # === Info ===
        info = tk.Frame(self.root, bg="#1e1e1e")
        info.pack(fill="x", padx=10, pady=(0, 10))
        tk.Label(info, text="Persistent: auto 500 | exec attack __COMBO__...  +  auto 500 | exec log ATK:$attacked.name",
                 bg="#1e1e1e", fg="#555", font=("Consolas", 7)).pack()
        tk.Label(info, text="+ auto 1000 | exec log POS:$posx:$posy:$posz  +  auto 1000 | exec log MP:$mppc",
                 bg="#1e1e1e", fg="#555", font=("Consolas", 7)).pack()

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

    def _save_voc(self):
        self.config["my_voc"] = self.voc_var.get()
        self.config["mp_request_enabled"] = self.mp_request_var.get()
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

    # === Memory bridge ===

    def _init_memory_bridge(self):
        self._mem_handle = None
        self._mem_addrs = []
        self._pot_mem_addrs = []
        self._current_mem_target = ""

        try:
            import pymem
            pm = pymem.Pymem("pbotwars.exe")
            self._mem_handle = pm.process_handle
            print(f"[MEM] Conectado ao pbotwars (PID {pm.process_id})", flush=True)

            self._mem_addrs = self._scan_memory(pm, PLACEHOLDER, "COMBO")
            self._pot_mem_addrs = self._scan_memory(pm, POT_PLACEHOLDER, "POT")

        except Exception as e:
            print(f"[MEM] Erro: {type(e).__name__}: {e}", flush=True)

    def _scan_memory(self, pm, pattern, label):
        kernel32 = ctypes.windll.kernel32

        class MBI(ctypes.Structure):
            _fields_ = [
                ("BaseAddress", ctypes.c_void_p),
                ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", ctypes.c_ulong),
                ("RegionSize", ctypes.c_size_t),
                ("State", ctypes.c_ulong),
                ("Protect", ctypes.c_ulong),
                ("Type", ctypes.c_ulong),
            ]

        mbi = MBI()
        address = 0x10000
        found = []

        while address < 0x7FFFFFFF:
            result = kernel32.VirtualQueryEx(
                pm.process_handle, ctypes.c_void_p(address),
                ctypes.byref(mbi), ctypes.sizeof(mbi)
            )
            if result == 0:
                address += 0x1000
                continue
            if mbi.State == 0x1000 and mbi.Protect in (0x04, 0x40):
                try:
                    data = pm.read_bytes(address, min(mbi.RegionSize, 0x200000))
                    offset = 0
                    while True:
                        idx = data.find(pattern, offset)
                        if idx == -1:
                            break
                        found.append(address + idx)
                        offset = idx + 1
                except:
                    pass
            address += mbi.RegionSize if mbi.RegionSize > 0 else 0x1000

        print(f"[MEM] {label}: {len(found)} enderecos", flush=True)
        return found

    def _write_to_memory(self, addrs, value, placeholder_len):
        if not self._mem_handle or not addrs:
            return False
        name_bytes = value.encode('latin-1', errors='ignore')[:placeholder_len]
        padded = name_bytes + b'\x00' * (placeholder_len - len(name_bytes))
        kernel32 = ctypes.windll.kernel32
        written = ctypes.c_size_t(0)
        for addr in addrs:
            kernel32.WriteProcessMemory(
                self._mem_handle, ctypes.c_void_p(addr),
                padded, len(padded), ctypes.byref(written)
            )
        return True

    def _write_target_to_memory(self, target_name):
        if target_name == self._current_mem_target:
            return
        self._write_to_memory(self._mem_addrs, target_name, len(PLACEHOLDER))
        self._current_mem_target = target_name
        print(f"[MEM] Target: '{target_name}'", flush=True)

    def _write_pot_target(self, name):
        if name == self._pot_target:
            return
        self._write_to_memory(self._pot_mem_addrs, name, len(POT_PLACEHOLDER))
        self._pot_target = name
        if name and name != POT_PLACEHOLDER.decode():
            print(f"[POT] Potando: '{name}'", flush=True)

    # === Combo toggle ===

    def _toggle_combo(self):
        self.combo_enabled = not self.combo_enabled
        if self.combo_enabled:
            self.btn_toggle.config(text="COMBO ON", bg="#225522", fg="#66ff66")
        else:
            self.btn_toggle.config(text="COMBO OFF", bg="#552222", fg="#ff6666")
            self.leader_target_name = ""
            self._write_target_to_memory(PLACEHOLDER.decode())

    # === Main tick ===

    def _tick(self):
        self._tick_network()
        self._tick_elfbot_log()
        self._tick_ui()
        self.root.after(300, self._tick)

    def _tick_network(self):
        if not self.ws.connected:
            return

        if self.combo_enabled:
            self.ws.send("ComboMember", self.config.get("player_name", ""))

            # Heartbeat NavPotion com vocacao
            self.ws.send("NavPotionReq", {"type": "ping", "voc": self.config.get("my_voc", "EK")})

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
                    elif isinstance(payload, (int, float)):
                        continue

                    if self.leader_target_name:
                        self._write_target_to_memory(self.leader_target_name)
                    else:
                        self._write_target_to_memory(PLACEHOLDER.decode())

            elif topic == "NavPotionReq":
                if isinstance(payload, dict) and payload.get("type") == "MP":
                    # Alguem pediu mana — escreve o nome pra Elf Bot potar
                    if self.combo_enabled and sender != self.config.get("player_name", ""):
                        self._write_pot_target(sender)
                        # Limpa depois de 2 segundos
                        self.root.after(2000, lambda: self._write_pot_target(POT_PLACEHOLDER.decode()))

        # Limpa membros offline
        now = time.time()
        stale = [n for n, t in self.connected_members.items() if now - t > 10]
        for n in stale:
            del self.connected_members[n]

    def _tick_elfbot_log(self):
        """Lê o elfscript.log e processa linhas com prefixo."""
        if not self.combo_enabled or not self.ws.connected:
            return

        elfbot_path = self.config.get("elfbot_path", "")
        if not elfbot_path:
            return

        log_path = os.path.join(elfbot_path, "elfsettings", "elfscript.log")

        try:
            # Le so o final do arquivo (rapido mesmo com log grande)
            with open(log_path, "rb") as f:
                f.seek(0, 2)
                size = f.tell()
                f.seek(max(0, size - 2048))
                data = f.read().decode('latin-1', errors='ignore')

            lines = data.split('\n')
            if not lines:
                return

            # Trunca log a cada 30 segundos pra nao crescer infinito
            self._log_truncate_timer += 1
            if self._log_truncate_timer > 100:  # ~30s (300ms * 100)
                self._log_truncate_timer = 0
                try:
                    with open(log_path, "w") as f:
                        f.write("")
                except:
                    pass

            # Processa as ultimas linhas
            for line in reversed(lines[-10:]):
                content = line.strip()
                if " " not in content:
                    continue

                data = content.split(" ", 1)[1].strip()

                if data.startswith("ATK:"):
                    target = data[4:]
                    if target != self._last_sent_target:
                        self._last_sent_target = target
                        if target:
                            self.ws.send("LeaderTarget", target)
                        else:
                            self.ws.send("LeaderTarget", None)
                    break  # ATK eh o mais recente que importa

                elif data.startswith("POS:"):
                    if data != self._last_pos:
                        self._last_pos = data
                        parts = data[4:].split(":")
                        if len(parts) == 3:
                            try:
                                x, y, z = int(parts[0]), int(parts[1]), int(parts[2])
                                self.ws.send("MapInfo", {
                                    "name": self.config.get("player_name", ""),
                                    "position": {"x": x, "y": y, "z": z},
                                    "outfit": {}
                                })
                            except ValueError:
                                pass

                elif data.startswith("MP:"):
                    try:
                        mp = int(data[3:])
                        if mp != self._last_mp:
                            self._last_mp = mp
                            threshold = self.config.get("mp_request_percent", 50)
                            if self.config.get("mp_request_enabled") and mp <= threshold:
                                self.ws.send("NavPotionReq", {
                                    "type": "MP",
                                    "voc": self.config.get("my_voc", "EK")
                                })
                    except ValueError:
                        pass

        except Exception:
            pass

    def _tick_ui(self):
        if self.ws.connected:
            self.lbl_server.config(text="Server: ON", fg="#66ff66")
            self.btn_connect.config(text="Reconectar")
        else:
            self.lbl_server.config(text="Server: OFF", fg="#ff6666")
            self.btn_connect.config(text="Conectar")

        if self.leader_target_name:
            self.lbl_target.config(text=f"Alvo: {self.leader_target_name}")
        else:
            self.lbl_target.config(text="")

        n = len(self.connected_members)
        self.lbl_status.config(text=f"{n} online" if n > 0 else "")

        current = set(self.list_connected.get(0, tk.END))
        members = set(self.connected_members.keys())
        if current != members:
            self.list_connected.delete(0, tk.END)
            for name in sorted(members):
                self.list_connected.insert(tk.END, name)

    def run(self):
        self.root.mainloop()
        self.ws.disconnect()


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def main():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

    app = ComboCompanion()
    app.run()


if __name__ == "__main__":
    main()
