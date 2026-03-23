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


@pytest.fixture
def sample_rate_config(sample_api_url, sample_username, sample_password, sample_plant_id):
    return SolarkConfig(
        username=sample_username,
        password=sample_password,
        plant_id=sample_plant_id,
        api_url=sample_api_url,
        output_format="table",
        timeout=10,
        rate_summer_start="06-01",
        rate_summer_end="09-30",
        rate_summer_inflow=0.2236,
        rate_summer_outflow=0.1038,
        rate_nonsummer_inflow=0.2274,
        rate_nonsummer_outflow=0.0990,
    )


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


def make_energy_report_with_values(
    plant_id="999999",
    period="year",
    date="2024",
    labels=None,
    records_per_label=3,
    unit="kWh",
    time_prefix="2024-",
):
    """Create an energy report with standard energy labels including Load, Import, Export."""
    if labels is None:
        labels = ["Load", "PV", "Export", "Import", "Charge", "Discharge"]
    records = []
    for label in labels:
        for i in range(records_per_label):
            # Generate realistic-ish values per label
            base = (i + 1) * 100.0
            if label == "Load":
                val = base * 2.5
            elif label == "PV":
                val = base * 3.0
            elif label == "Export":
                val = base * 1.5
            elif label == "Import":
                val = base * 0.3
            elif label == "Charge":
                val = base * 0.8
            elif label == "Discharge":
                val = base * 0.7
            else:
                val = base
            records.append(
                EnergyRecord(
                    timestamp=f"{time_prefix}{i + 1:02d}",
                    value=round(val, 1),
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
