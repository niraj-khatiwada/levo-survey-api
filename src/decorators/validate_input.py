from functools import wraps
from marshmallow import ValidationError


def validate_input(schema_class, target="data", inject_as=None):
    """
    Decorator to validate and deserialize input data.

    :param schema_class: The Marshmallow schema class to use.
    :param target: The name of the argument to validate (default: 'data').
    :param inject_as: The name of the argument to inject the validated data into.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            schema = schema_class()

            if target not in kwargs:
                raise ValueError(f"Missing `{target}` keyword argument for validation.")

            raw_data = kwargs[target]

            try:
                validated = schema.load(raw_data)
                if inject_as is not None:
                    kwargs[inject_as] = validated
            except ValidationError as e:
                raise ValidationError(f"Invalid input: {e.messages}")

            return func(*args, **kwargs)

        return wrapper

    return decorator
