import pytest
from dataclasses import dataclass
from safetydance import script, step, step_data


@dataclass
class Foo:
    bar: int


arg1 = step_data(int, "Hi, I'm arg1")
arg2 = step_data(dict, "Hi, I'm arg3")
One = step_data(int)
Two = step_data(int, "Here's a description for ya!")
SomeFoo = step_data(Foo)


@step
def step_one():  # def step_one(context: Context):
    One = 1
    Two = 2
    arg1 = 7
    arg2 = {"one": 1, "three": 3.333, "thirty": 30}
    SomeFoo = Foo(42)


@step
def step_with_args(arg1, arg2, arg3=None):
    """
    General state coming into this function should be that arg1 is unassigned,
    arg2 is passed an int in the call, and arg3 is passed a str
    steps_globally arg1 is an int, and arg2 is a dict
    """
    arg1 = SomeFoo
    assert isinstance(arg1, Foo)
    assert isinstance(arg2, float)
    assert isinstance(arg3, str)


@script
def my_script():
    step_one()
    assert One == 1
    assert Two == 2
    step_with_args(
        "keyword arg provided", arg2["three"], arg3="this is the keyword arg"
    )
    # arg1 and arg2 were declared as step_data with type int and dict, assigned values in step_one
    # step_with_args changes the class type locally as arg1:Foo, arg2:float
    # these should not affect step_gloabl, and below should pass as arg1:int, arg2:dict
    assert isinstance(arg1, int)
    assert isinstance(arg2, dict)


def test_context_access():
    my_script()
