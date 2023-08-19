from typing import Optional

import pytest
from pydantic import ValidationError

from telebot_constructor.pydantic_utils import ExactlyOneNonNullFieldModel


def test_exactly_one_non_null_field_model() -> None:
    class Example(ExactlyOneNonNullFieldModel):
        number: int
        foo: Optional[str] = None
        bar: Optional[int] = None
        baz: Optional[bool] = None

    # valid instantiations
    Example(number=1, foo="hello")
    Example(number=2, bar=1312)
    Example(number=3, baz=True)

    # invalid instantiations
    with pytest.raises(ValidationError):
        Example(number=4, foo="world", bar=111)
    with pytest.raises(ValidationError):
        Example(number=4, foo="world", baz=False)
    with pytest.raises(ValidationError):
        Example(number=4, bar=111, baz=True)
    with pytest.raises(ValidationError):
        Example(number=4, foo="world", bar=111, baz=False)
