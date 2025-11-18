import numpy as np
from OpenGL.GL import (
    GL_CLAMP_TO_EDGE,
    GL_FLOAT,
    GL_LINEAR,
    GL_RED,
    GL_TEXTURE0,
    GL_TEXTURE_3D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_R,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    glActiveTexture,
    glBindTexture,
    glDeleteTextures,
    glGenTextures,
    glTexImage3D,
    glTexParameteri,
)

from volumetric_viewer.volume_normalizer import VolumeNormalizer


class Volume:
    """
    Represents a normalized 3D volumetric dataset and manages it as an OpenGL 3D texture.
    """

    def __init__(
        self,
        raw_data: np.ndarray,
        sizes: tuple[int, int, int],
        spacings: tuple[float, float, float]
    ) -> None:
        """
        Initializes the Volume by normalizing the raw volume data.

        Args:
            raw_data (np.ndarray): Raw volumetric data to be normalized and uploaded.
            sizes (Tuple[int, int, int]): Volume dimensions (x, y, z).
            spacings (Tuple[float, float, float]): Physical voxel spacings.
        """
        self._sizes = sizes
        self.texture_id: int | None = None

        normalizer = VolumeNormalizer()
    
        self.normalized_data, self._scale_factors = normalizer.normalize(sizes, spacings, raw_data)

    def upload_to_gpu(self) -> None:
        """
        Uploads the normalized volume data to the GPU as a 3D texture.
        Deletes any existing texture before uploading.
        """
        if self.texture_id is not None:
            glDeleteTextures([self.texture_id])

        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_3D, self.texture_id)

        data_3d = self.normalized_data.reshape(self._sizes)

        glTexImage3D(
            GL_TEXTURE_3D,
            0,              
            GL_RED,         
            self._sizes[0], self._sizes[1], self._sizes[2],
            0,              
            GL_RED,         
            GL_FLOAT,       
            data_3d
        )

        # Texture parameters
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        glBindTexture(GL_TEXTURE_3D, 0)

    def bind(self, texture_unit: int = 0) -> None:
        """
        Binds the texture to the specified texture unit.

        Args:
            texture_unit (int): Index of the texture unit. Default is 0.
        """
        glActiveTexture(GL_TEXTURE0 + texture_unit)
        glBindTexture(GL_TEXTURE_3D, self.texture_id)

    def unbind(self) -> None:
        """
        Unbinds the 3D texture from the active texture unit.
        """
        glBindTexture(GL_TEXTURE_3D, 0)

    def delete(self) -> None:
        """
        Deletes the texture from GPU memory, if it exists.
        """
        if self.texture_id is not None:
            glDeleteTextures([self.texture_id])
            self.texture_id = None

    @property
    def sizes(self) -> tuple[int, int, int]:
        """
        Returns the volume dimensions.

        Returns:
            Tuple[int, int, int]: (x, y, z) volume size.
        """
        return self._sizes
    
    @property
    def scale_factors(self) -> tuple[float, float, float]:
        return self._scale_factors


    def __repr__(self) -> str:
        return (
            f"<Volume size={self._sizes} texture_id={self.texture_id}>"
        )
