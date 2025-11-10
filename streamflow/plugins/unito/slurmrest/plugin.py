from streamflow.ext.plugin import StreamFlowPlugin

from .connector import SlurmRestConnector

class SlurmRestStreamFlowPlugin(StreamFlowPlugin):
    def register(self) -> None:
        self.register_connector("unito.slurmrest", SlurmRestConnector)
