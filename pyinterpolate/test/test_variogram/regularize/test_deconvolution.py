import unittest
import numpy as np

from pyinterpolate.processing.point.structure import get_point_support_from_files
from pyinterpolate.processing.polygon.structure import get_polyset_from_file
from pyinterpolate.variogram.regularization.deconvolution import Deconvolution

DATASET = '../../samples/regularization/cancer_data.gpkg'
POLYGON_LAYER = 'areas'
POPULATION_LAYER = 'points'
POP10 = 'POP10'
GEOMETRY_COL = 'geometry'
POLYGON_ID = 'FIPS'
POLYGON_VALUE = 'rate'
MAX_RANGE = 400000
STEP_SIZE = 20000
MAX_ITERS = 2

AREAL_INPUT = get_polyset_from_file(DATASET, value_col=POLYGON_VALUE, index_col=POLYGON_ID,
                                    layer_name=POLYGON_LAYER)
POINT_SUPPORT_INPUT = get_point_support_from_files(point_support_data_file=DATASET,
                                                   polygon_file=DATASET,
                                                   point_support_geometry_col=GEOMETRY_COL,
                                                   point_support_val_col=POP10,
                                                   polygon_geometry_col=GEOMETRY_COL,
                                                   polygon_index_col=POLYGON_ID,
                                                   use_point_support_crs=True,
                                                   dropna=True,
                                                   point_support_layer_name=POPULATION_LAYER,
                                                   polygon_layer_name=POLYGON_LAYER)


class TestDeconvolution(unittest.TestCase):

    def test_fit_method(self):
        dcv = Deconvolution(verbose=False)
        dcv.fit(agg_dataset=AREAL_INPUT,
                point_support_dataset=POINT_SUPPORT_INPUT['data'],
                agg_step_size=STEP_SIZE,
                agg_max_range=MAX_RANGE)

        fitted = dcv.initial_regularized_variogram
        initial_deviation = dcv.initial_deviation

        self.assertTrue(fitted is not None)

        expected_deviation = 0.1582
        self.assertAlmostEqual(initial_deviation, expected_deviation, 4)

    def test_transform(self):
        dcv = Deconvolution(verbose=False)

        self.assertTrue(dcv.initial_theoretical_agg_model is None)

        dcv.fit(agg_dataset=AREAL_INPUT,
                point_support_dataset=POINT_SUPPORT_INPUT['data'],
                agg_step_size=STEP_SIZE,
                agg_max_range=MAX_RANGE,
                variogram_weighting_method='closest')

        self.assertTrue(dcv.initial_theoretical_agg_model is not None)

        dcv.transform(max_iters=MAX_ITERS)

        self.assertTrue(dcv.final_theoretical_model is not None)
        self.assertEqual(len(dcv.deviations), 3)

    def test_fit_transform(self):
        dcv1 = Deconvolution(verbose=False)
        dcv2 = Deconvolution(verbose=False)

        dcv1.fit(agg_dataset=AREAL_INPUT,
                 point_support_dataset=POINT_SUPPORT_INPUT['data'],
                 agg_step_size=STEP_SIZE,
                 agg_max_range=MAX_RANGE,
                 variogram_weighting_method='closest')
        dcv1.transform(max_iters=MAX_ITERS)

        dcv2.fit_transform(agg_dataset=AREAL_INPUT,
                           point_support_dataset=POINT_SUPPORT_INPUT['data'],
                           agg_step_size=STEP_SIZE,
                           agg_max_range=MAX_RANGE,
                           variogram_weighting_method='closest',
                           max_iters=MAX_ITERS)

        are_the_same = np.array_equal(dcv1.final_optimal_variogram, dcv2.final_optimal_variogram)
        self.assertTrue(are_the_same)

    def test_fast_stop(self):
        dcv = Deconvolution(verbose=True)

        dcv.fit(agg_dataset=AREAL_INPUT,
                point_support_dataset=POINT_SUPPORT_INPUT['data'],
                agg_step_size=STEP_SIZE,
                agg_max_range=MAX_RANGE,
                variogram_weighting_method='closest')

        max_iters = 3
        dcv.transform(max_iters=max_iters,
                      limit_deviation_ratio=0.5,
                      minimum_deviation_decrease=0.1)

        self.assertNotEqual(dcv.iter, max_iters+1)
