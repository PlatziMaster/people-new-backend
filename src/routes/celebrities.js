const express = require("express");
const celebritiesController = require("../controllers/celebrities");

const router = express.Router();

router.get("/", celebritiesController.info);

module.exports = router;
