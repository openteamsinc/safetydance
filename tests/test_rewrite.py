"""
This is the test for testing
references to step_data and context_key.

These test cases will cover cases in which there need to be imports
from other files.
"""
import pytest
from safetydance import step, step_data, script
from references import structure, config, stepdataStruct


@step
def add_data_structure():
    """
    Below, I run tests that are configured to call functions
    that belong to the dict method. These modify the dict.
    """
    structure.revenue += 20
    structure.books["Richard Feynmann"] = "The Lectures on Physics Vol I"
    structure.people.append("Travis Oliphant")


@step
def add_data_config():
    """
    config is a dict. Let's test a couple dict
    methods to make sure things are working
    """
    info = {"RAM": "32GB", "Input": "Keyboard", "processors": "2"}
    config.update(info)


@step
def before_data_inject():
    # This is a test step
    # showing how tests can be within a step
    assert structure.revenue == 42
    assert len(structure.books) == 1
    assert len(structure.people) == 1


@step
def after_data_inject():
    # This is the test suite for
    # tests after data has been added
    assert structure.revenue == 62
    assert structure.books["Richard Feynmann"] == "The Lectures on Physics Vol I"
    assert structure.books["Douglas Adams"] == "The Hitchhiker's Guide to the Galaxy"
    assert len(structure.books) == 2
    assert len(structure.people) == 2
    assert structure.people[0] == "Arthur Dent"
    assert config["OS"] == "nix"
    assert config["RAM"] == "32GB"


@step
def delete_data():
    del structure.books["Richard Feynmann"]
    structure.revenue = 42
    del structure.people[1]
    del config["Input"]


@script
def test_references():
    # Initialize structures
    structure = stepdataStruct(
        42, {"Douglas Adams": "The Hitchhiker's Guide to the Galaxy"}, ["Arthur Dent"]
    )
    config = {"OS": "nix"}
    # Run Prior Tests
    before_data_inject()
    # Update Data
    add_data_structure()
    add_data_config()
    # Test After Updating
    after_data_inject()
    # Delete Data
    delete_data()
    # Finish testing in method
    assert len(config) == 3
    assert len(structure.people) == 1
    assert structure.revenue == 42
    assert len(structure.books) == 1


accumulator = step_data(int)


@step
def start_accumulator_with(value: int):
    accumulator = value


@step
def increment_accumulator():
    accumulator = accumulator + 1


@step
def accumulated_value_is(expected: int):
    assert accumulator == expected


@script
def fest_repeated_calls():
    start_accumulator_with(1)
    accumulated_value_is(1)
    increment_accumulator()
    accumulated_value_is(2)
    increment_accumulator()
    accumulated_value_is(3)


@step
def recursive_accumulator(depth: int):
    if depth > 0:
        increment_accumulator()
        recursive_accumulator(depth - 1)


another_step_was_called = step_data(bool)


@step
def calls_another_step():
    another_step()


@step
def another_step():
    another_step_was_called = True


@script
def test_nested_step_calls():
    start_accumulator_with(0)
    recursive_accumulator(3)
    assert accumulator == 3

    another_step_was_called = False
    calls_another_step()
    assert another_step_was_called == True


@step
def step_one():
    print("I ran")


@step
def step_two():
    step_one()


@script
def the_script():
    step_one()
    step_two()


def test_another_test_of_nested_script_calls():
    """This test proves that nested step calls are being properly handled within a
    script."""
    the_script()
