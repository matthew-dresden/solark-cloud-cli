import pytest
from solark_cloud_cli.models.api_responses import ApiResponse, Record
from tests.conftest import make_api_response_dict


class TestRecord:
    @pytest.mark.parametrize(
        "time_val,value_val",
        [
            pytest.param("2024-01", "100.5", id="monthly"),
            pytest.param("2024-01-15", "0.0", id="daily-zero"),
            pytest.param("2024-06-15 14:30", "999.9", id="intraday"),
        ],
    )
    def test_record_parses_valid_data(self, time_val, value_val):
        record = Record(time=time_val, value=value_val)
        assert record.time == time_val
        assert record.value == value_val


class TestApiResponse:
    @pytest.mark.parametrize(
        "num_labels,num_records",
        [
            pytest.param(1, 1, id="single-label-single-record"),
            pytest.param(4, 12, id="four-labels-twelve-records"),
            pytest.param(6, 1, id="six-labels-one-record"),
        ],
    )
    def test_parses_valid_response(self, num_labels, num_records):
        labels = [f"Label{i}" for i in range(num_labels)]
        data = make_api_response_dict(labels=labels, records_per_label=num_records)
        response = ApiResponse.model_validate(data)
        assert response.success is True
        assert response.code == 0
        assert len(response.data.infos) == num_labels
        for info in response.data.infos:
            assert len(info.records) == num_records

    def test_rejects_missing_required_fields(self):
        with pytest.raises(Exception):
            ApiResponse.model_validate({"code": 0})
