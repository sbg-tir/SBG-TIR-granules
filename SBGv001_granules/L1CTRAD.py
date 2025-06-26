from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import datetime
from glob import glob
from os import makedirs
from os.path import exists, abspath, expanduser, dirname, join, basename, splitext
from typing import Union, List, Any

import numpy as np

import rasters as rt
import rasters
from rasters import Raster, MultiRaster, RasterGeometry, RasterGrid, KDTree
import colored_logging as cl

from .granule import ECOSTRESSGranule
from .tiled_granule import ECOSTRESSTiledGranule

__author__ = "Gregory Halverson"

from .write_XML_metadata import write_XML_metadata

logger = logging.getLogger(__name__)

PRIMARY_VARIABLE = "false_color"
PRODUCT_METADATA_GROUP = "L1B_RADMetadata"
GRID_NAME = "ECO_L1CG_RAD_70m"

L1CG_RAD_SHORT_NAME = "ECO_L1CG_RAD"
L1CG_RAD_LONG_NAME = "ECOSTRESS Gridded Top of Atmosphere Calibrated Radiance Instantaneous L1CG Global 70 m"

L1CT_RAD_SHORT_NAME = "ECO_L1CT_RAD"
L1CT_RAD_LONG_NAME = "ECOSTRESS Tiled Top of Atmosphere Calibrated Radiance Instantaneous L1CT Global 70 m"

TILED_OUTPUT_VARIABLES = [
    "cloud",
    "water",
    "radiance_1",
    "data_quality_1",
    "radiance_2",
    "data_quality_2",
    "radiance_3",
    "data_quality_3",
    "radiance_4",
    "data_quality_4",
    "radiance_5",
    "data_quality_5"
]


class L1RADGranule(ECOSTRESSGranule):
    _PRIMARY_VARIABLE = PRIMARY_VARIABLE
    _PRODUCT_METADATA_GROUP = PRODUCT_METADATA_GROUP

    def __init__(self, product_filename: str):
        ECOSTRESSGranule.__init__(self, product_filename=product_filename)

    def radiance(self, band: int, apply_cloud: bool = False) -> Raster:
        if band not in range(1, 6):
            raise ValueError(f"invalid radiance band: {band}")

        radiance = self.variable(f"radiance_{band}", apply_cloud=apply_cloud)

        return radiance

    @property
    def false_color(self) -> MultiRaster:
        band_5 = self.radiance(5, apply_cloud=False)
        band_4 = self.radiance(4, apply_cloud=False)
        band_2 = self.radiance(2, apply_cloud=False)
        false_color = MultiRaster.stack([band_5, band_4, band_2])

        return false_color

    def variable(
            self,
            variable_name: str,
            apply_scale: bool = True,
            apply_cloud: bool = True,
            geometry: RasterGeometry = None,
            fill_value: Any = None,
            kd_tree: KDTree = None,
            **kwargs):
        if self.data_group_name is None:
            raise ValueError("no data group name")

        if variable_name == "water":
            data = self.water.astype(np.uint8)
            fill_value = 0
        elif variable_name == "cloud":
            data = self.cloud.astype(np.uint8)
            fill_value = 0
        elif variable_name == "false_color":
            data = self.false_color.astype(np.float32)
        else:
            if "quality" in variable_name:
                apply_scale = False
                apply_cloud = False

            data = self.data(
                dataset_name=f"{self.data_group_name}/{variable_name}",
                apply_scale=apply_scale,
                apply_cloud=apply_cloud
            )

        if geometry is not None:
            gridded_data = data.resample(target_geometry=geometry, nodata=fill_value, kd_tree=kd_tree)
            data = gridded_data.astype(data.dtype)

        return data

class L1CTRAD(ECOSTRESSTiledGranule, L1RADGranule):
    _PRODUCT_NAME = "L1CT_RAD"
    _PRODUCT_METADATA_GROUP = "ProductMetadata"

    def __init__(
            self,
            product_location: str = None,
            orbit: int = None,
            scene: int = None,
            tile: str = None,
            time_UTC: Union[datetime, str] = None,
            build: str = None,
            process_count: int = None,
            containing_directory: str = None,
            **kwargs):
        L1RADGranule.__init__(self, product_filename=product_location)
        ECOSTRESSTiledGranule.__init__(
            self,
            product_location=product_location,
            orbit=orbit,
            scene=scene,
            tile=tile,
            time_UTC=time_UTC,
            build=build,
            process_count=process_count,
            containing_directory=containing_directory,
            **kwargs
        )

        self._water = None
        self._cloud = None

    @property
    def filename(self) -> str:
        return self.product_location

    @property
    def geometry(self) -> RasterGrid:
        if self._geometry is not None:
            return self._geometry

        URI = self.layer_URI("radiance_5")
        grid = RasterGrid.open(URI)

        return grid

    @property
    def variables(self) -> List[str]:
        return [
            "radiance_1",
            "radiance_2",
            "radiance_3",
            "radiance_4",
            "radiance_5",
            "data_quality_1",
            "data_quality_2",
            "data_quality_3",
            "data_quality_4",
            "data_quality_5"
            "water",
            "cloud"
        ]

    @property
    def water(self) -> Raster:
        if self._water is None:
            self._water = self.variable(variable="water")

        return self._water

    @property
    def cloud(self) -> Raster:
        if self._cloud is None:
            self._cloud = self.variable(variable="cloud")

        return self._cloud

    def variable(self, variable: str, geometry: RasterGeometry = None, **kwargs) -> Raster:
        if variable == "false_color":
            return self.false_color

        return ECOSTRESSTiledGranule.variable(self, variable=variable, geometry=geometry)
