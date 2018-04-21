"""."""
from decimal import Decimal, InvalidOperation


# FIXME: ban from instantiating this class
class QueryModifier(object):
    """."""

    name = ''
    arity = any
    vtype = any

    def __init__(self, separator=':', coerce_values=True):
        """."""
        self.separator = separator
        self.coerce_values = coerce_values

    def coerce_value(self, value):
        """Coerce value to integer or Decimal if possible."""
        try:
            casted_value = int(value)
        except ValueError:
            try:
                casted_value = Decimal(value)
            except InvalidOperation:
                casted_value = value

        return casted_value

    def parse(self, value):
        """."""
        stripped_values = value.split(self.separator, 1)[1].split(',').strip()
        stripped_values_len = len(stripped_values)

        # Make sure amount of values is allowed
        if self.arity != any and stripped_values_len > self.arity:
            errmsg = "Too many values for a query '%s': %i (%s allowed)"
            errmsg %= (''.join(value), stripped_values_len, str(self.arity))
            raise Exception(errmsg)

        parsed = [self.name]
        for value in stripped_values.split(','):
            if not value:
                raise Exception('Malformed query value: %s' % stripped_values)

            if self.coerce_values:
                # Attempt to convert value to numeric
                coercd_val = self.coerce_value(value)
                crd_val_type = type(coercd_val)

                # Make sure resulting value type is allowed
                if self.vtype != any and crd_val_type not in tuple(self.vtype):
                    supp_types = ''.join([str(i) for i in tuple(self.vtype)])
                    errmsg = 'Unsupported value type: %s is %s'
                    errmsg %= (crd_val_type, supp_types)
                    raise Exception(errmsg)

            parsed.append(coercd_val)

        return parsed


class BetweenModifier(QueryModifier):
    """."""

    name = 'between'
    arity = 2
    vtype = (int, Decimal)


class GreaterThenModifier(QueryModifier):
    """."""

    name = 'gt'
    arity = 1
    vtype = (int, Decimal)


class GreaterOrEqualModifier(QueryModifier):
    """."""

    name = 'gte'
    arity = 1
    vtype = (int, Decimal)


class LessThenModifier(QueryModifier):
    """."""

    name = 'lt'
    arity = 1
    vtype = (int, Decimal)


class LessOrEqualModifier(QueryModifier):
    """."""

    name = 'lte'
    arity = 1
    vtype = (int, Decimal)


class InModifier(QueryModifier):
    """."""

    name = 'in'
    arity = any
    vtype = any


class ExactModifier(QueryModifier):
    """."""

    name = 'exact'
    arity = 1  # NOTE: Did I get it right?
    vtype = any


class Contains(QueryModifier):
    """."""

    name = 'contains'
    arity = any
    vtype = any
