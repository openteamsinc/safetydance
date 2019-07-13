from ast import dump, arg, arguments, Attribute, copy_location, Call, fix_missing_locations, Load, Name, NameConstant, NodeVisitor, NodeTransformer, parse
from dataclasses import dataclass
from inspect import getclosurevars, getmodule, getsource, signature
from typing import Callable, Dict, NewType
import functools


@dataclass(frozen=True)
class ContextKey:
    datatype: type
    description: str


class Context(Dict[ContextKey, object]):
    ...

    
class NestingContext(Context):
    
    def __init__(self, *args, parent: Context = None, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.parent = parent
        
    def __missing__(self, key):
        if self.parent is not None:
            return self.parent[key]
        return super().__missing__(key)
        

class Step:
    def __init__(self, f: Callable):
        self.f = f

    def __call__(self, *args, **kwargs):
        #print(f"enter: {self.f.__name__}  args: {args}  kwargs: {kwargs}")
        self.f(*args, **kwargs)
        #print(f"exit: {self.f.__name__}  args: {args}")
        

def step(f):
    """
    Mark a function as a Step... later, do more
    """
    return functools.wraps(f)(Step(f))

        
class Script(Step):
    def __call__(self, *args, **kwargs):
        context = NestingContext()
        if "context" in kwargs:
            context.parent = kwargs["context"]
        kwargs["context"] = context
        super().__call__(*args, **kwargs)
        
        
class ScriptRewriter(NodeTransformer):
    def __init__(self, f: Callable):
        super().__init__()
        self.closurevars = getclosurevars(f)
        self.modulevars = vars(getmodule(f))
        
    def resolve_callable(self, id: str):
        if id in self.closurevars.nonlocals:
            return self.closurevars.nonlocals.get(id)
        if id in self.closurevars.globals:
            return self.closurevars.globals.get(id)
        if id in self.closurevars.unbound:
            return None
        
    def visit_arguments(self, arguments_node):
        """
        Rewrite args of the function so that it takes a Context argument.
        """
        context_arg = arg("context", Name("Context", Load()))
        arguments_node.kwonlyargs.insert(0, context_arg)
        arguments_node.kw_defaults.insert(0, NameConstant(None))
        return fix_missing_locations(arguments_node)

    def visit_Call(self, call):
        """
        Is it a call to a step? If so, rewrite it!
        The call should pass the context along, that's it.
        """
        if type(call.func) is Attribute:
            return call
        else:
            resolved_callable = self.resolve_callable(call.func.id)
            if resolved_callable is None:
                return call
            if not isinstance(resolved_callable, Step):
                return call
            # if it's a step, rewrite
            new_args = [copy_location(Name("context", Load()), call)]
            new_args.extend(call.args)
            return fix_missing_locations(copy_location(
                Call(
                    call.func,
                    new_args,
                    call.keywords),
                call))

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        decorators = node.decorator_list
        node.decorator_list = [
            decorator
            for decorator in node.decorator_list
            if self.modulevars.get(decorator.id, None) != script
        ]
        return node

        
def script(f):
    """
    Rewrite the function as a Script
    remember Signature.replace
    """
    sourcecode = getsource(f)
    in_tree = parse(sourcecode)
    out_tree = ScriptRewriter(f).visit(in_tree)
    new_func_name = out_tree.body[0].name
    func_scope = f.__globals__
    # Compile the new function in the old function's scope. If we don't change the
    # name, this actually overrides the old function with the new one
    exec(compile(out_tree, '<string>', 'exec'), func_scope)
    return functools.wraps(f)(Script(func_scope[new_func_name]))