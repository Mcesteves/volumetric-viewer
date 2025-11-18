import hashlib
from pathlib import Path

import numpy as np

from volumetric_viewer.data_type_enum import DataType
from volumetric_viewer.nhdr_reader import NHDRReader


def test_should_read_nrrd_files() -> None:
    current_dir = Path(__file__).parent
    tooth_file = (current_dir / ".." / "data" / "tooth.nhdr").resolve()

    reader = NHDRReader(str(tooth_file))

    assert reader.dimension == 3
    assert reader.spacing_x == 1.0
    assert reader.spacing_y == 1.0
    assert reader.spacing_z == 1.0

    assert reader.dim_x == 103
    assert reader.dim_y == 94
    assert reader.dim_z == 161

    assert reader.d_type == DataType.UINT8
    assert isinstance(reader.data, np.ndarray)

    # Integrity check via SHA-512
    expected_sha512 = (
        "5ee3d77ae951e129d29062a4fd4d8730fd8670bdaf4d01ddf907848072180cbf"
        "ea8ab897880147d2a79dc7f1d1806a34b32853074eca88f6758e01382469f9f6"
    )

    actual_sha512 = hashlib.sha512(reader.data.tobytes()).hexdigest()
    assert actual_sha512 == expected_sha512
