from datetime import datetime


class DateTimeTool:
    """
    Returns current date and time.
    """

    def now(self):

        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "datetime": datetime.now().isoformat(),
        }