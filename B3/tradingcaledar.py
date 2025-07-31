import QuantLib as ql

class Calendar:
    def __init__(self) -> None:
        self.calendar = ql.Brazil(ql.Brazil.Settlement)

    def business_days_between_dates(self, start_date: str, end_date: str) -> int:
        """Calculate number of days between two dates.

        Using B3 (Brazil Exchange) calendar, calculates the number of days
        between two given dates.

        Args:
            start_date: str = first day of the period (inclusive)
            end_date: str  = last day of the period (exclusive)

        Returns:
            int: number of days between these days

        Usage example:
            business_days_between_dates('2025-01-02','2025-02-01')
            >>>> 22
        """
        start_date:ql.QuantLib.Date = ql.Date(start_date, "%Y-%m-%d")
        end_date:ql.QuantLib.Date = ql.Date(end_date, "%Y-%m-%d")

        return self.calendar.businessDaysBetween(start_date, end_date)