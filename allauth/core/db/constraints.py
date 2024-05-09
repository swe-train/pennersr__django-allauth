from django.db.models import Q
from django.db.models.constraints import BaseConstraint, UniqueConstraint


class UniqueTrueConstraint(BaseConstraint):
    def __init__(self, fields, name, boolean_field):
        self.fields = fields
        self.name = name
        self.boolean_field = boolean_field

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        kwargs.update(
            {
                "fields": self.fields,
                "name": self.name,
                "boolean_field": self.boolean_field,
            }
        )
        return path, args, kwargs

    def constraint_sql(self, model, schema_editor):
        return self._realize(schema_editor).constraint_sql(model, schema_editor)

    def create_sql(self, model, schema_editor):
        return self._realize(schema_editor).create_sql(model, schema_editor)

    def remove_sql(self, model, schema_editor):
        return self._realize(schema_editor).remove_sql(model, schema_editor)

    def _realize(self, schema_editor):
        if False and schema_editor.connection.features.supports_expression_indexes:
            q_kwargs = {}
            q_kwargs[self.boolean_field] = True
            return UniqueConstraint(
                fields=self.fields, name=self.name, condition=Q(**q_kwargs)
            )
        return UniqueConstraint(fields=self.fields, name=self.name)
