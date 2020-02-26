STEPBODY_EXTENSION_REGISTRY = []

def register_stepbody_extension(extension: NodeTransformer):
    '''Takes in a valid node transformer and then injects the methods
    whose code is in NodeTransformer and then into the method for visiting
    a Node.  
    '''
    print(f'You are registering a stepbody extension.'
          f'Before rewrite, the current length is { len(STEPBODY_EXTENSION_REGISTRY) }')
    STEPBODY_EXTENSION_REGISTRY.append(extension)
    print(f'The size after adding the registry is { len(STEPBODY_EXTENSION_REGISTRY) }')
