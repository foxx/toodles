import toodles

class Toodles:
    """
    Entrypoint class
    """

    def __init__(self):
        self.databases = toodles.db.DatabaseManager()
        self.models = toodles.db.ModelManager(self.databases)
        self.wsgiapp = toodles.web.Application(catchall=True)
