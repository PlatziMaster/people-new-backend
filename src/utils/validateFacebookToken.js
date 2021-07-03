const https = require("https");
const userId = process.env.CLIENT_ID;
module.exports = async function (token) {
  await https.get(
    `https://graph.facebook.com/${userId}?access_token=${token}`,
    (res) => {
      if (res.statusCode === 200) {
        return true;
      }
      return false;
    }
  );
};
