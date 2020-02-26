import os, sys
import numpy as np
import ast
import astor

from safetydance import step, step_data, Context, script

array_one = step_data(np.array)
array_two = step_data(np.array)
array_three = step_data(np.array)


@step
def step_one():
    array_one = np.random.rand(4,4)

@step
def step_two():
    array_two = np.random.rand(4,4)

@step
def step_three():
    array_three = np.random.rand(4,4)

@step
def step_four():
    print(f'Array 1:\n { array_one }\n'
          f'Array 2:\n { array_two }\n' 
          f'Array 3:\n { array_three }\n')

@script
def main():
    print(f"Running Main!")
    step_one()
    step_two()
    step_three()
    step_four()
    print(f'Finished main!')

main()