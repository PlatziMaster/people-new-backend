import {makeExecutableSchema} from "graphql-tools"
import {resolvers} from "../graphQL/resolvers"


const typeDefs = `
 type Query {
  getCelebrities: [Celebrities]
  getArtists: [Artists]
  getCelebritie(id: ID!): Celebrities
  getArtist(id: ID!): Artists
 }
 type Celebrities{
   _id: ID
   name: String
   gender: String
   age: Int
   height: Float
   birthday: String
   net_worth: Float
   occupation: [String]
   nationality:  String
  bio: String
  Image: String

 }
type Artists{
  _id: ID
  Artist_name: String
  Albums_and_songs: [AlbumsSongs]
  Total_albums: Int
  Analysis:analisys
  Image: String
 }
 type AlbumsSongs{
  Album_name: String
  Total_tracks: Int
  Tracks_ids: [Tracks]
  Total_duration_in_minutes: Float
 }
 type Tracks{
   id: String
   song_name: String
 }
type analisys{
  Happiest:Happiest
  Saddest:Saddest
}
 type Happiest{
   id: String
   song_name: String
   valence: Float
   album_name: String
 }
 type Saddest{
  id: String
  song_name: String
  valence: Float
  album_name: String
 }
`;

export default makeExecutableSchema({
  typeDefs: typeDefs,
  resolvers: resolvers
})