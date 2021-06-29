const express = require("express");
const songsArtistsController = require("../controllers/songsArtists");

const router = express.Router();

router.get("/", songsArtistsController.info);

module.exports = router;
