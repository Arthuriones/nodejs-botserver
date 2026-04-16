"""
Tibia 8.6 Memory Reader
Lê dados do client direto da memória do processo.
Endereços padrão do Tibia 8.60 — ajuste no config.json se seu OT usar client modificado.
"""

import pymem
import pymem.process
import struct
import time


class Creature:
    __slots__ = ('id', 'name', 'hp', 'x', 'y', 'z')

    def __init__(self, id=0, name='', hp=0, x=0, y=0, z=0):
        self.id = id
        self.name = name
        self.hp = hp
        self.x = x
        self.y = y
        self.z = z


# Endereços padrão Tibia 8.60 (ajustáveis via config)
DEFAULT_ADDRESSES = {
    # Player
    "player_id":    0x72C83C,
    "player_name":  0x72C894,
    "player_hp":    0x72C844,
    "player_maxhp": 0x72C84C,
    "player_mp":    0x72C854,
    "player_maxmp": 0x72C858,
    "player_x":     0x72C880,
    "player_y":     0x72C884,
    "player_z":     0x72C888,
    "player_level": 0x72C840,

    # Target
    "target_id":    0x72C8B0,

    # Battle List
    "bl_start":     0x773700,
    "bl_step":      0xBC,
    "bl_max":       150,

    # Offsets dentro de cada entrada da Battle List
    "bl_id":        0x00,
    "bl_name":      0x04,
    "bl_hp":        0x8C,
    "bl_posx":      0x98,
    "bl_posy":      0x9C,
    "bl_posz":      0xA0,
}


class TibiaMemoryReader:
    def __init__(self, process_name="Tibia.exe", addresses=None):
        self.process_name = process_name
        self.addr = {**DEFAULT_ADDRESSES, **(addresses or {})}
        self.pm = None
        self.connected = False

        # Cache do estado atual
        self.player_name = ""
        self.player_id = 0
        self.player_hp = 0
        self.player_maxhp = 0
        self.player_mp = 0
        self.player_maxmp = 0
        self.player_x = 0
        self.player_y = 0
        self.player_z = 0
        self.player_level = 0
        self.target_id = 0
        self.battle_list = []

    def attach(self):
        """Tenta conectar ao processo do Tibia."""
        try:
            self.pm = pymem.Pymem(self.process_name)
            self.connected = True
            return True
        except Exception:
            self.pm = None
            self.connected = False
            return False

    def detach(self):
        if self.pm:
            try:
                self.pm.close_process()
            except Exception:
                pass
        self.pm = None
        self.connected = False

    def _read_int(self, address):
        try:
            return self.pm.read_int(address)
        except Exception:
            return 0

    def _read_string(self, address, max_len=32):
        try:
            raw = self.pm.read_bytes(address, max_len)
            return raw.split(b'\x00')[0].decode('latin-1', errors='ignore')
        except Exception:
            return ""

    def _write_int(self, address, value):
        try:
            self.pm.write_int(address, value)
            return True
        except Exception:
            return False

    def update(self):
        """Lê todos os dados relevantes da memória. Chamar a cada tick (~200ms)."""
        if not self.connected:
            if not self.attach():
                return False

        try:
            a = self.addr
            self.player_id = self._read_int(a["player_id"])
            self.player_name = self._read_string(a["player_name"])
            self.player_hp = self._read_int(a["player_hp"])
            self.player_maxhp = self._read_int(a["player_maxhp"])
            self.player_mp = self._read_int(a["player_mp"])
            self.player_maxmp = self._read_int(a["player_maxmp"])
            self.player_x = self._read_int(a["player_x"])
            self.player_y = self._read_int(a["player_y"])
            self.player_z = self._read_int(a["player_z"])
            self.player_level = self._read_int(a["player_level"])
            self.target_id = self._read_int(a["target_id"])

            self._read_battle_list()
            return True

        except Exception:
            self.connected = False
            return False

    def _read_battle_list(self):
        """Lê a battle list inteira da memória."""
        a = self.addr
        bl_start = a["bl_start"]
        bl_step = a["bl_step"]
        bl_max = a["bl_max"]
        creatures = []

        for i in range(bl_max):
            base = bl_start + (i * bl_step)
            cid = self._read_int(base + a["bl_id"])
            if cid == 0:
                continue

            name = self._read_string(base + a["bl_name"])
            if not name:
                continue

            hp = self._read_int(base + a["bl_hp"])
            x = self._read_int(base + a["bl_posx"])
            y = self._read_int(base + a["bl_posy"])
            z = self._read_int(base + a["bl_posz"])

            creatures.append(Creature(id=cid, name=name, hp=hp, x=x, y=y, z=z))

        self.battle_list = creatures

    def find_creature_by_name(self, name):
        """Procura criatura na battle list por nome (case-insensitive)."""
        name_lower = name.lower()
        for c in self.battle_list:
            if c.name.lower() == name_lower:
                return c
        return None

    def find_creature_by_id(self, creature_id):
        """Procura criatura na battle list por ID."""
        for c in self.battle_list:
            if c.id == creature_id:
                return c
        return None

    def attack_creature(self, creature_id):
        """Ataca uma criatura escrevendo o ID no endereço de target."""
        if not self.connected or creature_id == 0:
            return False
        return self._write_int(self.addr["target_id"], creature_id)

    def stop_attack(self):
        """Para de atacar."""
        if not self.connected:
            return False
        return self._write_int(self.addr["target_id"], 0)

    def get_current_target(self):
        """Retorna a criatura sendo atacada atualmente."""
        if self.target_id == 0:
            return None
        return self.find_creature_by_id(self.target_id)

    def hp_percent(self):
        if self.player_maxhp == 0:
            return 0
        return int((self.player_hp / self.player_maxhp) * 100)

    def mp_percent(self):
        if self.player_maxmp == 0:
            return 0
        return int((self.player_mp / self.player_maxmp) * 100)
