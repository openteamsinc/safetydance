class StepExtension:
    """Extensions to step execution should **must** subclass this class and override one
    or more of the methods it defines.
    """

    def __enter__(self, context: "safetydance.Context", step: "safetydance.Step"):
        """This method will be executed before the step is executed."""
        ...

    def __exit__(self, context: "safetydance.Context", step: "safetydance.Step"):
        """This method will be executed following step execution."""
        ...


STEP_EXTENSION_REGISTRY = []


def register_step_extension(step_extension: StepExtension):
    STEP_EXTENSION_REGISTRY.append(step_extension)


def enter_step(context: "safetydance.Context", step: "safetydance.Step"):
    for extension in STEP_EXTENSION_REGISTRY:
        extension.__enter__(context, step)


def exit_step(context: "safetydance.Context", step: "safetydance.Step"):
    for extension in reversed(STEP_EXTENSION_REGISTRY):
        extension.__exit__(context, step)
