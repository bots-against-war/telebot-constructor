from pydantic import BaseModel, model_validator
from typing import get_args, get_origin, Union


class ExactlyOneNonNullFieldModel(BaseModel):
    """
    If a subclass model has several Optional[...] fields, exactly one of them must contain the actual value,
    and others be None.

    Useful for serializing a union of different types under one wrapper object, like how Telegram Bot API
    handles multiple update types
    """

    @model_validator(mode="after")
    def validate_exactly_one_non_null_field(self) -> "ExactlyOneNonNullFieldModel":
        optional_field_names: set[str] = set()
        for field_name, field_info in self.model_fields.items():
            if get_origin(field_info.annotation) == Union and type(None) in get_args(field_info.annotation):
                optional_field_names.add(field_name)
        non_null_optional_fields = {name for name in optional_field_names if getattr(self, name) is not None}
        if len(non_null_optional_fields) != 1:
            raise ValueError(
                f"Exacly one optional field (of {sorted(optional_field_names)}) must be set to non-null value, "
                + f"but {len(non_null_optional_fields)} actually are: {sorted(non_null_optional_fields)}"
            )
