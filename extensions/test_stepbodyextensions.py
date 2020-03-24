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
    def addToNode(self, node, newnode):
        source = astor.to_source(node)
        print(f'S O U R C E C O D E O F N O D E'
              f'{source}')
        appended_node = ast.parse(source + "print('hello from within the ast!')")
        return appended_node
    '''This class is a class that will allow us
    to visit specific pieces of the code. It is added to
    the registry here.
    '''
    def visit_Assign(self, node):
        logger.debug(self, node)
        print('Visiting an assign Statement')
        print(astor.dump_tree(node.targets[0]))
        print("O R I G I N A L N O D E ------------------")
        print(type(node), f'{ astor.dump_tree(node) }')
        if (type(node.targets[0]) == ast.Subscript):
            print('I have detected the subscript -- this is part of a context. Attach logging here!')
            #func_code = compile(source="a = sum[1,2,3]", filename='lol', mode='exec')
            #newnode = ast.parse(source="a = sum[1,2,3]", filename='lol', mode='exec')
            code = ast.parse("print('hello from within the ast!')")
            newnode = compile(code, filename="<ast>", mode="exec")
            newnode = ast.Expr(value=newnode)
            print("N E W N O D E  ------------- -----------------")
            print(type(newnode), f'{ astor.dump_tree(newnode) }')
            print("O R I G I N A L N O D E ------------------")
            print(type(node), f'{ astor.dump_tree(node) }')
            #newnewnode = self.addToNode(node, newnode)
            #ast.copy_location(newnode, node)
            #ast.fix_missing_locations(newnode)
            print("N E W N O D E  ------------- P O S T C O P Y-----------------")
            print(type(newnode), f'{ astor.dump_tree(newnode) }')
        return ast.fix_missing_locations(newnode)

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
