import numpy as np


def bias_baseline(R):
    known = ~np.isnan(R)
    mu = np.nanmean(R)

    b_user = np.nanmean(R - mu, axis=1)
    residual = R - mu - b_user[:, None]

    n_item = known.sum(axis=0)
    b_item = np.zeros(R.shape[1])
    has_rating = n_item > 0
    b_item[has_rating] = (
        np.nansum(residual, axis=0)[has_rating] / n_item[has_rating])
    return mu, b_user, b_item

def baseline_matrix(R):
    """Full matrix of baseline predictions mu + b_user + b_item."""
    mu, b_user, b_item = bias_baseline(R)
    return mu + b_user[:, None] + b_item[None, :]


def rank_k(U, s, Vt, k):
    """Rank-k matrix from an SVD that was already computed."""
    return U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]