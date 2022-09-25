
from ...utils import MULTIPROCESSING

# Appropriate import depending on the use of multiprocessing (or not)
if MULTIPROCESSING:
    from .utils.multiprocessing import build_resources as build_sp_resources
else:
    from .utils import build_resources as build_sp_resources
