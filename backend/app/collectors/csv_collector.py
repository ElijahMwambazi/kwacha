from app.collectors.base import BaseCollector


class Collector(BaseCollector):
    name = "csv_collector"

    def collect(self):
        return {"collector": self.name, "status": "not_implemented"}
