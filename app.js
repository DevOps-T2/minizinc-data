const express = require('express');
const mysql = require('mysql');
const bodyParser = require('body-parser');
const storage = require('./storage');

const SERVICE_NAME = "minizinc-data";

const app = express();
app.use(bodyParser.json());
const port = 8000;
/*
const wdb = mysql.createConnection({
    host: `${SERVICE_NAME}-mysql-0.minizinc-data-headless`,
    user: 'root',
    database: 'Default'
});

const rdb = mysql.createConnection({
    host: `${SERVICE_NAME}-mysql-read`,
    user: 'root',
    database: 'Default'
})
*/
app.listen(port, () => {
    console.log(`Listening on ${port}`)
});

app.get('/api/minizinc/upload', async function(req, res) {
    policy = await storage.generatePostSignedPolicy();
    res.send(url)
});

app.post('/api/minizinc/upload', (req, res) => {
    // userID, fileName, fileUUID inserted into mysql.
    res.send("File created!")
})

app.get('/api/minizinc/', (req, res) => {
    // userID, fileUUID
    // Send link 
})