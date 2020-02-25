import pytest
from safetydance import script, step, step_data

first_value = step_data(int)
second_value = step_data(str)
third_value = step_data(list)

@step
def step_one():
    first_value = 1
    second_value = "two"
    third_value = ('a', 'b', 'c')

@script
def my_script():
    step_one()    
    tester = f"Values are: {first_value}, {second_value}, {third_value}"
    assert tester == "Values are: 1, two, ('a', 'b', 'c')"
    
def test_fstrings():
    my_script()