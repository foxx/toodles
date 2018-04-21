import playhouse

__all__ = ['ModelManager', 'DatabaseManager']


##############################################################################
# Model manager
##############################################################################

class ModelManager(list):
    """
    Handles registration for Peewee models
    """

    def __init__(self, database_manager):
        self.dbm = database_manager

    def create_tables(self):
        """Create database tables"""
        for cls in self:
            cls.create_table(fail_silently=True)

    def destroy_tables(self):
        """Destroy database tables"""
        for cls in self:
            cls.drop_table(fail_silently=True)

    def register(self, model_cls):
        """Register model(s) with app"""
        assert issubclass(model_cls, peewee.Model)
        assert not hasattr(model_cls._meta, 'database_manager')
        if model_cls in self:
            raise RuntimeError("Model already registered")
        self.append(model_cls)
        model_cls._meta.database_manager = self.dbm
        return model_cls


####################################################################
# DB manager
####################################################################

# XXX: improve KeyError message
class DatabaseManager(dict):
    """Database manager"""

    def __init__(self):
        self.routers = set()
        self.models = ModelManager(database_manager=self)

    def connect(self):
        """Create connection for all databases"""
        for name, connection in self.items():
            connection.connect()

    def disconnect(self):
        """Disconnect from all databases"""
        for name, connection in self.items():
            if not connection.is_closed():
                connection.close()

    def get_database(self, model):
        """Find matching database router"""
        for router in self.routers:
            r = router.get_database(model)
            if r is not None:
                return r
        return self.get('default')

    def register(self, name, db):
        if isinstance(db, str):
            self[name] = playhouse.db_url.connect(db)
        elif isinstance(db, peewee.Database):
            self[name] = db
        else:
            raise ValueError("unexpected 'db' type")


