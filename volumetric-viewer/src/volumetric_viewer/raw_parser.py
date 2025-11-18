import re

import numpy as np

from volumetric_viewer.data_type_enum import DataType


class RawParser:
    """
    Loads binary `.raw` volumetric files using filename conventions
    to infer the volume shape and data type.

    The filename must follow the format: ``{X}x{Y}x{Z}_{DATATYPE}.raw``  
    Example: ``128x128x64_uint8.raw``
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize the :class:`RawParser` with the path to a `.raw` file.

        :param file_path: Path to the `.raw` binary file.
        :type file_path: str
        :raises NameError: If the filename format is invalid and does not match the required pattern.
        """
        self._file_path: str = file_path
        self._dim_x: int
        self._dim_y: int
        self._dim_z: int
        self._d_type: DataType
        self._data: np.ndarray | None = None

        match = re.search(r"(\d+)x(\d+)x(\d+)_([a-zA-Z0-9]+)\.raw$", self._file_path)
        if match:
            self._dim_x, self._dim_y, self._dim_z = map(int, match.group(1, 2, 3))
            self._d_type = DataType.from_string(match.group(4))
        else:
            raise NameError("Invalid file name format. Expected: {X}x{Y}x{Z}_{DATATYPE}.raw")

    def read_data(self) -> np.ndarray:
        """
        Read the binary `.raw` file and return its contents as a NumPy array.

        :raises FileNotFoundError: If the file does not exist.
        :raises ValueError: If the read data size does not match the expected volume shape.
        :returns: The volumetric data read from the file.
        :rtype: numpy.ndarray
        """
        try:
            self._data = np.fromfile(self._file_path, dtype=self._d_type.value)
        except FileNotFoundError as err:
            raise FileNotFoundError(f"Raw file not found: {self._file_path}") from err

        expected_size = self._dim_x * self._dim_y * self._dim_z
        if self._data.size != expected_size:
            raise ValueError(
                f"Unexpected file size: expected {expected_size} elements, got {self._data.size}"
            )

        self._data = self._data.reshape((self._dim_x, self._dim_y, self._dim_z))
        return self._data

    # ======================
    #   Public Properties
    # ======================

    @property
    def data(self) -> np.ndarray | None:
        """
        The loaded volumetric data, or ``None`` if it has not yet been loaded.

        :returns: Loaded NumPy array or ``None``.
        :rtype: numpy.ndarray | None
        """
        return self._data

    @property
    def dim_x(self) -> int:
        """
        The volume size along the X axis.

        :returns: Size along X.
        :rtype: int
        """
        return self._dim_x

    @property
    def dim_y(self) -> int:
        """
        The volume size along the Y axis.

        :returns: Size along Y.
        :rtype: int
        """
        return self._dim_y

    @property
    def dim_z(self) -> int:
        """
        The volume size along the Z axis.

        :returns: Size along Z.
        :rtype: int
        """
        return self._dim_z

    @property
    def shape(self) -> tuple[int, int, int]:
        """
        The shape of the volume as a tuple ``(dim_x, dim_y, dim_z)``.

        :returns: Volume shape.
        :rtype: tuple[int, int, int]
        """
        return self._dim_x, self._dim_y, self._dim_z

    @property
    def d_type(self) -> DataType:
        """
        The data type of the volume (e.g., ``UINT8``, ``FLOAT32``).

        :returns: The volume's data type.
        :rtype: DataType
        """
        return self._d_type

    @property
    def file_path(self) -> str:
        """
        The path to the `.raw` file.

        :returns: File path.
        :rtype: str
        """
        return self._file_path

    def __repr__(self) -> str:
        """
        Return a concise string representation of the :class:`RawParser` instance.

        :returns: A formatted string describing the instance.
        :rtype: str
        """
        return (
            f"<RawParser shape=({self._dim_x}, {self._dim_y}, {self._dim_z}) "
            f"type={self._d_type} path={self._file_path}>"
        )
