const { MongoClient } = require("mongodb");
require("dotenv").config();
const USER = encodeURIComponent(process.env.DB_USER);
const PASSWORD = encodeURIComponent(process.env.DB_PASSWORD);
const DB_NAME = process.env.DB_NAME;

const MONGO_URI = `mongodb+srv://${USER}:${PASSWORD}@${process.env.DB_HOST}/${DB_NAME}?retryWrites=true&w=majority`;
let db = null;

export async function connect() {
  if (db != null) {
    return db;
  }
  const client = MongoClient(
    MONGO_URI,
    { useUnifiedTopology: true },
    { useNewUrlParser: true },
    { connectTimeoutMS: 30000 },
    { keepAlive: 1 }
  );

  try {
    await client.connect();
    db = client.db("capstoneproject2");
    console.log("DB is connected");
    return db;
  } catch (e) {
    console.log(e);
  }
}
