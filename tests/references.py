#!/usr/bin/env python

# Mock Module to import into
# Main test method
from dataclasses import dataclass
from safetydance import step_data


@dataclass
class stepdataStruct:
    revenue: int
    books: dict
    people: list
    

class HasStepData:
    a_step_data = step_data(str, "this isn't recommended.")


config = step_data(dict)
structure = step_data(stepdataStruct)
