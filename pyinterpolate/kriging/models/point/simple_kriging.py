"""
Perform point simple kriging.

Functions
---------
A. simple_kriging()

Authors
-------
1. (A.,) -> Szymon Moliński | @SimonMolinsky

TODO
----
* log k, predicted, dataset
"""
# Python core
from typing import List, Union, Tuple

# Core calculation and data visualization
import numpy as np

# Pyinterpolate
from pyinterpolate.kriging.utils.process import get_predictions, solve_weights
from pyinterpolate.variogram import TheoreticalVariogram


def simple_kriging(
        theoretical_model: TheoreticalVariogram,
        known_locations: np.ndarray,
        unknown_location: Union[List, Tuple, np.ndarray],
        process_mean: float,
        neighbors_range=None,
        no_neighbors=1,
        use_all_neighbors_in_range=False,
        allow_approximate_solutions=False,
        err_to_nan=False
) -> List:
    """
    Function predicts value at unknown location with Ordinary Kriging technique.

    Parameters
    ----------
    theoretical_model : TheoreticalVariogram
                        Trained theoretical variogram model.

    known_locations : numpy array
                      Array with the known locations.

    unknown_location : Union[List, Tuple, numpy array]
                       Point where you want to estimate value (x, y) <-> (lon, lat)

    process_mean : float
                   The mean value of a process over a study area. Should be know before processing. That's why Simple
                   Kriging has limited number of applications. You must have multiple samples and well-known area to
                   know this parameter.

    neighbors_range : float, default = None
                      Maximum distance where we search for point neighbors. If None given then range is selected from
                      the theoretical_model rang attribute.

    no_neighbors : int, default = 4
                   Number of the n-closest neighbors used for interpolation.

    use_all_neighbors_in_range : bool, default = False
                                 True: if number of neighbors within the neighbors_range is greater than the
                                 number_of_neighbors then take all of them for modeling.

    allow_approximate_solutions : bool, default = False
                                  Allows the approximation of kriging weights based on the OLS algorithm.
                                  Not recommended to set to True if you don't know what you are doing!

    err_to_nan : bool, default=False
                 Singular matrix error in solve kriging system to NAN.

    Returns
    -------
    : numpy array
        [predicted value, variance error, longitude (x), latitude (y)]

    """

    k, predicted, dataset = get_predictions(theoretical_model,
                                            known_locations,
                                            unknown_location,
                                            neighbors_range,
                                            no_neighbors,
                                            use_all_neighbors_in_range)

    if err_to_nan:
        try:
            output_weights = solve_weights(predicted, k, allow_approximate_solutions)
        except np.linalg.LinAlgError as _:
            return [np.nan, np.nan, unknown_location[0], unknown_location[1]]
    else:
        output_weights = solve_weights(predicted, k, allow_approximate_solutions)

    r = dataset[:, -2] - process_mean
    zhat = r.dot(output_weights)
    zhat = zhat + process_mean

    sigma = np.matmul(output_weights.T, k)

    return [zhat, sigma, unknown_location[0], unknown_location[1]]
