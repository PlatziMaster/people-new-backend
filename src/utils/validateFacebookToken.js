const https = require("https");
const userId = process.env.CLIENT_ID;
module.exports = function (token) {
  https.get(
    `https://graph.facebook.com/${userId}?access_token=${token}`,
    (res) => {
      console.log(res.statusCode);
      console.log(userId);
      console.log(token);
      if (res.statusCode === 200) {
        return true;
      }
      return false;
    }
  );
};
