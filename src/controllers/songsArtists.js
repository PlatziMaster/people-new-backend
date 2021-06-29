import {connect} from '../database';

exports.info =  async(req, res) => {
  const db = await connect();
  const result = await db.collection('songsArtists').find({}).toArray();
  res.json(result);
};