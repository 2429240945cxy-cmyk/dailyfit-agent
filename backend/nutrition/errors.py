class NutritionLookupError(RuntimeError):
    """Raised when a nutrition source cannot produce a usable result."""


class NutritionParseError(NutritionLookupError):
    """Raised when a source response lacks required nutrients."""
