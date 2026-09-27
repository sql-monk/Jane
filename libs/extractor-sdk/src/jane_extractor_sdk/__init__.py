"""SDK for Jane Python extractors.

Write ``extract(material, params, ctx)`` and return one of :func:`success`, :func:`empty`,
:func:`unrecognized` (raise an exception to fail). See README.md of this package.
"""

from .context import Context, DiagnosticsLog
from .result import empty, entity, success, unrecognized
from .types import Diagnostic, EntityOut, ExtractResult, Material, Unrecognized

__version__ = "0.1.0"

__all__ = [
    "Context",
    "Diagnostic",
    "DiagnosticsLog",
    "EntityOut",
    "ExtractResult",
    "Material",
    "Unrecognized",
    "__version__",
    "empty",
    "entity",
    "success",
    "unrecognized",
]
