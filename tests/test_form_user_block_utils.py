import pytest

from telebot_constructor.user_flow.blocks.form import join_localizable_texts
from telebot_constructor.utils.pydantic import Language, LocalizableText


@pytest.mark.parametrize(
    "texts, expected_result, sep",
    [
        pytest.param(["foo", "bar", "baz"], "foo bar baz", " "),
        pytest.param(["foo"], "foo", " "),
        pytest.param(["foo", "bar", "baz"], "foobarbaz", ""),
        pytest.param(
            [
                {
                    Language.lookup("ru"): "ru1",
                    Language.lookup("en"): "en1",
                },
                {
                    Language.lookup("ru"): "ru2",
                    Language.lookup("en"): "en2",
                },
            ],
            {
                Language.lookup("ru"): "ru1  ru2",
                Language.lookup("en"): "en1  en2",
            },
            "  ",
        ),
    ],
)
def test_join_localizable_texts(texts: list[LocalizableText], expected_result: LocalizableText, sep: str) -> None:
    assert join_localizable_texts(texts, sep) == expected_result
