const mysql = require("mysql");

// CR: Connection without any use
const db = mysql.createPool({
  host: process.env.DATABASE_HOST,
  user: process.env.DATABASE_USER,
  password: process.env.DATABASE_PASSWORD,
  database: process.env.DATABASE,
});

exports.index = (req, res) => {
  res.json({
    status: 200,
    "message:": "Welcome to my API",
  });
};
