const express = require('express');
const app = express();

console.log('🚀 Server is starting...');

app.get('/', (req, res) => {
    console.log(' Request received at /');
    res.send('Gym Management System is running!');
});

app.listen(3000, () => {
    console.log(' Server running on port 3000');
});