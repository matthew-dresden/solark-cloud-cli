import json

from solark_cloud_cli.models.energy import EnergyReport


class JsonFormatter:
    def format(self, report: EnergyReport) -> str:
        return json.dumps(report.model_dump(mode="json"), indent=2)
