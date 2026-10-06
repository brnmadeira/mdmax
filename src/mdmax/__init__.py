"""mdmax - convert documents into compact text for Claude and measure the tokens saved."""

__version__ = "4.0.0"

from .convert import (  # noqa: E402
    SUPPORTED_EXTENSIONS,
    ConversionResult,
    MissingDependency,
    NotConvertible,
    convert,
)

__all__ = [
    "__version__",
    "SUPPORTED_EXTENSIONS",
    "ConversionResult",
    "MissingDependency",
    "NotConvertible",
    "convert",
]
