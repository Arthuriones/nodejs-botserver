module.exports = async ({ config, utils, state }) => {
    if (!state.apiRouter) {
        utils.log.warn('ElfBot Bridge: apiRouter not found. HTTP module must load first.');
        return;
    }

    const router = state.apiRouter;

    // Alvos por canal POR SENDER: leaderTargets[channel][senderName] = { name, ts }
    const leaderTargets = {};

    // Membros bridge (ElfBot) por canal
    const bridgeMembers = {};

    // Captura LeaderTarget vindo do WebSocket (OTC) e salva por sender
    utils.registerWsHook('LeaderTarget', (ws, msg) => {
        const channel = ws.userData.channel;
        const sender = ws.userData.name;
        const target = msg.message;

        if (!leaderTargets[channel]) leaderTargets[channel] = {};

        if (target === null || target === undefined) {
            leaderTargets[channel][sender] = { name: '', ts: Date.now() };
        } else if (typeof target === 'object') {
            leaderTargets[channel][sender] = { name: target.name || '', ts: Date.now() };
        } else {
            leaderTargets[channel][sender] = { name: String(target), ts: Date.now() };
        }

        return false;
    }, state);

    function broadcastToChannel(channel, message) {
        if (!state.channels[channel]) return;
        const payload = JSON.stringify(message);
        state.channels[channel].forEach(client => {
            try { client.send(payload); } catch {}
        });
    }

    // GET /api/bridge/members?channel=1
    // Retorna todos os conectados (WS + bridge), um por linha
    router.get('/bridge/members', (req, res) => {
        const channel = req.query.channel || '1';
        const names = new Set();

        // Membros WS (OTC)
        if (state.channels[channel]) {
            state.channels[channel].forEach(ws => {
                if (ws.userData?.name) names.add(ws.userData.name);
            });
        }

        // Membros bridge (ElfBot) — ultimos 5s
        if (bridgeMembers[channel]) {
            for (const [name, ts] of Object.entries(bridgeMembers[channel])) {
                if (Date.now() - ts < 5000) names.add(name);
            }
        }

        res.type('text/plain');
        res.send([...names].join('\n'));
    });

    // GET /api/bridge/target?channel=1&leaders=Player1,Player2
    // Retorna o alvo mais recente dos lideres especificados
    router.get('/bridge/target', (req, res) => {
        const channel = req.query.channel || '1';
        const leaders = (req.query.leaders || '').split(',').map(s => s.trim()).filter(Boolean);

        res.type('text/plain');

        if (!leaders.length || !leaderTargets[channel]) {
            res.send('');
            return;
        }

        // Pega o alvo mais recente entre os lideres selecionados
        let bestName = '';
        let bestTs = 0;

        for (const leader of leaders) {
            const t = leaderTargets[channel][leader];
            if (t && t.ts > bestTs) {
                bestName = t.name;
                bestTs = t.ts;
            }
        }

        res.send(bestName);
    });

    // POST /api/bridge/target
    // ElfBot lider envia alvo → salva + broadcast pro WS
    router.post('/bridge/target', (req, res) => {
        const { name, channel, target } = req.body || {};
        if (!name || !channel) return res.status(400).send('missing name/channel');

        const ch = String(channel);
        if (!leaderTargets[ch]) leaderTargets[ch] = {};

        if (target) {
            leaderTargets[ch][name] = { name: target, ts: Date.now() };
            broadcastToChannel(ch, {
                type: 'message',
                id: 0,
                name: name,
                topic: 'LeaderTarget',
                message: target
            });
        } else {
            leaderTargets[ch][name] = { name: '', ts: Date.now() };
            broadcastToChannel(ch, {
                type: 'message',
                id: 0,
                name: name,
                topic: 'LeaderTarget',
                message: null
            });
        }

        res.send('ok');
    });

    // POST /api/bridge/heartbeat
    router.post('/bridge/heartbeat', (req, res) => {
        const { name, channel } = req.body || {};
        if (!name || !channel) return res.status(400).send('missing name/channel');

        const ch = String(channel);

        if (!bridgeMembers[ch]) bridgeMembers[ch] = {};
        bridgeMembers[ch][name] = Date.now();

        broadcastToChannel(ch, {
            type: 'message',
            id: 0,
            name: name,
            topic: 'ComboMember',
            message: name
        });

        res.send('ok');
    });

    utils.log.success('ElfBot Bridge: HTTP endpoints ready (/api/bridge/*)');
};

module.exports.deps = [];

module.exports.meta = {
    name: 'elfbot-bridge',
    description: 'HTTP bridge for ElfBot combo sync with OTC clients',
    author: 'Arthur',
    version: '1.0.0',
    priority: 10,
    enabled: true
};
