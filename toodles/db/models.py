import peewee
import datetime
from peewee import DateTimeField

####################################################################
# Model
####################################################################


class Metadata(peewee.Metadata):
    _database = None

    @property
    def database(self):
        # if this model has a specific database, use that instead
        if self._database: 
            return self._database

        # if model has a db manager then use db routing
        if self.database_manager:
            return self.database_manager.get_database(self)
        
    @database.setter
    def database(self, value):
        self._database = value


class Model(peewee.Model):
    """Custom model"""

    class Meta:
        model_metadata_class = Metadata

    def update_instance(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()

    @classmethod
    def create_or_get(self, **kwargs):
        with self.atomic():
            try:
                return self.create(**kwargs), True
            except peewee.IntegrityError:
                return self.get(**kwargs), False

    @classmethod
    def get_or_none(cls, **kwargs):
        try:
            return cls.get(**kwargs)
        except cls.DoesNotExist:
            return None

    @classmethod
    def atomic(self):
        """Shortcut method for creating atomic context"""
        return self._meta.database.atomic()
    
    def to_pk_ref(self):
        """Returns dict of values to uniquely reference this item"""
        fields = self._meta.get_primary_keys()
        assert fields
        values = {field.name:self.__data__[field.name] for field in fields}
        return values

    @classmethod
    def from_pk_ref(self, cursor):
        """Returns model instance from unique cursor reference"""
        return self.get(**cursor)

    def refetch(self):
        """
        Return new model instance with fresh data from database
        Only works on models which have a primary or compound key
        See https://github.com/coleifer/peewee/issues/638

        XXX: Add support for models without PK
        """
        ref = self.to_pk_ref()
        return self.from_pk_ref(ref)


####################################################################
# Mixins
####################################################################

def utcnow_no_ms():
    """Returns utcnow without microseconds"""
    return datetime.datetime.utcnow().replace(microsecond=0)


class TimestampModelMixin(Model):
    """Track creation and modification times"""
    created = DateTimeField(default=utcnow_no_ms)
    modified = DateTimeField()

    def save(self, **kwargs):
        self.modified = datetime.datetime.now()
        return super(TimestampModelMixin, self).save(**kwargs)


