const express = require('express');
const cors = require('cors');
require('dotenv').config();

const chatRoutes = require('./routes/chats');

const app = express();
app.use(cors());
app.use(express.json());
app.use('/api/chats', chatRoutes);

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
});
