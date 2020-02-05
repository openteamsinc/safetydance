from safetydance import Context, script, step, step_data, Step
from safetydance.extensions import (
    register_step_extension,
    StepExtension,
    STEP_EXTENSION_REGISTRY,
)


One = step_data(int)
Two = step_data(str)
Three = step_data(int)


@step
def step_one():
    One = 1
    Two = "2"


@step
def step_two():
    Three = One + int(Two)


@script
def script_for_testing():
    step_one()
    step_two()


class ExtensionOne(StepExtension):
    def __init__(self):
        self.entered = False
        self.exited = False

    def __enter__(self, context: Context, step: Step):
        assert context is not None
        assert step is not None
        self.entered = True

    def __exit__(self, context, step):
        assert context is not None
        assert step is not None
        self.exited = True

    def assert_was_called_for_all(self):
        assert self.entered
        assert self.exited


def test_simple_extension():
    STEP_EXTENSION_REGISTRY.clear()
    extension = ExtensionOne()
    register_step_extension(extension)
    script_for_testing()
    extension.assert_was_called_for_all()
    print(script_for_testing)
    script_for_testing()


class ExtensionLayer(StepExtension):
    def __init__(self, trace, name):
        self.trace = trace
        self.name = name

    def __enter__(self, context, step):
        self.trace.append(f"-> {self.name} {step}")

    def __exit__(self, context, step):
        self.trace.append(f"<- {self.name} {step}")


def test_multiple_extensions():
    STEP_EXTENSION_REGISTRY.clear()
    trace = []
    extension_one = ExtensionLayer(trace, "one")
    extension_two = ExtensionLayer(trace, "two")
    register_step_extension(extension_one)
    register_step_extension(extension_two)
    script_for_testing()
    from pprint import pprint

    pprint(trace)
    for i, value in enumerate(
        [
            f"-> one {script_for_testing}",
            f"-> two {script_for_testing}",
            f"-> one {step_one}",
            f"-> two {step_one}",
            f"<- two {step_one}",
            f"<- one {step_one}",
            f"-> one {step_two}",
            f"-> two {step_two}",
            f"<- two {step_two}",
            f"<- one {step_two}",
            f"<- two {script_for_testing}",
            f"<- one {script_for_testing}",
        ]
    ):
        assert trace[i] == value
