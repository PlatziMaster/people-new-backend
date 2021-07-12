const mysql = require("mysql");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");

// CR: Multiples connections across the app
const db = mysql.createPool({
  host: process.env.DATABASE_HOST,
  user: process.env.DATABASE_USER,
  password: process.env.DATABASE_PASSWORD,
  database: process.env.DATABASE,
});

exports.login = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        error: {
          message: "Please provide an email and password",
        },
      });
    }

    db.query(
      "SELECT * FROM users WHERE email = ?",
      [email],
      async (error, results) => {
        // CR: The prod env must be without console.logs
        console.log(results);
        if (
          results.length === 0 ||
          !(await bcrypt.compare(password, results[0].password))
        ) {
          return res.status(401).json({
            error: {
              message: "Email or Password is incorrect",
            },
          });
        } else {
          const id = results[0].id;
          const token = jwt.sign({ id }, process.env.JWT_SECRET, {
            expiresIn: process.env.JWT_EXPIRES_IN,
          });
          // CR: The prod env must be without console.logs
          console.log("The token is: " + token);

          const cookieOptions = {
            expires: new Date(
              Date.now() + process.env.JWT_COOKIE_EXPIRES * 24 * 60 * 60 * 1000
            ),
            httpOnly: true,
          };
          const dateUpdate = new Date();
          // CR: Which is the reason to update the user? For save the last login?
          db.query(
            `UPDATE users SET updatedAt = ?  WHERE  email = "${email}"`,
            [dateUpdate],
            (error, results) => {
              // CR: The prod env must be without console.logs
              if (error) {
                console.log(error);
              } else {
                console.log("Update Last login");
              }
            }
          );
          res.cookie("jwt", token, cookieOptions);
          res.status(202).json({
            status: 202,
            "message:": "User Login",
            id: id,
            token: token,
          });
        }
      }
    );
  } catch (error) {
    // CR: The prod env must be without console.logs
    console.log(error);
  }
};

exports.register = (req, res) => {
  const { email, password, passwordConfirm } = req.body;

  db.query(
    "SELECT email FROM users WHERE email = ?",
    [email],
    async (error, results) => {
      // CR: The prod env must be without console.logs
      if (error) {
        console.log(error);
      }

      if (results.length > 0) {
        return res.json({
          error: {
            message: "That email is already in use",
          },
        });
      } else if (password !== passwordConfirm) {
        return res.json({
          error: {
            message: "Passwords do not match",
          },
        });
      }
      let hashedPassword = await bcrypt.hash(password, 8);
      const dateUpdate = new Date();
      db.query(
        "INSERT INTO users SET ?",
        {
          email: email,
          password: hashedPassword,
          createdAt: dateUpdate,
        },
        (error, results) => {
          // CR: The prod env must be without console.logs
          if (error) {
            console.log(error);
          } else {
            console.log(results);
            return res.json({
              status: 202,
              "message:": "User registered",
            });
          }
        }
      );
    }
  );
};
