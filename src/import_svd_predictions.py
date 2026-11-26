import argparse
import sqlite3
from pathlib import Path
import numpy as np


# Create a separate table for the predicted ratings
# We do not want to mix actual ratings with predicted ratings
CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS predicted_ratings (
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    predicted_rating REAL NOT NULL
        CHECK(predicted_rating BETWEEN 1 AND 5),
    PRIMARY KEY (user_id, movie_id)
)
"""


# Create an index so that we can quickly retrieve
# the highest predicted ratings for each user
CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_predictions_user_score
ON predicted_ratings(user_id, predicted_rating DESC)
"""


def main():

    # Allow the database and predictions file to be
    # passed through the command line
    parser = argparse.ArgumentParser(
        description="Import SVD predictions into MovieLens"
    )

    parser.add_argument(
        '--db',
        type=Path,
        default=Path('backend/movielens.db')
    )

    parser.add_argument(
        '--npz',
        type=Path,
        default=Path('svd_predictions.npz')
    )

    # Number of predicted ratings to insert at a time
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10000
    )

    args = parser.parse_args()

    # Make sure the batch size is valid
    if args.batch_size < 1:
        parser.error('--batch-size must be positive')

    # Make sure both files exist before continuing
    if not args.db.is_file() or not args.npz.is_file():
        parser.error('Database or NPZ file not found')


    # Load the arrays that we saved from build_svd_predictions.py
    with np.load(args.npz, allow_pickle=False) as data:

        # Matrix containing all of our predicted ratings
        predictions = data['predictions']

        # Mask containing the locations of the actual ratings
        observed = data['observed_mask']

        # IDs corresponding to the rows and columns of the matrix
        user_ids = data['user_ids']
        movie_ids = data['movie_ids']


    # Make sure the dimensions of our matrices match
    # Number of rows = number of users
    # Number of columns = number of movies
    if (
        predictions.shape != observed.shape
        or predictions.shape != (len(user_ids), len(movie_ids))
    ):
        raise ValueError('Inconsistent matrix dimensions')


    # Make sure our observed mask contains Boolean values
    if observed.dtype != np.bool_:
        raise ValueError('observed_mask must be Boolean')


    # Make sure all of the predictions are valid ratings
    if (
        not np.all(np.isfinite(predictions))
        or np.any((predictions < 1) | (predictions > 5))
    ):
        raise ValueError('Predictions must be between 1 and 5')


    # Make sure we do not have duplicate user or movie IDs
    if (
        len(np.unique(user_ids)) != len(user_ids)
        or len(np.unique(movie_ids)) != len(movie_ids)
    ):
        raise ValueError('Duplicate user or movie IDs')


    # Connect to our MovieLens database
    with sqlite3.connect(args.db) as conn:

        # Get the current users and movies from the database
        db_users = {
            row[0] for row in conn.execute(
                'SELECT user_id FROM users'
            )
        }

        db_movies = {
            row[0] for row in conn.execute(
                'SELECT movie_id FROM movies'
            )
        }

        # Make sure the predictions were generated using
        # the same users and movies that are in our database
        if (
            db_users != set(map(int, user_ids))
            or db_movies != set(map(int, movie_ids))
        ):
            raise ValueError(
                'User or movie IDs have changed. Regenerate predictions.'
            )


        # Get the locations of the actual ratings in the database
        actual = {
            (int(u), int(m))
            for u, m in conn.execute(
                'SELECT user_id, movie_id FROM ratings'
            )
        }

        # Get the locations of the actual ratings from our mask
        masked = {
            (int(user_ids[i]), int(movie_ids[j]))
            for i, j in zip(*np.nonzero(observed))
        }

        # Make sure no rating locations have been added or removed
        # since we generated the predictions matrix
        if actual != masked:
            raise ValueError(
                'Rating locations have changed. Regenerate predictions.'
            )


        # Use a transaction so that we can roll back the changes
        # if something goes wrong while inserting the predictions
        with conn:

            # Create the predicted ratings table if it does not exist
            conn.execute(CREATE_TABLE)

            # Remove the old predictions since we are replacing them
            # with the predictions from our latest SVD model
            conn.execute('DELETE FROM predicted_ratings')

            batch = []
            inserted = 0


            # Go through each row of the predictions matrix
            for i, user_id in enumerate(user_ids):

                # Find the columns where the user has not rated a movie
                # ~observed[i] reverses the Boolean values in the mask
                for j in np.flatnonzero(~observed[i]):

                    # Get the user ID, movie ID, and predicted rating
                    batch.append((
                        int(user_id),
                        int(movie_ids[j]),
                        float(predictions[i, j])
                    ))

                    # Insert the predictions once we reach the batch size
                    # This is faster than inserting one rating at a time
                    if len(batch) >= args.batch_size:

                        conn.executemany(
                            'INSERT INTO predicted_ratings VALUES (?, ?, ?)',
                            batch
                        )

                        inserted += len(batch)

                        # Clear the batch before collecting more ratings
                        batch.clear()


            # Insert any remaining predictions that did not
            # make up a complete batch
            if batch:

                conn.executemany(
                    'INSERT INTO predicted_ratings VALUES (?, ?, ?)',
                    batch
                )

                inserted += len(batch)


            # Create the index for retrieving recommendations
            conn.execute(CREATE_INDEX)


        # Find the total number of predictions in the database
        count = conn.execute(
            'SELECT COUNT(*) FROM predicted_ratings'
        ).fetchone()[0]

        print(f'Imported {inserted:,} predictions')
        print(f'Table contains {count:,} rows')
        print('Original ratings table was not modified')


if __name__ == '__main__':
    main()