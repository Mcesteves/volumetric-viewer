import os

import numpy as np

from volumetric_viewer.nhdr_reader import NHDRReader
from volumetric_viewer.volume_normalizer import VolumeNormalizer


def test_should_normalize_volume():
    current_dir = os.path.dirname(__file__)
    tooth_file = os.path.join(current_dir, "..", "data", "tooth.nhdr")
    tooth_file = os.path.abspath(tooth_file)

    reader = NHDRReader(tooth_file)
    normalizer = VolumeNormalizer()

    normalized_data, scale_factors = normalizer.normalize(
        (reader.dim_x, reader.dim_y, reader.dim_z),
        (reader.spacing_x, reader.spacing_y, reader.spacing_z),
        reader.data, reader.d_type
    )

    # Check if voxel data is in the range [0, 1]
    assert np.min(normalized_data) >= 0.0, "Normalized data contains values below 0"
    assert np.max(normalized_data) <= 1.0, "Normalized data contains values above 1"

    # Check if scale factors are correct
    physical_size = (
        reader.dim_x * reader.spacing_x,
        reader.dim_y * reader.spacing_y,
        reader.dim_z * reader.spacing_z
    )
    max_size = max(physical_size)
    expected_uniform_scale = 1.0 / max_size
    expected_scale_factors = tuple(s * expected_uniform_scale for s in physical_size)

    assert np.allclose(scale_factors, expected_scale_factors, atol=1e-6), (
        f"Scale factors are incorrect. Expected {expected_scale_factors}, got {scale_factors}"
    )

    # Check if normalized data has the same shape as the original data
    assert normalized_data.shape == reader.data.shape, (
        "Normalized data shape differs from the original data shape"
    )