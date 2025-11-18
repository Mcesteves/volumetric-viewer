import os

import numpy as np

from volumetric_viewer.data_type_enum import DataType
from volumetric_viewer.raw_parser import RawParser


class RawReader:
    """
    High-level interface for reading and representing volumetric data
    from binary `.raw` files.

    This class internally uses :class:`~volumetric_viewer.raw_parser.RawParser`
    to load the binary data and extract its metadata (dimensions, data type, etc.).

    It also provides convenience properties for voxel spacing and dimension handling.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize a :class:`RawReader` instance and load the specified `.raw` file.

        :param file_path: Path to the `.raw` binary file.
        :type file_path: str
        :raises FileNotFoundError: If the specified file does not exist.
        :raises NameError: If the filename does not follow the expected naming convention.
        :raises ValueError: If the file size does not match the inferred dimensions.
        """
        self._raw_file_path: str = file_path
        self._dimension: int
        self._spacing_x: float
        self._spacing_y: float
        self._spacing_z: float

        self._dim_x: int
        self._dim_y: int
        self._dim_z: int

        self._d_type: DataType
        self._data: np.ndarray

        self._load_raw()

    def _load_raw(self) -> None:
        """
        Load the raw volumetric data and initialize internal attributes.

        This method validates the file path, invokes :class:`RawParser` to
        read the binary data, and sets up volume metadata such as shape,
        data type, and voxel spacing.

        :raises FileNotFoundError: If the `.raw` file does not exist.
        """
        if not os.path.exists(self._raw_file_path):
            raise FileNotFoundError(f"Raw file not found: {self._raw_file_path}")
        
        raw_parser = RawParser(self._raw_file_path)
        self._data = raw_parser.read_data()
        self._dim_x = raw_parser.dim_x
        self._dim_y = raw_parser.dim_y
        self._dim_z = raw_parser.dim_z
        self._d_type = raw_parser.d_type

        # Default voxel spacing (can't be overwritten for now)
        self._spacing_x = 1.0
        self._spacing_y = 1.0
        self._spacing_z = 1.0
        self._dimension = 3

    # ======================
    #   Public Properties
    # ======================

    @property
    def dimension(self) -> int:
        """
        Number of dimensions in the loaded volume (always 3).

        :returns: Dimensionality of the volume.
        :rtype: int
        """
        return self._dimension

    @property
    def spacing_x(self) -> float:
        """
        Voxel spacing along the X axis.

        :returns: Spacing value along the X axis.
        :rtype: float
        """
        return self._spacing_x

    @property
    def spacing_y(self) -> float:
        """
        Voxel spacing along the Y axis.

        :returns: Spacing value along the Y axis.
        :rtype: float
        """
        return self._spacing_y

    @property
    def spacing_z(self) -> float:
        """
        Voxel spacing along the Z axis.

        :returns: Spacing value along the Z axis.
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
        Data type of the volume (e.g., ``UINT8``, ``FLOAT32``).

        :returns: The data type of the volume.
        :rtype: DataType
        """
        return self._d_type

    @property
    def data(self) -> np.ndarray:
        """
        The volumetric data loaded from the `.raw` file.

        :returns: Raw volumetric data as a NumPy array.
        :rtype: numpy.ndarray
        """
        return self._data

    @property
    def shape(self) -> tuple[int, int, int]:
        """
        Shape of the volumetric dataset.

        :returns: The volume shape as ``(dim_x, dim_y, dim_z)``.
        :rtype: tuple[int, int, int]
        """
        return self._dim_x, self._dim_y, self._dim_z

    @property
    def spacing(self) -> tuple[float, float, float]:
        """
        Voxel spacing in each spatial dimension.

        :returns: Spacing tuple ``(spacing_x, spacing_y, spacing_z)``.
        :rtype: tuple[float, float, float]
        """
        return self._spacing_x, self._spacing_y, self._spacing_z

    def __repr__(self) -> str:
        """
        Return a concise string representation of the :class:`RawReader` instance.

        :returns: A string describing the volume dimensions, spacing, and data type.
        :rtype: str
        """
        return (
            f"<RawReader dims=({self.dim_x}, {self.dim_y}, {self.dim_z}) "
            f"spacing=({self.spacing_x}, {self.spacing_y}, {self.spacing_z}) "
            f"type={self.d_type}>"
        )
