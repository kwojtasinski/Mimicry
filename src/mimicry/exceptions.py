from mimicry.models import FieldConfiguration


class MimicryInvalidFieldConfigurationError(Exception):
    """Exception raised when a field configuration is invalid."""

    def __init__(self, field: FieldConfiguration, exception: Exception) -> None:
        self.field = field
        self.exception = exception
        super().__init__(f"Invalid field configuration for '{field}': {exception}")


class MimicryInvalidCountValueError(Exception):
    """Exception raised when the count value is invalid."""

    def __init__(self, count: int) -> None:
        self.count = count
        super().__init__(
            f"Invalid count value: {count}. It must be a positive integer.",
        )
