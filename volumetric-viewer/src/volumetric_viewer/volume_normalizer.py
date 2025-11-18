
import numpy as np


class VolumeNormalizer:
    """
    Provides normalization of volumetric data intensity and spatial coordinates.
    """

    def normalize(
        self, 
        sizes: tuple[int, int, int], 
        spacings: tuple[float, float, float], 
        data: np.ndarray
    ) -> tuple[np.ndarray, tuple[float, float, float]]:
        """
        Normalizes intensity values and computes spatial scaling.

        Returns:
            normalized_data (np.ndarray): Densities between 0 and 1.
            scale_factors (tuple[float, float, float]): Normalization factor along each axis.
        """
        physical_size = (
            sizes[0] * spacings[0],
            sizes[1] * spacings[1],
            sizes[2] * spacings[2]
        )

        max_size = max(physical_size)
        uniform_scale = 1.0 / max_size

        scale_factors = tuple(s * uniform_scale for s in physical_size)

        normalized_data = (data - np.min(data)) / (np.max(data) - np.min(data))

        return normalized_data, scale_factors