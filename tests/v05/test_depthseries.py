from datetime import datetime
from random import randint

import numpy as np
import pandas as pd
import pytest

from cognite.v05 import depthseries, timeseries, dto

DS_NAME = None


@pytest.fixture(autouse=True, scope='class')
def ts_name():
    global DS_NAME
    DS_NAME = 'test_ds_{}'.format(randint(1, 2 ** 53 - 1))



class TestDepthseries:
    def test_post_depthseries(self):
        tso = dto.TimeSeries(DS_NAME)
        res = depthseries.post_depth_series([tso])
        assert res == {}

    @pytest.fixture(scope='class')
    def create_depthseries(self):
        tso = dto.TimeSeries(DS_NAME)
        try:
            res = depthseries.post_depth_series([tso])
        except:
            pass
        yield depthseries.get_depthseries(prefix=DS_NAME)
        try:
            depthseries.delete_depth_series(DS_NAME)
        except:
            pass

    def test_post_datapoints(self):
        dps = [dto.DatapointDepth(i, i * 100) for i in range(10)]
        res = depthseries.post_datapoints(DS_NAME, depthdatapoints=dps)
        assert res == {}

    def test_get_latest(self):
        from cognite.v05.dto import LatestDatapointResponse
        response = depthseries.get_latest(DS_NAME)
        assert isinstance(response, LatestDatapointResponse)
        assert isinstance(response.to_ndarray(), np.ndarray)
        assert isinstance(response.to_pandas(), pd.DataFrame)
        assert isinstance(response.to_json(), dict)

    def test_update_timeseries(self):
        tso = dto.TimeSeries(DS_NAME, unit='celsius')
        res = depthseries.update_depth_series([tso])
        assert res == {}

    def test_depthseries_unit_correct(self):
        tso = dto.TimeSeries(DS_NAME, unit='celsius')
        res = depthseries.update_depth_series([tso])
        series = depthseries.get_depthseries(prefix=DS_NAME)
        assert series.to_json()[0]['unit'] == 'celsius'
        assert series.to_json()[1]['unit'] == 'm'

    def test_get_depthseries_output_format(self):
        from cognite.v05.dto import TimeSeriesResponse
        series = depthseries.get_depthseries(prefix=DS_NAME)
        assert isinstance(series, TimeSeriesResponse)
        assert isinstance(series.to_ndarray(), np.ndarray)
        assert isinstance(series.to_pandas(), pd.DataFrame)
        assert isinstance(series.to_json()[0], dict)

    def test_get_depthseries_confirm_names(self):
        df = depthseries.get_depthseries(prefix=DS_NAME).to_pandas()
        assert df.loc[df.index[0], 'name'] == DS_NAME
        assert df.loc[df.index[1], 'name'] == DS_NAME + "_DepthIndex"

    def test_get_depthseries_no_results(self):
        result = depthseries.get_depthseries(prefix='not_a_depthseries_prefix')
        assert result.to_pandas().empty
        assert len(result.to_json()) == 0

    def test_reset_depthseries(self):
        res = depthseries.reset_depth_series(DS_NAME)
        assert res == {}

