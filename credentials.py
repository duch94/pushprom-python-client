class Credentials:

    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port

    @property
    def address(self):
        return f"http://{self.host}:{self.port}"
