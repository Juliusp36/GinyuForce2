import argparse
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds


# Create the baseline matrix using user and movie biases
def baseline_matrix(R):

    # Find the ratings that are known
    known = ~np.isnan(R)

    # Find the global mean of all known ratings
    mu = float(np.nanmean(R))

    # Find the number of ratings for each user
    user_count = known.sum(axis=1)

    # Calculate how much each user deviates from the global mean
    user_bias = np.divide(
        np.nansum(R - mu, axis=1),
        user_count,
        out=np.zeros(R.shape[0]),
        where=user_count > 0,
    )

    # Remove the global mean and user bias from the ratings
    residual = R - mu - user_bias[:, None]

    # Find the number of ratings for each movie
    movie_count = known.sum(axis=0)

    # Calculate the movie bias from the remaining residuals
    movie_bias = np.divide(
        np.nansum(residual, axis=0),
        movie_count,
        out=np.zeros(R.shape[1]),
        where=movie_count > 0,
    )

    # B_ui = global mean + user bias + movie bias
    return mu + user_bias[:, None] + movie_bias[None, :]


# Use iterative SVD to predict the missing ratings
# From our evaluation, we found that k = 5 and 5 iterations
# gave us the lowest validation RMSE
def iterative_svd_predict(R, k=5, n_iter=5):

    # Keep track of the ratings that we already know
    known = ~np.isnan(R)

    # Create the baseline matrix
    B = baseline_matrix(R)

    # Subtract the baseline from the known ratings
    # Set the missing residuals to 0
    observed_residual = np.where(known, R - B, 0.0)

    # Create a copy so that we can update the missing residuals
    # without changing the original residuals
    X = observed_residual.copy()

    # Repeat the SVD process n_iter times
    for iteration in range(n_iter):

        # Find the k largest singular values and their vectors
        # X is approximately equal to U * Sigma * Vt
        U, s, Vt = svds(
            X,
            k=k,
            which="LM",
            solver="arpack",
            random_state=0,
        )

        # SciPy does not guarantee the order of the singular values
        # Sort them from largest to smallest
        order = np.argsort(s)[::-1]

        # Reconstruct the matrix using the k singular values
        # Multiplying U by s is equivalent to U @ diag(s)
        L = (U[:, order] * s[order]) @ Vt[order, :]

        # Keep the original residuals for the known ratings
        # Replace the missing residuals with our new predictions
        X = np.where(known, observed_residual, L)

        print(f"Completed iteration {iteration + 1}/{n_iter}")

    # Add the baseline back to the reconstructed residuals
    # Make sure that all predicted ratings are between 1 and 5
    return np.clip(B + L, 1.0, 5.0)


def main():

    # Allow the database and output file to be passed
    # through the command line
    parser = argparse.ArgumentParser(
        description="Build MovieLens SVD predictions"
    )

    parser.add_argument(
        "--db",
        default="backend/movielens.db"
    )

    parser.add_argument(
        "--output",
        default="svd_predictions.npz"
    )

    args = parser.parse_args()

    # Make sure the database exists before connecting to it
    if not Path(args.db).is_file():
        parser.error(f"Database not found: {args.db}")

    # Connect to the database and pull the information
    # needed to create our ratings matrix
    with sqlite3.connect(args.db) as conn:

        # Get all of the actual ratings
        ratings = pd.read_sql_query(
            "SELECT user_id, movie_id, rating FROM ratings",
            conn
        )

        # Get all of the users
        users = pd.read_sql_query(
            "SELECT user_id FROM users ORDER BY user_id",
            conn
        )

        # Get all of the movies
        movies = pd.read_sql_query(
            "SELECT movie_id, title FROM movies ORDER BY movie_id",
            conn
        )

    # Convert the user and movie IDs into NumPy arrays
    user_ids = users.user_id.to_numpy()
    movie_ids = movies.movie_id.to_numpy()

    # Map each user ID to a row in the matrix
    user_index = {
        uid: i for i, uid in enumerate(user_ids)
    }

    # Map each movie ID to a column in the matrix
    movie_index = {
        mid: j for j, mid in enumerate(movie_ids)
    }

    # Create the ratings matrix
    # Rows represent users and columns represent movies
    # Missing ratings are represented by NaN
    R = np.full(
        (len(user_ids), len(movie_ids)),
        np.nan,
        dtype=float
    )

    # Find the row and column for each known rating
    rows = ratings.user_id.map(user_index).to_numpy(dtype=int)
    cols = ratings.movie_id.map(movie_index).to_numpy(dtype=int)

    # Fill the matrix with the ratings from the database
    R[rows, cols] = ratings.rating.to_numpy()

    # Create a mask so that we know which ratings are real
    # True = known rating
    # False = missing rating
    known = ~np.isnan(R)

    # Run iterative SVD using all of the known ratings
    # We no longer need to split the data since we have
    # already evaluated the model and selected our parameters
    predictions = iterative_svd_predict(
        R,
        k=5,
        n_iter=5
    )

    # Save the predictions matrix so that we do not have to
    # run SVD again when importing the predictions into SQLite
    np.savez_compressed(
        args.output,
        predictions=predictions.astype(np.float32),
        observed_mask=known,
        user_ids=user_ids,
        movie_ids=movie_ids,
    )

    # Display information about the predictions matrix
    print(f"Prediction matrix: {predictions.shape}")
    print(f"Observed: {known.sum()}")
    print(f"Missing: {(~known).sum()}")
    print(f"Saved predictions to {args.output}")


# Run the main function when executing this file directly
if __name__ == "__main__":
    main()