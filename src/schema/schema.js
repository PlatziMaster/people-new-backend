import {makeExecutableSchema} from "graphql-tools"
import {resolvers} from "../graphQL/resolvers"


const typeDefs = `
 type Query {
  hello:String
  getCelebrities: [Celebrities]
  getCelebritie(id: ID!): Celebrities
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


`;

export default makeExecutableSchema({
  typeDefs: typeDefs,
  resolvers: resolvers
})