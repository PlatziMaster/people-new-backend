const express = require("express");
const authController = require("../controllers/auth");
const auth = require("../middleware/auth");

const router = express.Router();

router.post("/register", auth, authController.register);

router.post("/login", authController.login);

module.exports = router;
