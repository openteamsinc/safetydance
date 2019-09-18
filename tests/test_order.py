"""
This is the test for testing
references to step_data and context_key.

These test cases will cover cases in which there need to be imports
from other files.
"""
import pytest
from llstep import step, script, Context
from references import structure, config, stepdataStruct
context = Context()

@step
def add_data_structure():
    """
    Below, I run tests that are configured to call functions
    that belong to the dict method. These modify the dict.
    """
    structure.revenue += 20
    structure.books['Richard Feynmann'] = 'The Lectures on Physics Vol I'
    structure.people.append('Travis Oliphant')

@step
def add_data_config():
    """
    config is a dict. Let's test a couple dict
    methods to make sure things are working
    """
    info = {'RAM':'32GB', 'Input':'Keyboard', 'processors':'2'}
    config.update(info)

@script
def init_data():
    structure = stepdataStruct(42, {'Douglas Adams' : "The Hitchhiker's Guide to the Galaxy"}, ['Arthur Dent'])
    config  = {'OS':'nix'}

init_data()
print(f'{structure}')

def test_before_data_inject():
    # This is a test step
    # showing how tests can be within a step
    assert structure.revenue == 42
    assert len(structure.books) == 1
    assert len(structure.people) == 1

add_data_structure(context)
add_data_config(context)

def test_after_data_inject():
    # This is the test suite for
    # tests after data has been added
    assert structure.revenue == 62
    assert structure.books['Richard Feynmann'] == 'The Lectures on Physics Vol I'
    assert structure.books['Douglas Adams'] == "The Hitchhiker's Guide to the Galaxy"
    assert len(structure.books) == 2
    assert len(structure.people) == 2
    assert structure.people[0] == 'Arthur Dent'
    assert config['OS'] == 'nix'
    assert config['RAM'] == '32GB'

def delete_data():
    del structure.books['Richard Feynmann']
    structure.revenue = 42
    del structure.people[1]
    del config['Input']

delete_data()

def test_after_data_delete(structure=structure, config=config):
    # Initialize structures
    assert len(config) == 3
    assert len(structure.people) == 1
    assert structure.revenue == 42
    assert len(structure.books) == 1
