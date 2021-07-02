const https = require("https");
const userId = process.env.CLIENT_ID;
module.exports = function (token) {
  https.get(
    `https://graph.facebook.com/${userId}?input_token=${token}`,
    (res) => {
      if (res.statusCode === 200) {
        return true;
      }
      return false;
    }
  );
};
