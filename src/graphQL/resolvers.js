import  {connect} from '../database'
import {ObjectID} from 'mongodb';

export const resolvers = {
 Query :{
   hello: () =>{
     return "Hello world with GraphQL"
   },
   getCelebrities: async() =>{
    const db = await connect();
    const result = await db.collection('celebrities').find({}).toArray();

    return result
   },
   getCelebritie: async(_,args) =>{
    const _id =args.id;
      const db = await connect();
     const result = await db.collection('celebrities').findOne({"_id":ObjectID(_id)});

    return result
   }

 }
}