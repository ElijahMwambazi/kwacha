from app.collectors.base import BaseCollector


class Collector(BaseCollector):
    name = "zamstats_collector"

    def collect(self):
        return {"collector": self.name, "status": "not_implemented"}
