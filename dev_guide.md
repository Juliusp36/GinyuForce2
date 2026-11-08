## This document will serve as a summary for the backend. 

The backend consists of an API and database. Check the schema for the database within the 'db' file located in the '/backend' directory. This will primarily be a guide to the API. 

# How to start the API

#### 1. Navigate to the backend folder
```text
cd src/backend
```

#### 2. Install the required packages 
```text
python3 -m pip install -r requirements.txt
```

#### 3. Start the API
```text
python3 app.py
```

# API Endpoints 

## Get endpoints 
: Lists the associated records 

+ /api/health
+ /api/movies
+ /api/users
+ /api/movies 
+ /api/ratings 
+ /api/posers 

## Other Methods 

+ Post - Create ratings, users, and perform lookups 
```text
# perform a lookup
GET	/api/users/1 # Get user 1 
GET /api/ratings/user/1 # Get the ratings entered by user 1 
```
+ Put - Update data 
+ Delete - Remove data 

## CRUD Operations Available in the database (CREATE, READ, UPDATE, DELETE)
+ users - CRUD 
+ movies - R
+ ratings - CRUD 
+ movie_posters - R
