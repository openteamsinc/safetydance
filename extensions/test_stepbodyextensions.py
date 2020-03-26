import numpy as np
import logging 
import ast
import astor
import safetydance.extensions as sbe
from safetydance import step, step_data, Context, script

logger = logging.getLogger(__name__)

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

class addTheseFuncs(ast.NodeTransformer):
    '''This class is a class that will allow us
    to visit specific pieces of the code. It is added to
    the registry here.
    '''
    def visit_Assign(self, node):
         if (type(node.targets[0]) == ast.Subscript):
           newnode = ast.parse(source=(f'print("inside a node here")'), filename='<ast>', mode='exec')
           newexpr = newnode.body[0]
           ast.copy_location(newexpr, node)
           ast.fix_missing_locations(newexpr)
         return [node, newexpr]

    def visit_AnnAssign(self,node):
        logger.debug('In AnnAssign')
        return node
    
    def visit_AugAssign(self, node):
        logger.debug('In AugAssign')
        return node
    
addTheseFuncsIni = addTheseFuncs()
sbe.register_stepbody_extension(addTheseFuncsIni)

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
