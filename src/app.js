const express = require("express");
const mysql = require("mysql");
const dotenv = require("dotenv");
var cors = require("cors");
const cookieParser = require("cookie-parser");
const { graphqlHTTP } = require("express-graphql");
import schema from "./schema/schema"
dotenv.config({ path: "./.env" });

const app = express();

const port = process.env.PORT || 3000;

const db = mysql.createPool({
  host: process.env.DATABASE_HOST,
  user: process.env.DATABASE_USER,
  password: process.env.DATABASE_PASSWORD,
  database: process.env.DATABASE,
});


var corsOptions = {
  origin: "*",
  optionsSuccessStatus: 200,
};

app.use(cors(corsOptions));

app.use(express.urlencoded({ extended: false }));

app.use(express.json());
app.use(cookieParser());

db.getConnection((error) => {
  if (error) {
    console.log(error);
  } else {
    console.log("MYSQL Connected...");
  }
});


app.use("/graphql", graphqlHTTP({ schema: schema, graphiql: true }));
app.use("", require("./routes/index"));
app.use("/auth", require("./routes/auth"));
app.use("/celebrities", require("./routes/celebrities"));
app.use("/songsArtists", require("./routes/songsArtists"));

app.listen(port, () => {
  console.log(`Server started on Port ${port}`);
});
