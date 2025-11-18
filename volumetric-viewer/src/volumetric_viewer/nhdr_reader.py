import os
from typing import Any

import nrrd
import numpy as np

from volumetric_viewer.data_type_enum import DataType
from volumetric_viewer.raw_parser import RawParser


class NHDRReader:
    """
    Reads NHDR (Nearly Raw Raster Data Header) files and their associated
    RAW data files, extracting metadata and volume data into memory.

    This class parses both the `.nhdr` header and the corresponding `.raw` data file,
    using :class:`~volumetric_renderer.raw_parser.RawParser` to load the binary data.

    It supports validation of volume dimensions, voxel spacing, and data types.

    **Example:**

    .. code-block:: python

        from volumetric_renderer.nhdr_reader import NHDRReader

        reader = NHDRReader("data/brain_scan.nhdr")

        volume = reader.data           # Raw NumPy array
        shape = reader.shape           # (x, y, z)
        spacing = reader.spacing       # (sx, sy, sz)
        dtype = reader.d_type          # e.g. DataType.UINT8
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize an :class:`NHDRReader` instance and parse the associated NHDR and RAW files.

        :param file_path: Path to the `.nhdr` file.
        :type file_path: str
        :raises FileNotFoundError: If the NHDR file or associated RAW file does not exist.
        :raises ValueError: If any required metadata field is missing or invalid.
        """
        self._nhdr_file_path: str = file_path
        self._data_file: str

        self._dimension: int
        self._spacing_x: float
        self._spacing_y: float
        self._spacing_z: float

        self._dim_x: int
        self._dim_y: int
        self._dim_z: int

        self._d_type: DataType
        self._data: np.ndarray

        self._load_nhdr()

    def _load_nhdr(self) -> None:
        """
        Load the NHDR file, parse its metadata fields, and read the associated RAW data.

        :raises FileNotFoundError: If the NHDR file or the referenced RAW file does not exist.
        :raises ValueError: If any required metadata field is missing or malformed.
        """
        if not os.path.exists(self._nhdr_file_path):
            raise FileNotFoundError(f"NHDR file not found: {self._nhdr_file_path}")

        _, header = nrrd.read(self._nhdr_file_path)

        self._parse_dimension(header)
        self._parse_data_file(header)
        self._parse_spacing(header)
        self._parse_sizes(header)
        self._parse_data_type(header)

        if not os.path.exists(self._data_file):
            raise FileNotFoundError(f"Raw data file not found: {self._data_file}")

        self._data = RawParser(self._data_file).read_data()

    def _parse_dimension(self, header: dict[str, Any]) -> None:
        """
        Parse and validate the ``dimension`` field from the NHDR header.

        :param header: Parsed NHDR header dictionary.
        :type header: dict[str, Any]
        :raises ValueError: If the volume dimension is not equal to 3 (required for 3D volumes).
        """
        self._dimension = int(header.get("dimension", 0))
        if self._dimension != 3:
            raise ValueError(f"Unsupported volume dimension: {self._dimension}")

    def _parse_data_file(self, header: dict[str, Any]) -> None:
        """
        Parse the ``data file`` field and resolve the absolute path to the associated RAW file.

        :param header: Parsed NHDR header dictionary.
        :type header: dict[str, Any]
        :raises ValueError: If the ``data file`` field is missing or invalid.
        """
        data_file_name = header.get("data file")
        if not data_file_name:
            raise ValueError("Missing 'data file' in NHDR header")

        if not os.path.isabs(data_file_name):
            nhdr_dir = os.path.dirname(self._nhdr_file_path)
            self._data_file = os.path.join(nhdr_dir, data_file_name)
        else:
            self._data_file = data_file_name

    def _parse_spacing(self, header: dict[str, Any]) -> None:
        """
        Parse the ``space directions`` field to extract voxel spacing.

        :param header: Parsed NHDR header dictionary.
        :type header: dict[str, Any]
        :raises ValueError: If the ``space directions`` field is missing or malformed.
        """
        space_directions = header.get("space directions")
        if space_directions is None or len(space_directions) != 3:
            raise ValueError("Invalid or missing 'space directions' in NHDR header")

        self._spacing_x = float(space_directions[0][0])
        self._spacing_y = float(space_directions[1][1])
        self._spacing_z = float(space_directions[2][2])

    def _parse_sizes(self, header: dict[str, Any]) -> None:
        """
        Parse the ``sizes`` field to extract the volume dimensions (X, Y, Z).

        :param header: Parsed NHDR header dictionary.
        :type header: dict[str, Any]
        :raises ValueError: If the ``sizes`` field is missing or malformed.
        """
        sizes = header.get("sizes")
        if sizes is None or len(sizes) != 3:
            raise ValueError("Invalid or missing 'sizes' in NHDR header")

        self._dim_x = int(sizes[0])
        self._dim_y = int(sizes[1])
        self._dim_z = int(sizes[2])

    def _parse_data_type(self, header: dict[str, Any]) -> None:
        """
        Parse the ``type`` field and map it to a :class:`~volumetric_renderer.data_type_enum.DataType`.

        :param header: Parsed NHDR header dictionary.
        :type header: dict[str, Any]
        :raises ValueError: If the ``type`` field is missing or unsupported.
        """
        type_str = header.get("type")
        if not type_str:
            raise ValueError("Missing 'type' in NHDR header")

        self._d_type = DataType.from_string(type_str)

    # ======================
    #   Public Properties
    # ======================

    @property
    def dimension(self) -> int:
        """
        Number of dimensions in the loaded volume (always 3).

        :returns: Volume dimensionality.
        :rtype: int
        """
        return self._dimension

    @property
    def spacing_x(self) -> float:
        """
        Voxel spacing along the X axis.

        :returns: Spacing value along X.
        :rtype: float
        """
        return self._spacing_x

    @property
    def spacing_y(self) -> float:
        """
        Voxel spacing along the Y axis.

        :returns: Spacing value along Y.
        :rtype: float
        """
        return self._spacing_y

    @property
    def spacing_z(self) -> float:
        """
        Voxel spacing along the Z axis.

        :returns: Spacing value along Z.
        :rtype: float
        """
        return self._spacing_z

    @property
    def dim_x(self) -> int:
        """
        Volume size along the X axis.

        :returns: Number of voxels along X.
        :rtype: int
        """
        return self._dim_x

    @property
    def dim_y(self) -> int:
        """
        Volume size along the Y axis.

        :returns: Number of voxels along Y.
        :rtype: int
        """
        return self._dim_y

    @property
    def dim_z(self) -> int:
        """
        Volume size along the Z axis.

        :returns: Number of voxels along Z.
        :rtype: int
        """
        return self._dim_z

    @property
    def d_type(self) -> DataType:
        """
        Data type of the volumetric data (e.g., ``UINT8``, ``FLOAT32``).

        :returns: Data type of the volume.
        :rtype: DataType
        """
        return self._d_type

    @property
    def data(self) -> np.ndarray:
        """
        The volumetric data loaded from the associated RAW file.

        :returns: Loaded volume data.
        :rtype: numpy.ndarray
        """
        return self._data

    @property
    def data_file_path(self) -> str:
        """
        Absolute path to the associated RAW data file.

        :returns: Path to the `.raw` file.
        :rtype: str
        """
        return self._data_file

    @property
    def shape(self) -> tuple[int, int, int]:
        """
        Shape of the volume as ``(dim_x, dim_y, dim_z)``.

        :returns: Volume shape.
        :rtype: tuple[int, int, int]
        """
        return self._dim_x, self._dim_y, self._dim_z

    @property
    def spacing(self) -> tuple[float, float, float]:
        """
        Voxel spacing along each axis.

        :returns: Spacing tuple ``(spacing_x, spacing_y, spacing_z)``.
        :rtype: tuple[float, float, float]
        """
        return self._spacing_x, self._spacing_y, self._spacing_z

    def __repr__(self) -> str:
        """
        Return a concise string representation of the :class:`NHDRReader` instance.

        :returns: A string summarizing volume metadata.
        :rtype: str
        """
        return (
            f"<NHDRReader dims=({self.dim_x}, {self.dim_y}, {self.dim_z}) "
            f"spacing=({self.spacing_x}, {self.spacing_y}, {self.spacing_z}) "
            f"type={self.d_type}>"
        )
