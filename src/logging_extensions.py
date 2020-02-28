import os, sys
import numpy as np
import ast
import astor
import logging
import safetydance.extension.stepbodyextension as sbe
from safetydance import step, step_data, Context, script

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

array_one = step_data(np.array)
array_two = step_data(np.array)
array_three = step_data(np.array)

@step
def step_one():
    logger.debug('Inside Step One. Performing Random Matrix Generation.')
    array_one = np.random.rand(4,4)
    logger.debug(f'Array one has been assigned.')

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

class addTheseFuncs(ast.NodeTransformer):
    '''This class is a class that will allow us
    to visit specific pieces of the code. It is added to
    the registry here.
    '''
    def visit_FunctionDef(self, node):
        logger.debug(self, node)
        #self.generic_visit(node)
    
sbe.register_stepbody_extension(addTheseFuncs)

@script
def main():
    print(f"Running Main!")
    print(f"Current stepbody registry: { sbe.STEPBODY_EXTENSION_REGISTRY }")
    step_one()
    #step_two()
    #step_three()
    #step_four()
    print(f'Finished main!')

main()