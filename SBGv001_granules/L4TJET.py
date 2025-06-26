import json
import logging
from os.path import exists

from rasters import Raster

from .colors import ET_COLORMAP
from .tiled_granule import ECOSTRESSTiledGranule

GRANULE_PREVIEW_CMAP = ET_COLORMAP

class L4JET:
    logger = logging.getLogger(__name__)

    _DATA_GROUP_NAME = "EVAPOTRANSPIRATION PT-JPL"
    _PRODUCT_METADATA_GROUP = "L3_ET_PT-JPL Metadata"
    _GRANULE_PREVIEW_CMAP = GRANULE_PREVIEW_CMAP

    def __init__(
            self,
            L3_ET_PTJPL_filename: str,
            L2_CLOUD_filename: str = None,
            L1B_GEO_filename: str = None,
            **kwargs):
        super().__init__(
            product_filename=L3_ET_PTJPL_filename,
            L2_CLOUD_filename=L2_CLOUD_filename,
            L1B_GEO_filename=L1B_GEO_filename,
            data_group_name=self._DATA_GROUP_NAME,
            product_metadata_group_name=self._PRODUCT_METADATA_GROUP,
            **kwargs
        )

        if not exists(L3_ET_PTJPL_filename):
            raise IOError(f"L3 PTJPLSM file does not exist: {L3_ET_PTJPL_filename}")

    def __repr__(self):
        display_dict = {
            "L3 PT-JPL": self.product_filename,
            "L2 CLOUD:": self.L2_CLOUD_filename,
            "L1B GEO:": self.L1B_GEO_filename
        }

        display_string = f"L3 PT-JPL Granule\n{json.dumps(display_dict, indent=2)}"


        return display_string

    @property
    def BESSinst(self) -> Raster:
        return self.variable("BESSinst", cmap=ET_COLORMAP)

    @property
    def ETdaily(self) -> Raster:
        return self.variable("ETdaily", cmap=ET_COLORMAP)
    
    @property
    def MOD16inst(self) -> Raster:
        return self.variable("MOD16inst", cmap=ET_COLORMAP)
    
    @property
    def PTJPLSMinst(self) -> Raster:
        return self.variable("PTJPLSMinst", cmap=ET_COLORMAP)
    
    @property
    def PTJPLSMcanopy(self) -> Raster:
        return self.variable("PTJPLSMcanopy", cmap=ET_COLORMAP)

    @property
    def PTJPLSMsoil(self) -> Raster:
        return self.variable("PTJPLSMsoil", cmap=ET_COLORMAP)

    @property
    def PTJPLSMinterception(self) -> Raster:
        return self.variable("PTJPLSMinterception", cmap=ET_COLORMAP)

    @property
    def STICinst(self) -> Raster:
        return self.variable("STICinst", cmap=ET_COLORMAP)

    @property
    def STICcanopy(self) -> Raster:
        return self.variable("STICcanopy", cmap=ET_COLORMAP)

    @property
    def ETinst(self) -> Raster:
        return self.variable("ETinst", cmap=ET_COLORMAP)

    @property
    def LE(self) -> Raster:
        return self.ETinst

    @property
    def ETinst_kg(self) -> Raster:
        return self.ETinst / 2450000.0


class L4TJET(ECOSTRESSTiledGranule, L4JET):
    _PRIMARY_VARIABLE = "ETdaily"
    _PRODUCT_NAME = "L4T_JET"
