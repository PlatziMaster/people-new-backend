
# Celebrity Wiki - Backend 

The celebrity wiki backend is part of a full stack project, this backend side consists of these components:
- Login (Node.js, social account login with JWT)
- User registration (Node.js)
- Token generation for API key (Node.js with JWT Library)
- GraphQL (Node.js)
- Token verification middleware (Google and facebook login)
- API (Node.js)
- ETL (Extraction, transformation, load) in Python3
The GraphQL and the API endpoints are both deployed in Heroku, you can find them here: https://people-new.herokuapp.com/

The ETL Portion runs on a lambda function on AWS and is set to run once every week.

## API
## Endpoints
### ```POST /auth/login```
This endpoint is used to login users.

Receives:
- Email
- Password

If successfull login (email and password are correct) Returns:
- Status Code: ```202```
- JWT 


### ```POST /auth/register```
This endpoint is used to register users.

Receives:
- Email
- Password
- Password confirm

If these are correct returns:
- Status Code: ```202```
- Message: ```User registered```


### ```GET /graphql```
<strong> Requires authentication </strong>
Returns the graphical interface where the queries are located 
## License

[MIT](https://choosealicense.com/licenses/mit/)

  
## Run the ETL locally
### Pre-requisites:
- Python3
- API Key from https://celebrityninjas.com/api
- Spotify Develeoper account with an app registered, (you'll need the client Id and the client secret)

Navigate to etl 
```bash
cd etl/
```

Install the dependencies
```bash
pip install -r requirements.txt
```

Export the environment variables
```bash
export apikey=yourApiKey
export client_id_sp=yourSpotifyClientId
export client_secret_sp=YourSpotifyClientSecret
```

Run the process and wait for it to finish:
```bash
python3 etl.py
```


## Run the server locally
### Pre-requisites:
- MongoDB cluster
- MySQL Database
- Google Oauth Client Id, you can get it from here https://developers.google.com/identity/protocols/oauth2/web-server
- Web token secret with HS256 hashing
- Python3
- Run the ```etl``` portion


Clone the project

```bash
  git clone https://github.com/AbejaCruz/people-new-backend
```

Go to the project directory

```bash
  cd people-new-backend
```

Install dependencies

```bash
  npm install
```

Configure environment variables in the .env.example with the values needed to connect to your MySQL and MongoDB instances.

Start the server
```bash
    npm run dev
```

