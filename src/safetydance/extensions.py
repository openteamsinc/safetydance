import cProfile
import pstats
import io
import psutil
import configparser

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

        
class toggle_profiles(StepExtension):
    def __enter__(context: "safetydance.Context", step: "safetydance.Step"):

        global profile
        global qualified_func_names

        try:
            len(qualified_func_names)
        except:
            qualified_func_names = []
            config = configparser.ConfigParser()
            config.read("config_file.ini")
            for x in config['PROFILED']:
                if config['PROFILED'][x] == 'True':
                    qualified_func_names.append(x)
        
        try:
            len(profile)
        except:
            profile = []
            
        if f'{step.__module__}.{step.__name__}' in qualified_func_names:
            print(f"===Profiling enabled for {step.__name__}===")
            profile.append(cProfile.Profile())
            profile[-1].enable()
    
    def __exit__(context: "safetydance.Context", step: "safetydance.Step"):
        if f'{step.__module__}.{step.__name__}' in qualified_func_names:
            print(f"Printing profiling collected for {step.__name__}:")
            try: 
                profile_pop = profile.pop()
                profile_pop.disable()
            finally:
                s = io.StringIO()
                ps = pstats.Stats(profile_pop, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
                ps.print_stats()
                print(s.getvalue())
            
            p = psutil.Process()
            with p.oneshot():
                print(f"Memory: {p.memory_full_info()} \n")


STEP_EXTENSION_REGISTRY = []


def register_step_extension(step_extension: StepExtension):
    STEP_EXTENSION_REGISTRY.append(step_extension)

def enter_step(context: "safetydance.Context", step: "safetydance.Step"):
    for extension in STEP_EXTENSION_REGISTRY:
        extension.__enter__(context, step)


def exit_step(context: "safetydance.Context", step: "safetydance.Step"):
    for extension in reversed(STEP_EXTENSION_REGISTRY):
        extension.__exit__(context, step)
