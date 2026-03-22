import pytest
from solark_cloud_cli.config import SolarkConfig
from solark_cloud_cli.models.energy import EnergyRecord, EnergyReport


@pytest.fixture
def sample_plant_id():
    return "999999"


@pytest.fixture
def sample_date():
    return "2024"


@pytest.fixture
def sample_api_url():
    return "https://test.solarkcloud.example.com"


@pytest.fixture
def sample_username():
    return "testuser@example.com"


@pytest.fixture
def sample_password():
    return "test-secure-pass"


@pytest.fixture
def sample_config(sample_api_url, sample_username, sample_password, sample_plant_id):
    return SolarkConfig(
        username=sample_username,
        password=sample_password,
        plant_id=sample_plant_id,
        api_url=sample_api_url,
        output_format="table",
        timeout=10,
    )


def make_token_response_dict(
    access_token="test-access-token",
    refresh_token="test-refresh-token",
    expires_in=3599,
    scope="station.view",
    token_type="Bearer",
):
    return {
        "code": 0,
        "msg": "Success",
        "data": {
            "access_token": access_token,
            "token_type": token_type,
            "expires_in": expires_in,
            "refresh_token": refresh_token,
            "scope": scope,
        },
        "success": True,
    }


def make_api_response_dict(labels=None, records_per_label=3, unit="kWh", time_prefix="2024-"):
    if labels is None:
        labels = ["PV", "Load", "Export", "Import"]
    infos = []
    for label in labels:
        records = []
        for i in range(records_per_label):
            records.append(
                {
                    "time": f"{time_prefix}{i + 1:02d}",
                    "value": str(round((i + 1) * 100.5, 1)),
                    "updateTime": None,
                }
            )
        infos.append(
            {
                "unit": unit,
                "records": records,
                "label": label,
                "id": None,
                "groupCode": None,
                "name": None,
            }
        )
    return {
        "code": 0,
        "msg": "Success",
        "data": {"infos": infos},
        "success": True,
    }


@pytest.fixture
def sample_api_response_dict():
    return make_api_response_dict()


@pytest.fixture
def sample_token_response_dict():
    return make_token_response_dict()


def make_energy_report(
    plant_id="999999",
    period="year",
    date="2024",
    labels=None,
    records_per_label=3,
    unit="kWh",
    time_prefix="2024-",
):
    if labels is None:
        labels = ["PV", "Load"]
    records = []
    for label in labels:
        for i in range(records_per_label):
            records.append(
                EnergyRecord(
                    timestamp=f"{time_prefix}{i + 1:02d}",
                    value=round((i + 1) * 100.5, 1),
                    unit=unit,
                    label=label,
                )
            )
    return EnergyReport(
        plant_id=plant_id,
        period=period,
        date=date,
        records=records,
        labels=labels,
    )


@pytest.fixture
def sample_energy_report():
    return make_energy_report()
