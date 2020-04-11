#!/usr/bin/env python3
import safetydance.extensions as sbe
from safetydance import step, step_data, Context, script
from ast import (
    NodeTransformer,
    Name,
    Index,
    Call,
    Str,
    Num,
    Expr,
    Eq,
    Subscript,
    Load,
    Store,
    Assert,
    Compare,
    dump,
)

x = step_data(int)
y = step_data(int)
z = step_data(int)
a = step_data(int)


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
    assert a == x, f"Uh-oh, a is {a} - not {x}"
    step_two()
    assert a == y, f"Uh-oh, a is {a} - not {y}"
    step_three()
    assert a == z, f"Uh-oh, a is {a} - not {z}"


class StepBodyExtensionOne(NodeTransformer):
    """
    This adds an assert function every time that
    a variable is initilaized and always resolves to
    true.
    """

    def visit_Assign(self, node):
        if (type(node.targets[0]) == Subscript) and node.targets[
            0
        ].value.id == "context":
            a = node.value
            called_func = Call(
                func=Name(id="print", ctx=Load()),
                args=[
                    Str(
                        s=f"""
                a has just been assigned to the value {a.n} inherited from
                {node.targets[0].slice.value.id} whose value was {node.value.n}.
                """
                    )
                ],
                keywords=[],
            )
            newnode = Expr(
                targets=[
                    Subscript(
                        value=Name(id="context", ctx=Load()),
                        slice=Index(value=Name(id="x", ctx=Load())),
                        ctx=Store(),
                    )
                ],
                value=called_func,
            )
            return [node, newnode]


def test_stepbodyextension_one():
    attach_asserts = StepBodyExtensionOne()
    sbe.register_stepbody_extension(attach_asserts)
    script_one()
