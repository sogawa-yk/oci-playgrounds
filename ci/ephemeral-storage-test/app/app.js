const express = require('express');
const mysql = require('mysql2');

const app = express();
app.use(express.json());

// MySQLコネクション設定
const connectWithRetry = () => {
  const connection = mysql.createConnection({
    host: 'localhost',  // docker-compose内のサービス名
    user: 'testuser',
    password: 'testpass',
    database: 'testdb'
  });

  connection.connect((err) => {
    if (err) {
      console.error('Error connecting to MySQL:', err);
      console.log('Retrying in 5 seconds...');
      setTimeout(connectWithRetry, 5000);
      return;
    }
    console.log('Connected to MySQL database');
  });

  connection.on('error', (err) => {
    console.error('MySQL connection error:', err);
    if (err.code === 'PROTOCOL_CONNECTION_LOST') {
      connectWithRetry();
    } else {
      throw err;
    }
  });

  return connection;
};

let connection;

// ヘルスチェックエンドポイント
app.get('/health', (req, res) => {
  res.json({ status: 'OK' });
});

// ノート一覧の取得
app.get('/notes', (req, res) => {
  if (!connection) {
    return res.status(503).json({ error: 'Database connection not ready' });
  }

  connection.query('SELECT * FROM notes', (err, results) => {
    if (err) {
      console.error('Error fetching notes:', err);
      return res.status(500).json({ error: 'Database error' });
    }
    res.json(results);
  });
});

// ノートの作成
app.post('/notes', (req, res) => {
  if (!connection) {
    return res.status(503).json({ error: 'Database connection not ready' });
  }

  const { content } = req.body;
  if (!content) {
    return res.status(400).json({ error: 'Content is required' });
  }

  connection.query('INSERT INTO notes (content) VALUES (?)', [content], (err, result) => {
    if (err) {
      console.error('Error creating note:', err);
      return res.status(500).json({ error: 'Database error' });
    }
    res.status(201).json({ id: result.insertId, content });
  });
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
  connection = connectWithRetry();
});
