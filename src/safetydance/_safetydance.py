from ast import (
    alias,
    arg,
    Attribute,
    copy_location,
    Call,
    fix_missing_locations,
    Index,
    ImportFrom,
    Load,
    Module,
    Name,
    NameConstant,
    NodeTransformer,
    parse,
    Str,
    Subscript,
)
from astor import code_to_ast
from dataclasses import dataclass
from importlib import import_module
from inspect import getclosurevars, getmodule
from typing import Any, Callable, Dict, Type, TypeVar, Generic
from .extensions import enter_step, exit_step
import functools
import inspect


def step_decorator(f):
    f.is_step_decorator = True
    return f


T = TypeVar("T")


@dataclass(frozen=True)
class ContextKey(Generic[T]):
    datatype: T
    description: str
    initializer: Callable[["Context"], T]


def step_data(
    key_type: Type,
    description: str = None,
    initializer: Callable[["Context"], Type] = None,
):
    return ContextKey(key_type, description, initializer)


class Context(Dict[ContextKey, Any]):
    def __getitem__(self, key: ContextKey):
        """
        A ``Context`` differs from a plain ``Dict`` in that it will initialize a key
        with a default value if the key defines a default value initializer.
        """
        if key not in self and key.initializer is not None:
            initial_value = key.initializer(self)
            self[key] = initial_value
        return super().__getitem__(key)


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
        __tracebackhide__ = True
        if self.f is None:
            self.rewrite()
        enter_step(context, self)
        self.f(context, *args, **kwargs)
        exit_step(context, self)

    def rewrite(self):
        if hasattr(self.f_original, "__rewritten_step__"):
            self.f = self.f_original.__rewritten_step__
            return
        in_tree = code_to_ast(self.f_original)
        filename, lineno = code_to_ast.get_file_info(self.f_original)
        out_tree = self.step_rewriter(self.f_original).visit(in_tree)
        new_func_name = self.f_original.__name__
        func_scope = self.f_original.__globals__
        if "Context" not in self.f_original.__globals__:
            self.f_original.__globals__["Context"] = Context
        # Compile the new function in the old function's scope. If we don't change the
        # name, this actually overrides the old function with the new one
        if not isinstance(out_tree, Module):
            out_tree = Module(body=[out_tree])
        exec(compile(out_tree, f"{filename}", "exec"), func_scope)
        self.f = func_scope[new_func_name]
        self.f.IsStep = True
        setattr(self.f_original, "__rewritten_step__", self.f)

        # make sure that the function hasn't been overwritten due to the reparsing of
        # the source file.
        m = import_module(self.__module__)
        setattr(m, self.__name__, self)


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

    def is_step_decorator(self, decorator):
        if not hasattr(decorator, "id"):
            return False
        decorator = self.f.__globals__.get(decorator.id)
        return hasattr(decorator, "is_step_decorator")

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        node.decorator_list = [
            decorator
            for decorator in node.decorator_list
            if not self.is_step_decorator(decorator)
        ]
        node.body = [self.step_body_rewriter.visit(n) for n in node.body]
        return fix_missing_locations(node)


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
        __tracebackhide__ = True
        if self.f is None:
            self.rewrite()
        context = NestingContext()
        if "context" in kwargs:
            context.parent = kwargs["context"]
        kwargs["context"] = context
        enter_step(context, self)
        self.f(*args, **kwargs)
        exit_step(context, self)


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
            if hasattr(resolved_callable, "IsStep"):
                new_args = [copy_location(Name("context", Load()), call)]
                new_args.extend(call.args)
                return fix_missing_locations(
                    copy_location(Call(call.func, new_args, call.keywords), call)
                )
            else:
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
                return node
            else:
                return fix_missing_locations(
                    copy_location(
                        Subscript(
                            value=Name(id="context", ctx=Load()),
                            slice=Index(value=Name(id=node.id, ctx=Load())),
                            ctx=node.ctx,
                        ),
                        node,
                    )
                )
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
