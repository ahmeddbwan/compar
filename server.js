const express = require('express');
const multer = require('multer');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const exceljs = require('exceljs');
const fs = require('fs');

// Initialize app
const app = express();

// Create storage for multer to handle uploaded files
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'UPLOAD_FOLDER/');
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  }
});

const upload = multer({ storage });

// Connect to SQLite database
const db = new sqlite3.Database('./database.db', (err) => {
  if (err) {
    console.error('Error opening database', err.message);
  } else {
    console.log('Connected to SQLite database');
  }
});

// Function to create table if it doesn't exist
function createTable() {
  db.run(`CREATE TABLE IF NOT EXISTS file_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date TEXT,
    status TEXT
  )`);
}

// Endpoint to handle file upload
app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded');
  }

  const filePath = path.join(__dirname, 'UPLOAD_FOLDER', req.file.filename);
  const workbook = new exceljs.Workbook();

  // Read and process the Excel file
  workbook.xlsx.readFile(filePath)
    .then(() => {
      const worksheet = workbook.worksheets[0];  // Assuming data is on the first sheet
      const data = [];
      worksheet.eachRow((row, rowNumber) => {
        if (rowNumber > 1) {  // Skip header row
          data.push([
            row.getCell(1).text,  // Name
            row.getCell(2).text,  // Date
            row.getCell(3).text   // Status
          ]);
        }
      });

      // Insert data into SQLite database
      const insertQuery = `INSERT INTO file_data (name, date, status) VALUES (?, ?, ?)`;

      db.serialize(() => {
        const stmt = db.prepare(insertQuery);
        data.forEach(row => {
          stmt.run(row);
        });
        stmt.finalize();

        // Respond with success
        res.json({ success: true, message: 'Data successfully uploaded and inserted into the database!' });
      });
    })
    .catch((err) => {
      console.error(err);
      res.status(500).json({ error: 'Error processing file' });
    });
});

// Endpoint to fetch table data
app.get('/get-table-data', (req, res) => {
  db.all('SELECT * FROM file_data', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Error fetching data' });
    } else {
      res.json(rows);  // Send the data as JSON
    }
  });
});

// Endpoint to create table if not exists (from frontend button)
app.post('/create_table', (req, res) => {
  createTable();
  res.json({ success: true });
});

// Serve static files (for frontend)
app.use(express.static('public'));

// Start server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
