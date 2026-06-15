"""Runtime identity discovery and runtime context construction for MXM."""

from mxm.runtime.build import build_runtime_context
from mxm.runtime.context import RuntimeContext, RuntimeMetadata, RuntimePaths
from mxm.runtime.identity import build_runtime_identity
from mxm.runtime.validation import RuntimeIdentityError, validate_runtime_identity_shape
from mxm.types import RuntimeIdentity

__all__ = [
    "RuntimeContext",
    "RuntimeIdentity",
    "RuntimeIdentityError",
    "RuntimeMetadata",
    "RuntimePaths",
    "build_runtime_context",
    "build_runtime_identity",
    "validate_runtime_identity_shape",
]
