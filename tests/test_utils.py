import pytest

from telebot_constructor.user_flow.blocks.form import join_localizable_texts
from telebot_constructor.utils import page_params_to_redis_indices
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


@pytest.mark.parametrize(
    "params, expected_result",
    [
        pytest.param((0, 10), (-10, -1)),
        pytest.param((1, 10), (-11, -2)),
        pytest.param((0, 0), (0, -1)),
        pytest.param((10, 0), (-10, -11)),
    ],
)
def test_page_params_to_redis_indices(params: tuple[int, int], expected_result: tuple[int, int]):
    assert page_params_to_redis_indices(*params) == expected_result
