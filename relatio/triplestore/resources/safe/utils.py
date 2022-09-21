
from typing import Callable, Optional


def get_safe_class(class_name:        str, 
                   class_model:       type, 
                   super_class:       type, 
                   super_super_class: Optional[type]     = None,
                   __new__:           Optional[Callable] = None):

    # Get class inheritance order
    bases = (super_class,)
    if super_super_class is not None:
        bases += ( super_super_class, *super_super_class.__bases__ )
    
    if __new__ is None:
        def __new__(cls, label, **kwargs):
            # Check arguments types
            _ = class_model(label=label, **kwargs)
            return super(safe_class, cls).__new__(cls, label, **kwargs)

    safe_class = type(class_name, bases, { '__new__': __new__ })
    return safe_class
