from ast import (
    arg,
    Attribute,
    copy_location,
    Call,
    fix_missing_locations,
    Index,
    Load,
    Name,
    NameConstant,
    NodeTransformer,
    parse,
    Str,
    Subscript,
)
from dataclasses import dataclass
from inspect import getclosurevars, getfile, getmodule, getsource
from typing import Any, Callable, Dict, Type
import functools
import inspect
import logging

def step_decorator(f):
    f.is_step_decorator = True
    return f


@dataclass(frozen=True)
class ContextKey:
    datatype: type
    description: str


def step_data(key_type: Type, description: str = None):
    return ContextKey(key_type, description)


class Context(Dict[ContextKey, Any]):
    ...


class NestingContext(Context):
    def __init__(self, *args, parent: Context = None, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.parent = parent

    def __missing__(self, key):
        if self.parent is not None:
            return self.parent[key]
        raise KeyError(key)


class Step:
    def __init__(self, f: Callable, step_rewriter):
        self.f_original = f
        self.f = None
        self.step_rewriter = step_rewriter

    def __call__(self, context: Context, *args, **kwargs):
        if self.f is None:
            self.rewrite()
        self.f(context, *args, **kwargs)

    def rewrite(self):
        sourcecode = getsource(self.f_original)
        in_tree = parse(sourcecode)
        out_tree = self.step_rewriter(self.f_original).visit(in_tree)
        new_func_name = out_tree.body[0].name
        func_scope = self.f_original.__globals__
        # Compile the new function in the old function's scope. If we don't change the
        # name, this actually overrides the old function with the new one
        exec(compile(out_tree, "<string>", "exec"), func_scope)
        self.f = func_scope[new_func_name]


class StepRewriter(NodeTransformer):
    def __init__(self, f: Callable):
        super().__init__()
        self.f = f
        self.step_body_rewriter = StepBodyRewriter(f)
        self.modulevars = vars(getmodule(f))
        
    def visit_arguments(self, arguments_node):
        """
        Rewrite args of the function so that it takes a positional Context argument.
        """
        context_arg = arg("context", Name("Context", Load()))
        arguments_node.args.insert(0, context_arg)
        return fix_missing_locations(arguments_node)
    
    def is_step_decorator(self, decorator_id):
        decorator = self.f.__globals__.get(decorator_id)
        return hasattr(decorator, 'is_step_decorator')
    
    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        node.decorator_list = [
            decorator
            for decorator in node.decorator_list
            if not self.is_step_decorator(decorator.id)
        ]
        node.body = [self.step_body_rewriter.visit(n) for n in node.body]
        return node
 
        
@step_decorator
def step(f, step_rewriter=StepRewriter, step_class=Step):
    """
    Rewrite the step function so:
    1. `context: Context` is the first parameter
    2. All references to ContextKey instances are rewritten as
       `context[key]`
    """
    return functools.wraps(f)(step_class(f, step_rewriter=step_rewriter))


class Script(Step):
    def __call__(self, *args, **kwargs):
        if self.f is None:
            self.rewrite()
        context = NestingContext()
        if "context" in kwargs:
            context.parent = kwargs["context"]
        kwargs["context"] = context
        self.f(*args, **kwargs)


class StepBodyRewriter(NodeTransformer):
    
    def __init__(self, f: Callable):
        super().__init__()
        self.f = f
        self.closurevars = getclosurevars(f)
        self.modulevars = vars(getmodule(f))
        self.step_globals = f.__globals__
        
    def resolve(self, id: str):
        if id in self.closurevars.nonlocals:
            return self.closurevars.nonlocals.get(id)
        if id in self.closurevars.globals:
            return self.closurevars.globals.get(id)
        if id in self.closurevars.unbound:
            return None
        
    def visit_Call(self, call):
        """
        Is it a call to a step? If so, rewrite it!
        The call should pass the context along, that's it.
        """
        call.args = [self.visit(arg) for arg in call.args]
        if type(call.func) is Attribute:
            call.func = self.visit_Attribute(call.func)
            return call
        resolved_callable = self.resolve(call.func.id)
        if resolved_callable is None:
            return call
        if not isinstance(resolved_callable, Step):
            return call
        # if it's a step, rewrite
        new_args = [copy_location(Name("context", Load()), call)]
        new_args.extend(call.args)
        return fix_missing_locations(
            copy_location(Call(call.func, new_args, call.keywords), call)
        )
        
    def visit_Name(self, node):
        """
        If the name resolves to a ContextKey, rewrite it as a subscript
        of the `context`.
        """
        sig = inspect.signature(self.f)
        resolved = self.step_globals.get(node.id, None)
        
        if resolved is not None and isinstance(resolved, ContextKey):
            if node.id in sig.parameters:
                logging.info(" '" + str(node.id) + "' skipped in context[] map, called from " + str(self.f))
                return node
            else:
                return fix_missing_locations(copy_location(Subscript(
                    value=Name(id="context", ctx=Load()),
                    slice=Index(value=Name(id=node.id, ctx=Load())),
                    ctx=node.ctx
                ), node))
        else:
            return node
        
        
    def visit_Attribute(self, node):
        node.value = self.visit(node.value)
        return node
    
    
       
class ScriptRewriter(StepRewriter):

    def visit_arguments(self, arguments_node):
        """
        Rewrite args of the function so that it takes a Context argument.
        """
        context_arg = arg("context", Name("Context", Load()))
        arguments_node.kwonlyargs.insert(0, context_arg)
        arguments_node.kw_defaults.insert(0, NameConstant(None))
        return fix_missing_locations(arguments_node)


@step_decorator
def script(f, script_rewriter=ScriptRewriter, script_class=Script):
    """
    Rewrite the function as a Script
    remember Signature.replace
    """
    return functools.wraps(f)(script_class(f, step_rewriter=script_rewriter))
