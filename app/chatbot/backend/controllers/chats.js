const pool = require('../models/db');

// Get all chat sessions of user
exports.getChatSessions = async (req, res) => {
  const { user_uid } = req.params;
  if (!user_uid) {
    return res.status(400).send('user_uid is required');
  }
  console.log('Fetching sessions for user:', user_uid);
  try {
    const result = await pool.query(
      'SELECT * FROM chat_sessions WHERE user_id = $1 ORDER BY created_at DESC',
      [user_uid]
    );
    res.json(result.rows);
  } catch (err) {
    res.status(500).send(err.message);
  }
};

// Get full chat (messages) for a session
exports.getChatMessages = async (req, res) => {
  const { session_id } = req.params;
  try {
    const result = await pool.query(
      'SELECT * FROM chat_messages WHERE session_id = $1 ORDER BY created_at ASC',
      [session_id]
    );
    res.json(result.rows);
  } catch (err) {
    res.status(500).send(err.message);
  }
};

// Save a new message in a session
exports.addMessage = async (req, res) => {
  const { session_id, user_uid, message, sender } = req.body; // sender = 'user' or 'bot'
  console.log('Adding message:', { session_id, user_uid, message, sender });
  try {
    const result = await pool.query(
      'INSERT INTO chat_messages (session_id, message_text, sender_role) VALUES ($1, $2, $3) RETURNING *',
      [session_id, message, sender]
    );
    console.log('Message added:', result.rows[0]);
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).send(err.message);
  }
};

// Create a new chat session
exports.createSession = async (req, res) => {
  const { user_uid, title } = req.body;
  if (!user_uid || !title) {
    return res.status(400).send('user_uid and title are required');
  }
  console.log('Creating session for user:', user_uid, 'with title:', title);
  try {
    const result = await pool.query(
      'INSERT INTO chat_sessions (user_id, title) VALUES ($1, $2) RETURNING *',
      [user_uid, title]
    );
    console.log('Session created:', result.rows[0]);
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).send(err.message);
  }
};

exports.getUserMetadata = async (req, res) => {
  const user_uid = req.params.user_uid;

  try {
    // Try faculty first
    let result = await pool.query(
      'SELECT reg_number FROM faculty_member_profiles WHERE "UID" = $1',
      [user_uid]
    );

    let reg_number = result.rows.length > 0 ? result.rows[0].reg_number : null;

    // If not found in faculty, try student
    if (!reg_number) {
      result = await pool.query(
        'SELECT reg_number FROM "Student details" WHERE "UID" = $1',
        [user_uid]
      );
      reg_number = result.rows.length > 0 ? result.rows[0].reg_number : null;
    }

    // If still not found
    if (!reg_number) {
      return res.status(404).json({ error: 'User not found' });
    }

    const firstLetter = reg_number.charAt(0).toUpperCase();
    let user_role = '';

    if (firstLetter === 'F') {
      user_role = 'faculty';
    } else if (firstLetter === 'S') {
      user_role = 'student';
    } else {
      user_role = 'unknown';
    }

    res.json({
      user_reg_number: reg_number,
      user_role: user_role,
    });

  } catch (error) {
    console.error('Error fetching user metadata:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

