from ast import NodeTransformer
import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

STEPBODY_EXTENSION_REGISTRY = []

def register_stepbody_extension(extension: NodeTransformer):
    '''Takes in a valid node transformer and then injects the methods
    whose code is in NodeTransformer and then into the method for visiting
    a Node.  
    '''
    logger.debug(f'You are registering a stepbody extension named: { extension.__name__ }\n'
                 f'Before rewrite, the current length is { len(STEPBODY_EXTENSION_REGISTRY) }')
    STEPBODY_EXTENSION_REGISTRY.append(extension)
    #logger.info(f'The size after adding extension { extension.__name__ } the registry is { len(STEPBODY_EXTENSION_REGISTRY) }')
