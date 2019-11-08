from unittest.mock import mock_open, patch

import pytest
import semver

from caffeine import app_info
from caffeine.deployment.release import new_version, get_current_release


@pytest.mark.parametrize(
    "bump, h",
    [
        ("major", "6f1ed002ab5595859014ebf0951522d9"),
        ("minor", "f43708ad8cd051f0e1cb169424abe8ea"),
        ("patch", "ed914ac948ad3a33c62f93422ba931ec"),
    ],
)
def test_new_version(bump, h):
    with patch("builtins.open", mock_open()) as mock_file:
        old_version = app_info.version

        def side_effect(w):
            bumper = getattr(semver, f"bump_{bump}")
            assert bumper(old_version) in w
            assert h in w

        mock_file.return_value.write.side_effect = side_effect
        new_version(bump, h)


def test_get_current_release():
    assert get_current_release() == app_info.release_name
