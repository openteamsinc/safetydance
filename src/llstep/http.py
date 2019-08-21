from llstep import bdd, step


@extension
@step
def get(self: bdd.StepLeader, context: Context, url: str):
    print(f"GET {url}")
