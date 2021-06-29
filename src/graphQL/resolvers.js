import { connect } from "../database";
import { ObjectID } from "mongodb";

export const resolvers = {
  Query: {
    getCelebrities: async () => {
      const db = await connect();
      const result = await db.collection("celebrities").find({}).toArray();

      return result;
    },
    getCelebritie: async (_, args) => {
      const _id = args.id;
      const db = await connect();
      const result = await db
        .collection("celebrities")
        .findOne({ _id: ObjectID(_id) });

      return result;
    },
    getArtists: async () => {
      const db = await connect();
      const result = await db.collection("songsArtists").find({}).toArray();
      return result;
    },
    getArtist: async (_, args) => {
      const _id = args.id;
      const db = await connect();
      const result = await db
        .collection("songsArtists")
        .findOne({ _id: ObjectID(_id) });

      return result;
    },
  },
};
