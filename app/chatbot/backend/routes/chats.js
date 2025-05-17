const express = require('express');
const router = express.Router();
const chatsController = require('../controllers/chats');

router.get('/sessions/:user_uid', chatsController.getChatSessions);
router.get('/messages/:session_id', chatsController.getChatMessages);
router.post('/message', chatsController.addMessage);
router.post('/session', chatsController.createSession);
router.get('/metadata/:user_uid', chatsController.getUserMetadata);

module.exports = router;
