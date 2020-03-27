#!/usr/bin/env python3
import safetydance.extensions as sbe
from safetydance import step, step_data, Context, script
from ast import NodeTransformer, Name, Index, Call, Str, Expr, Subscript, Load, Store

x = step_data(int)
y = step_data(int)
z = step_data(int)

@step
def step_one():
    x = 2

@step
def step_two():
    y = 5

@step
def step_three():
    z = 7

@script
def script_one():
    step_one()
    step_two()
    step_three()

class StepBodyExtensionOne(NodeTransformer):
    def visit_Assign(self, node):
        if((type(node.targets[0]) == Subscript)\
           and node.targets[0].value.id == 'context'):
            called_func = Call\
               (func=Name(id='print', ctx=Load()), \
                args=[Str(s=f'{node.targets[0].slice.value.id} has just been assigned.')], \
                keywords=[])
            newnode = Expr(targets=[Subscript(value=Name(id='context', ctx=Load()), slice=Index(value=Name(id='array_one', ctx=Load())), ctx=Store())],\
                              value=called_func)

            return [node, newnode]

def test_stepbodyextension_one():
    attach_prints = StepBodyExtensionOne()
    sbe.register_stepbody_extension(attach_prints)
    script_one()
