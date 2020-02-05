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


config = step_data(dict)
structure = step_data(stepdataStruct)
