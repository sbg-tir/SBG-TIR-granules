from os.path import basename, splitext
import logging

import colored_logging as cl

from .granule import ECOSTRESSGranule
from .L1CTRAD import L1CTRAD
from .L2TLSTE import L2TLSTE
from .L2TSTARS import L2TSTARS

## FIXME include L4T ETAUX

from .L4TJET import L4TJET
from .L4TESI import L4TESI
from .L4TWUE import L4TWUE

logger = logging.getLogger(__name__)

def open_granule(
        filename: str,
        L2_CLOUD_filename: str = None,
        L1B_GEO_filename: str = None,
        **kwargs) -> ECOSTRESSGranule:
    filename_base = splitext(basename(filename))[0]

    if filename_base.startswith("ECOv003_L1CT_RED"):
        logger.info(f"loading Collection 2 L1CT RAD: {cl.file(filename)}")
        return L1CTRAD(filename, **kwargs)
    elif filename_base.startswith("ECOv003_L2T_LSTE"):
        logger.info(f"loading Collection 2 L2T LSTE: {cl.file(filename)}")
        return L2TLSTE(filename, **kwargs)
    elif filename_base.startswith("ECOv003_L2T_STARS"):
        logger.info(f"loading Collection 2 L2T STARS: {cl.file(filename)}")
        return L2TSTARS(filename, **kwargs)
    elif filename_base.startswith("ECOv003_L3T_JET"):
        logger.info(f"loading Collection 2 L3T JET: {cl.file(filename)}")
        return L4TJET(filename, **kwargs)
    
    ## FIXME include L4T ETAUX

    elif filename_base.startswith("ECOv003_L4T_ESI"):
        logger.info(f"loading Collection 2 L4T ESI: {cl.file(filename)}")
        return L4TESI(filename, **kwargs)
    elif filename_base.startswith("ECOv003_L4T_WUE"):
        logger.info(f"loading Collection 2 L4T WUE: {cl.file(filename)}")
        return L4TWUE(filename, **kwargs)
    