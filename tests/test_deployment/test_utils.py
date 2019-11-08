from unittest.mock import patch

import pytest
from click import UsageError

from caffeine.deployment.utils import dev_mode_only


def test_fn():
    return "blah"


def test_dev_mode_only():
    with patch("caffeine.deployment.utils.Env") as env:
        env.return_value.bool.return_value = False
        fn_dev = dev_mode_only(test_fn)
        with pytest.raises(UsageError):
            fn_dev()

        env.return_value.bool.return_value = True
        fn_prod = dev_mode_only(test_fn)
        assert fn_prod() == test_fn()
