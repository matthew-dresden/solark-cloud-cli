import logging

from solark_cloud_cli.config import SolarkConfig
from solark_cloud_cli.models.energy import EnergyReport, ValuationRow

logger = logging.getLogger(__name__)


class ValuationService:
    def __init__(self, config: SolarkConfig) -> None:
        if not config.has_rate_config():
            msg = (
                "Rate configuration is required for value calculations. "
                "Set SOLARK_RATE_SUMMER_INFLOW, SOLARK_RATE_SUMMER_OUTFLOW, "
                "SOLARK_RATE_NONSUMMER_INFLOW, and SOLARK_RATE_NONSUMMER_OUTFLOW "
                "in your .env file or as environment variables."
            )
            raise ValueError(msg)
        self._config = config

    def add_valuations(self, report: EnergyReport) -> EnergyReport:
        """Add dollar value calculations to an energy report.

        Supported for year and month periods where data is in kWh.
        Returns the report unchanged for day period (data is in watts).
        """
        logger.info("Computing valuations for %s period, date %s", report.period, report.date)
        if report.period not in ("year", "month"):
            return report

        # Build lookup: {timestamp: {label: value}}
        by_time: dict[str, dict[str, float]] = {}
        for record in report.records:
            if record.timestamp not in by_time:
                by_time[record.timestamp] = {}
            by_time[record.timestamp][record.label] = record.value

        valuations: list[ValuationRow] = []
        for timestamp in sorted(by_time.keys()):
            row = by_time[timestamp]
            load = row.get("Load", 0.0)
            grid_import = row.get("Import", 0.0)
            export = row.get("Export", 0.0)

            month = self._extract_month(timestamp)
            is_summer = self._config.is_summer_month(month)

            if is_summer:
                inflow_rate = self._config.rate_summer_inflow
                outflow_rate = self._config.rate_summer_outflow
            else:
                inflow_rate = self._config.rate_nonsummer_inflow
                outflow_rate = self._config.rate_nonsummer_outflow

            # These are guaranteed non-None by has_rate_config() check in __init__
            assert inflow_rate is not None
            assert outflow_rate is not None

            self_consumed = load - grid_import
            avoided_cost = self_consumed * inflow_rate
            export_credit = export * outflow_rate
            total_value = avoided_cost + export_credit

            logger.debug(
                "Timestamp %s: summer=%s, self_consumed=%.1f, avoided=$%.2f, export=$%.2f, total=$%.2f",
                timestamp,
                is_summer,
                self_consumed,
                avoided_cost,
                export_credit,
                total_value,
            )

            valuations.append(
                ValuationRow(
                    timestamp=timestamp,
                    self_consumed_kwh=round(self_consumed, 1),
                    avoided_cost=round(avoided_cost, 2),
                    export_credit=round(export_credit, 2),
                    total_value=round(total_value, 2),
                )
            )

        logger.info("Valuation complete: %d rows computed", len(valuations))
        return report.model_copy(update={"valuations": valuations})

    @staticmethod
    def _extract_month(timestamp: str) -> int:
        """Extract month number from timestamps like '2025-06' or '2025-06-15'."""
        parts = timestamp.split("-")
        if len(parts) >= 2:
            return int(parts[1])
        msg = f"Cannot extract month from timestamp: {timestamp}"
        raise ValueError(msg)
