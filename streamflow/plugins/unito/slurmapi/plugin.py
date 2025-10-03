from streamflow.ext.plugin import StreamFlowPlugin

from .connector import SlurmApiConnector

class SlurmApiStreamFlowPlugin(StreamFlowPlugin):
    def register(self) -> None:
        self.register_connector("unito.slurmapi", SlurmApiConnector)
