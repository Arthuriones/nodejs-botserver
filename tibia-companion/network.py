"""
WebSocket client para o BotServer.
Roda em thread separada, comunica via filas (thread-safe).
"""

import threading
import queue
import json
import time
import websocket


class BotServerClient:
    def __init__(self):
        self.incoming = queue.Queue()
        self.outgoing = queue.Queue()
        self.connected = False
        self.url = ""
        self.player_name = ""
        self.channel = "1"
        self._ws = None
        self._thread = None
        self._stop = False

    def connect(self, url, player_name, channel="1"):
        """Inicia conexão em background thread."""
        self.url = url
        self.player_name = player_name
        self.channel = channel
        self._stop = False

        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def disconnect(self):
        self._stop = True
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
        self.connected = False

    def send(self, topic, message):
        """Envia mensagem pro BotServer (thread-safe)."""
        self.outgoing.put({
            "type": "message",
            "topic": topic,
            "message": message
        })

    def get_messages(self):
        """Pega todas as mensagens recebidas (thread-safe)."""
        messages = []
        while not self.incoming.empty():
            try:
                messages.append(self.incoming.get_nowait())
            except queue.Empty:
                break
        return messages

    def _run_loop(self):
        """Loop de conexão com auto-reconnect."""
        while not self._stop:
            try:
                self._ws = websocket.WebSocket()
                self._ws.settimeout(0.2)
                self._ws.connect(self.url)

                # Init
                init_msg = json.dumps({
                    "type": "init",
                    "name": self.player_name,
                    "channel": self.channel
                })
                self._ws.send(init_msg)
                self.connected = True

                while not self._stop:
                    # Receber
                    try:
                        data = self._ws.recv()
                        if data:
                            msg = json.loads(data)
                            if msg.get("type") == "ping":
                                self._ws.send(json.dumps({"type": "ping"}))
                            else:
                                self.incoming.put(msg)
                    except websocket.WebSocketTimeoutException:
                        pass
                    except websocket.WebSocketConnectionClosedException:
                        break

                    # Enviar
                    while not self.outgoing.empty():
                        try:
                            msg = self.outgoing.get_nowait()
                            self._ws.send(json.dumps(msg))
                        except queue.Empty:
                            break
                        except Exception:
                            break

            except Exception:
                self.connected = False

            if not self._stop:
                time.sleep(3)

        self.connected = False
