const express = require("express");
const authController = require("../controllers/auth");
const auth = require("../middleware/auth");
/**
 * This is the router variable para referencias los controler para registrar y hacer login
 */

const router = express.Router();

router.post("/register", auth, authController.register);

router.post("/login", authController.login);

module.exports = router;
