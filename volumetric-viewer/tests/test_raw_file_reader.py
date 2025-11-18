import hashlib
import os

from volumetric_viewer.data_type_enum import DataType
from volumetric_viewer.raw_parser import RawParser


def test_should_parse_raw_files():
    current_dir = os.path.dirname(__file__)
    tooth_file = os.path.join(current_dir, "..", "data", "tooth_103x94x161_uint8.raw")
    tooth_file = os.path.abspath(tooth_file)
    parser = RawParser(tooth_file)

    assert parser.dim_x == 103
    assert parser.dim_y == 94
    assert parser.dim_z == 161

    assert parser.d_type == DataType.UINT8

    tooth_data = parser.read_data()

    sha512_value = "5ee3d77ae951e129d29062a4fd4d8730fd8670bdaf4d01ddf907848072180cbfea8ab897880147d2a79dc7f1d1806a34b32853074eca88f6758e01382469f9f6"
    sha512 = hashlib.sha512()
    sha512.update(tooth_data.tobytes())
    assert sha512.hexdigest() == sha512_value
