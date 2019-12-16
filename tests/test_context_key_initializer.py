import pytest
from safetydance import script, step, step_data, Context


def simple_context_initializer(context: Context) -> int:
    return 1


key_with_initializer = step_data(int, initializer=simple_context_initializer)
key_without_initializer = step_data(int)


@script
def validates_with_initializer():
    assert key_with_initializer == 1


@script
def validates_exception_without_initializer():
    with pytest.raises(KeyError):
        assert key_without_initializer == 1


def test_key_initialization_behavior():
    validates_with_initializer()
    validates_exception_without_initializer()
