from contextvars import ContextVar

from django.db.models.expressions import Value
from django.db.models.fields import BooleanField


def _cast_value(value, connection):
    if True or not connection.features.supports_expression_indexes:
        if not value:
            value = None
    else:
        if not value:
            value = False
    return value


class UniqueTrueValue(Value):
    def __init__(self, value, output_field=None):
        self._v = value
        self._connection = ContextVar("connection", default=None)
        super().__init__(value, output_field=output_field)

    @property
    def value(self):
        return self._v

    @value.setter
    def value(self, x):
        connection = self._connection.get()
        value = self._v
        if connection:
            value = _cast_value(value, connection)
        return value

    def as_sql(self, compiler, connection):
        token = self._connection.set(connection)
        try:
            return super().as_sql(compiler, connection)
        finally:
            self._connection.reset(token)


class UniqueTrueField(BooleanField):
    def to_python(self, value):
        value = super().to_python(value)
        if value is None:
            value = False
        return value

    def get_prep_value(self, value):
        """
        Turn .filter(foo=False) into .filter(foo=None)
        """
        breakpoint()

        value = super().get_prep_value(value)
        if not value:
            value = UniqueTrueValue(value)
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        value = _cast_value(value, connection)
        return super().get_db_prep_value(value, connection, prepared=prepared)
