const https = require("https");
const userId = process.env.CLIENT_ID;
module.exports = function (token) {
  console.log(`https://graph.facebook.com/${userId}?access_token=${token}`);
  https.get(
    `https://graph.facebook.com/${userId}?access_token=${token}`,
    (res) => {
      if (res.id === `${userId}`) {
        return true;
      }
      return false;
    }
  );
};
