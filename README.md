# GinyuForce2
Welcome to the repository for the Fall 2026 MATH344L project
## Projec Instructions 
We have chosen the following instructions:

**Recommendation System**

Construct a basic recommendation system for items like movies, music, books, or games and represent the users' ratings or preferences in the form of a matrix, then investigate how linear algebra—specifically low-rank matrix approximations—can be applied in order to identify patterns and predict the missing ratings.

Build and test your system using Python, working with either a real dataset or one that your group has created which is interesting enough.

Possible questions: Can you predict what a user will like by referring to the preferences of other users.

## Brainstorming (WIP)
So far, there is a json file with users and their ratings for specific movies. Notice, that per each individual, not every movie in the database has a ranking. A good next step is to be able to approximate rankings for movies per user. 
### How might we produce ranking approximations: 
+ Scale up our json file to an sql database that holds more data fields (SQLite would suffice here) :
  + For example, we could have two tables. One for users and one for movies.
  + Each user would have a specific json object for thier preferences
  + The movies table would hold additional fields such as ID, Genre, Sub-Genre, Release Date, Original Language, Keywords, Description, etc..
    + More data fields theoreticall make it easier to reccomend movies to users
  + We would then produce matrix approximations to fill in the gaps for movies that users did not rate themselves
### Presentation 
I propose a simple Python interface using FastAPI(backend) and React(Frontend) that has a login and create account page that shows the user their ratings, approximates (i.e. what they might like or their possible ratings). We could display movie posters and descriptions when the user clicks on it. This can be achieved by filling our database with requests to the **OMDB API** which contains a database of movies which can give us the fields we need, and poster images. 
### Difficulties
Matrix approximation because it is the only thing in this project that either of us has no experience in
