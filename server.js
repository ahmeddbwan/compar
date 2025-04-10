const express = require('express');
const mongoose = require('mongoose');
const app = express();

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/filedata', {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => {
    console.log('MongoDB connected');
}).catch(err => {
    console.error('MongoDB connection error:', err);
});

// Define a model (assuming a simple schema)
const FileData = mongoose.model('FileData', new mongoose.Schema({
    name: String,
    date: Date,
    status: String
}));

// Route to get data from the database
app.get('/get-table-data', async (req, res) => {
    try {
        const data = await FileData.find();  // Fetch data from the database
        res.json(data);  // Send data as JSON to the frontend
    } catch (err) {
        res.status(500).send({ message: 'Error fetching data' });
    }
});

// Serve static files (for your HTML, JS, and CSS)
app.use(express.static('public'));

// Start server
app.listen(3000, () => {
    console.log('Server running on port 3000');
});
