module.exports = {
    appTitle: 'NodeJS BotServer',
    HTTP_HOST: process.env.HOST || '0.0.0.0',
    HTTP_PORT: parseInt(process.env.PORT || '8080'),
    HTTP_ALLOWED_IPS: ['127.0.0.1', '::1'],
    WS_PORT: parseInt(process.env.WS_PORT || process.env.PORT || '8080'),
    WS_MAX_PAYLOAD: 64 * 1024,
    WS_MAX_PACKETS: 100,
    WS_MAX_TOPIC_LENGTH: 30,
};
