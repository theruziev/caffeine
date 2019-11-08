import pytest

from caffeine.common.store import SortInt


@pytest.mark.parametrize("code, result", [(1, 1), (-1, -1), (0, 0), (1.0, 1), (0.0, 0), (-1.0, -1)])
def test_sort_int_success(code, result):
    sort = SortInt.validate(code)
    assert sort == result


@pytest.mark.parametrize(
    "code, result",
    [(2, ValueError), (3, ValueError), ("-1", ValueError), ("0", ValueError), ("1", ValueError)],
)
def test_sort_int_error(code, result):
    with pytest.raises(result):
        SortInt.validate(code)
