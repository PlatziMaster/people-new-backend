import {connect} from '../database';

exports.info =  async(req, res) => {
  const db = await connect();
  const result = await db.collection('celebrities').find({}).toArray();
  res.json(result);
};