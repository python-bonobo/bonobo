import logging
from os import environ
from unittest.mock import patch

import pytest

from bonobo import settings
from bonobo.errors import ValidationError

TEST_SETTING = "TEST_SETTING"


def test_to_bool():
    assert not settings.to_bool("")
    assert not settings.to_bool("FALSE")
    assert not settings.to_bool("NO")
    assert not settings.to_bool("0")

    assert settings.to_bool("yup")
    assert settings.to_bool("True")
    assert settings.to_bool("yes")
    assert settings.to_bool("1")


def test_setting():
    s = settings.Setting(TEST_SETTING)
    assert s.get() is None

    with patch.dict(environ, {TEST_SETTING: "hello"}):
        assert s.get() is None
        s.clear()
        assert s.get() == "hello"

    s = settings.Setting(TEST_SETTING, default="nope")
    assert s.get() is "nope"

    with patch.dict(environ, {TEST_SETTING: "hello"}):
        assert s.get() == "nope"
        s.clear()
        assert s.get() == "hello"

    s = settings.Setting(TEST_SETTING, default=0, validator=lambda x: x == 42)
    with pytest.raises(ValidationError):
        assert s.get() is 0

    s.set(42)

    with pytest.raises(ValidationError):
        s.set(21)


def test_default_settings():
    settings.clear_all()

    assert settings.DEBUG.get() is False
    assert settings.PROFILE.get() is False
    assert settings.QUIET.get() is False
    assert settings.LOGGING_LEVEL.get() == logging._checkLevel("INFO")

    with patch.dict(environ, {"DEBUG": "t"}):
        settings.clear_all()
        assert settings.LOGGING_LEVEL.get() == logging._checkLevel("DEBUG")

    settings.clear_all()


def test_check():
    settings.check()
    with patch.dict(environ, {"DEBUG": "t", "PROFILE": "t", "QUIET": "t"}):
        settings.clear_all()
        with pytest.raises(RuntimeError):
            settings.check()
    settings.clear_all()
