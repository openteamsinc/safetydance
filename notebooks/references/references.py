#!/usr/bin/env python

# Mock Module to import into
# Main test method
from llstep import step_data
from dataclasses import dataclass

@dataclass
class TestStruct:
        revenue: int
        books: dict
        people: list

config = step_data(dict)
structure = step_data(TestStruct)
