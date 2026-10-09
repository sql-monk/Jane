"""Validation against the JSON Schemas of the contracts (``contracts/schemas``, WP-00) - R17.

Services never keep their own copies of contract documents: they validate with the contract files. One class for
every service:

* :class:`ContractSchemas` - ``contracts/schemas/**.schema.json`` (cross-file ``$ref`` resolved from the files)
  and, optionally, one OpenAPI document of ``contracts/openapi`` (its components and request bodies);
  validators are cached; errors come sorted by instance path as :class:`~jane_kit.errors.FieldError` with RFC 6901
  pointers (``prefix`` + path), or raised as ``422 validation_failed`` (:meth:`ContractSchemas.validate`);
* :meth:`ContractSchemas.locate` - where the contracts are: the service's setting, ``JANE_CONTRACTS_DIR``, the
  checkout, then the image fallbacks (``/app/contracts``); a missing directory stops the service at start
  (:class:`ContractsNotFound` names the setting).

``format_check=True`` also checks ``format`` (``date-time``, ``uri``... as far as the validators are installed);
the validation of a service keeps the mode it had, so API behaviour does not change.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from typing import Any, Self

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError, best_match
from referencing import Registry

from jane_kit.contracts import OpenAPISpec, contracts_dir
from jane_kit.errors import FieldError, ValidationFailed

__all__ = ["ContractSchemas", "ContractsNotFound", "json_pointer"]


class ContractsNotFound(RuntimeError):
    """The contracts directory is not available (misconfigured deployment)."""


def json_pointer(path: Iterable[Any], prefix: str = "") -> str:
    """RFC 6901 pointer of an instance path (``~`` -> ``~0``, ``/`` -> ``~1``)."""
    return prefix + "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in path)


def _path_key(error: ValidationError) -> list[tuple[bool, Any]]:
    """Instance path order: list indexes numerically, keys alphabetically (never ``int`` vs ``str``)."""
    return [(isinstance(p, str), p) for p in error.absolute_path]


Explain = Callable[[ValidationError, str], list[FieldError] | None]
"""Hook turning one error into field errors (e.g. a ``oneOf`` re-validated against the branch named by a
discriminator); ``None`` - use the default."""


class ContractSchemas:
    """Validators over the contract schemas of ``root`` (``contracts/``); see the module docstring."""

    def __init__(self, root: Path, *, openapi: str | None = None, format_check: bool = False) -> None:
        self.root = Path(root)
        self.schemas_dir = (self.root / "schemas").resolve()
        self.spec = OpenAPISpec.load(self.root / "openapi" / openapi) if openapi else None
        self.registry: Registry[Any] = (
            self.spec.registry if self.spec is not None else Registry(retrieve=OpenAPISpec._retrieve)  # type: ignore[call-arg]
        )
        self.format_checker = FormatChecker() if format_check else None
        self._validators: dict[str, Draft202012Validator] = {}

    @classmethod
    def locate(
        cls,
        configured: Path | None,
        *,
        setting: str,
        marker: str = "schemas",
        openapi: str | None = None,
        format_check: bool = False,
        start: Path | None = None,
        fallbacks: Sequence[Path] = (Path("/app/contracts"),),
    ) -> Self:
        """The contracts of ``configured`` (a service setting), else of ``JANE_CONTRACTS_DIR`` / the checkout
        (searched from ``start``), else of ``fallbacks``; the directory must contain ``marker``."""
        candidates = [configured] if configured is not None else [contracts_dir(start), *fallbacks]
        for candidate in candidates:
            if candidate is not None and (candidate / marker).exists():
                return cls(candidate, openapi=openapi, format_check=format_check)
        raise ContractsNotFound(f"contracts/{marker} not found: set {setting} (or JANE_CONTRACTS_DIR)")

    # ------------------------------------------------------------------------------------------- addressing
    def uri(self, ref: str) -> str:
        """Absolute URI of ``ref``: ``x.schema.json`` / ``common/y.schema.json#/$defs/Z`` (relative to
        ``contracts/schemas``) or an absolute ``file://``/``https://`` URI (returned as is)."""
        if "://" in ref.partition("#")[0]:
            return ref
        path, _, fragment = ref.partition("#")
        return (self.schemas_dir / path).resolve().as_uri() + "#" + fragment

    def component(self, name: str) -> str:
        """URI of ``#/components/schemas/<name>`` of the OpenAPI document."""
        if self.spec is None:
            raise ValueError("no OpenAPI document loaded")
        return f"{self.spec.base_uri}#/components/schemas/{name}"

    def request_schema_uri(self, method: str, path: str, media: str = "application/json") -> str:
        """URI of the request body schema of an operation of the OpenAPI document."""
        if self.spec is None:
            raise ValueError("no OpenAPI document loaded")
        op = self.spec.operation(method, path)
        body = self.spec.follow(op.loc.child("requestBody"))
        return body.child("content", media, "schema").ref

    # ------------------------------------------------------------------------------------------- validation
    def validator(self, ref: str) -> Draft202012Validator:
        uri = self.uri(ref)
        if uri not in self._validators:
            self._validators[uri] = Draft202012Validator(
                {"$ref": uri}, registry=self.registry, format_checker=self.format_checker
            )
        return self._validators[uri]

    def iter_errors(self, ref: str, instance: Any) -> list[ValidationError]:
        """Errors sorted by instance path."""
        return sorted(self.validator(ref).iter_errors(instance), key=_path_key)

    def field_errors(
        self,
        ref: str,
        instance: Any,
        prefix: str = "",
        *,
        code: str | Callable[[ValidationError], str] = "schema",
        limit: int | None = None,
        message_max: int | None = None,
        best: bool = False,
        explain: Explain | None = None,
    ) -> list[FieldError]:
        """:class:`FieldError` per error: ``pointer`` = ``prefix`` + RFC 6901 path (``/`` for the root when no
        prefix), ``code`` (or ``code(error)``), the message cut at ``message_max``; ``best`` - a failed
        ``oneOf``/``anyOf`` reports its best sub-error; at most ``limit`` errors."""
        out: list[FieldError] = []
        for error in self.iter_errors(ref, instance):
            explained = explain(error, prefix) if explain is not None else None
            if explained is not None:
                out.extend(explained)
            else:
                message = error.message
                if best and error.context:
                    sub = best_match(error.context)
                    if sub is not None:
                        message = f"{sub.message} (at {json_pointer(sub.absolute_path, prefix)})"
                out.append(
                    FieldError(
                        pointer=json_pointer(error.absolute_path, prefix) or "/",
                        code=code(error) if callable(code) else code,
                        message=message[:message_max] if message_max else message,
                    )
                )
            if limit is not None and len(out) >= limit:
                return out[:limit]
        return out

    def validate(
        self, ref: str, instance: Any, prefix: str = "", *, detail: str = "", **options: Any
    ) -> None:
        """Raise ``422 validation_failed`` with :meth:`field_errors` if ``instance`` does not match ``ref``."""
        errors = self.field_errors(ref, instance, prefix, **options)
        if errors:
            raise ValidationFailed(detail or "the document does not match the contract", errors=errors)
