from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_ELEMENT_ARRAY_BUFFER,
    GL_FALSE,
    GL_FLOAT,
    GL_STATIC_DRAW,
    GL_TEXTURE0,
    GL_TEXTURE_3D,
    GL_TRIANGLES,
    GL_UNSIGNED_INT,
    GLfloat,
    GLuint,
    glActiveTexture,
    glBindBuffer,
    glBindTexture,
    glBindVertexArray,
    glBufferData,
    glDrawElements,
    glEnableVertexAttribArray,
    glGenBuffers,
    glGenVertexArrays,
    glGetUniformLocation,
    glUniform1i,
    glUseProgram,
    glVertexAttribPointer,
)

from volumetric_viewer.volume import Volume


class Renderer:
    """
    Responsible for rendering a 3D volume using OpenGL.
    Creates and draws a unit cube.
    """

    def __init__(self, shader_program: int) -> None:
        """
        Initializes the renderer with the shader program.

        Args:
            shader_program (int): The compiled OpenGL shader program ID.
        """
        self._volume: Volume | None = None
        self._shader_program = shader_program
        self._vao = self._create_cube_vao()

    def _create_cube_vao(self) -> int:
        """
        Creates the necessary buffers to render a unit cube.

        Returns:
            int: The generated Vertex Array Object (VAO) ID.
        """
        # Cube vertices (positions from 0 to 1 in each axis)
        vertices = [
            0, 0, 0,
            1, 0, 0,
            1, 1, 0,
            0, 1, 0,
            0, 0, 1,
            1, 0, 1,
            1, 1, 1,
            0, 1, 1,
        ]

        # Indices for the cube's triangles (12 triangles, 36 indices)
        indices = [
            0, 1, 2, 2, 3, 0,  # face z-
            4, 5, 6, 6, 7, 4,  # face z+
            0, 4, 7, 7, 3, 0,  # face x-
            1, 5, 6, 6, 2, 1,  # face x+
            3, 2, 6, 6, 7, 3,  # face y+
            0, 1, 5, 5, 4, 0   # face y-
        ]

        # Create VAO, VBO, and EBO
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, len(vertices) * 4, (GLfloat * len(vertices))(*vertices), GL_STATIC_DRAW)

        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * 4, (GLuint * len(indices))(*indices), GL_STATIC_DRAW)

        # Vertex attribute: position (3 floats)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glBindVertexArray(0)
        return vao

    def render(self) -> None:
        """
        Renders the volume using the current shader and 3D texture.
        """
        if self._volume is None:
            return
    
        glUseProgram(self._shader_program)
        glBindVertexArray(self._vao)

        # Bind 3D texture to texture unit 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_3D, self._volume.texture_id)

        # Set shader uniform for volume texture
        location = glGetUniformLocation(self._shader_program, "volumeTex")
        glUniform1i(location, 0)

        # Draw cube with triangles
        glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)

        # Unbind everything
        glBindTexture(GL_TEXTURE_3D, 0)
        glBindVertexArray(0)
        glUseProgram(0)

    def __repr__(self) -> str:
        return f"<Renderer vao={self._vao} shader_program={self._shader_program}>"

    def update_volume(self, new_volume: Volume) -> None:
        """
        Updates the renderer to use a new volume.
        Args:
            new_volume (Volume): The volume containing the new uploaded 3D texture.
        """
        if self._volume is not None:
            self._volume.delete()

        self._volume = new_volume

    @property
    def scale_factors(self):
        return self._volume.scale_factors if self._volume else (1.0, 1.0, 1.0)