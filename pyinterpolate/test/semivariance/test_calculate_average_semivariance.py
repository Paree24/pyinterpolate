import unittest
import os
import numpy as np
import geopandas as gpd
from pyinterpolate.data_processing.data_preparation.get_points_within_area import get_points_within_area
from pyinterpolate.data_processing.data_preparation.prepare_areal_shapefile import prepare_areal_shapefile
from pyinterpolate.semivariance.areal_semivariance.areal_semivariance import ArealSemivariance
from pyinterpolate.semivariance.areal_semivariance.within_block_semivariance.calculate_average_semivariance\
    import calculate_average_semivariance


class TestCalculateAverageSemivariance(unittest.TestCase):

    def test_calculate_average_semivariance(self):

        # Data prepration
        my_dir = os.path.dirname(__file__)

        areal_dataset = os.path.join(my_dir, 'sample_data/test_areas_pyinterpolate.shp')
        subset = os.path.join(my_dir, 'sample_data/test_points_pyinterpolate.shp')

        a_id = 'id'
        areal_val = 'value'
        points_val = 'value'

        # Get maximum range and set step size

        gdf = gpd.read_file(areal_dataset)

        total_bounds = gdf.geometry.total_bounds
        total_bounds_x = np.abs(total_bounds[2] - total_bounds[0])
        total_bounds_y = np.abs(total_bounds[3] - total_bounds[1])

        max_range = min(total_bounds_x, total_bounds_y)
        step_size = max_range / 4

        lags = np.arange(0, max_range, step_size * 2)

        areal_data_prepared = prepare_areal_shapefile(areal_dataset, a_id, areal_val)
        points_in_area = get_points_within_area(areal_dataset, subset, areal_id_col_name=a_id,
                                                points_val_col_name=points_val)

        # Set areal semivariance class
        areal_semivariance = ArealSemivariance(areal_data_prepared, lags, step_size,
                                               points_in_area)
        areal_semivariance.regularize_semivariogram()
        avg_semi = calculate_average_semivariance(areal_semivariance.distances_between_blocks,
                                                  areal_semivariance.inblock_semivariance, areal_semivariance.areal_lags,
                                                  areal_semivariance.areal_ss)
        data_test_vals = avg_semi.astype(np.int)

        desired_output = np.array([[0, 111], [1, 111]])
        test_vals = (data_test_vals == desired_output)
        self.assertTrue(test_vals.all(), "Output should be [[0, 111], [1, 111]]")


if __name__ == '__main__':
    unittest.main()
