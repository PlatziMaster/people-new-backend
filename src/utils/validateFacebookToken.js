const https = require("https");
const userId = process.env.CLIENT_ID;
module.exports = function (token) {
  console.log(userId);
  https.get(
    `https://graph.facebook.com/${userId}?access_token=${token}`,
    (res) => {
      console.log(res.statusCode);
      if (res.statusCode === 200) {
        return true;
      }
      return false;
    }
  );
};
