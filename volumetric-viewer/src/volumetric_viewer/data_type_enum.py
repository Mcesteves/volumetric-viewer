from enum import Enum

import numpy as np


class DataType(Enum):
    UINT8 = np.uint8
    INT8 = np.int8
    UINT16 = np.uint16
    INT16 = np.int16
    UINT32 = np.uint32
    INT32 = np.int32
    UINT64 = np.uint64
    INT64 = np.int64
    FLOAT16 = np.float16
    FLOAT32 = np.float32
    FLOAT64 = np.float64
    BOOL = np.bool_

    @classmethod
    def from_string(cls, name: str):
        """
        Converts a string (case-insensitive) into the corresponding DataType.
        Raises ValueError if the name is invalid.
        """
        try:
            return cls[name.upper()]
        except KeyError as err:
            raise ValueError(
                f"Invalid type '{name}'. Valid types are: {', '.join(cls.list())}"
            ) from err