import os

from OpenGL.GL import (
    GL_COMPILE_STATUS,
    GL_FALSE,
    GL_FRAGMENT_SHADER,
    GL_LINK_STATUS,
    GL_VERTEX_SHADER,
    glAttachShader,
    glCompileShader,
    glCreateProgram,
    glCreateShader,
    glDeleteProgram,
    glDeleteShader,
    glGetProgramInfoLog,
    glGetProgramiv,
    glGetShaderInfoLog,
    glGetShaderiv,
    glGetUniformLocation,
    glLinkProgram,
    glShaderSource,
    glUniform1f,
    glUniform1i,
    glUniform3f,
    glUniformMatrix4fv,
    glUseProgram,
)


class ShaderProgram:
    """
    Represents an OpenGL GLSL shader program, responsible for loading,
    compiling, linking, and managing vertex and fragment shaders.

    This class provides utility methods for binding the shader,
    managing uniforms, and safely handling OpenGL resource cleanup.

    **Example:**

    .. code-block:: python

        from volumetric_viewer.shader_program import ShaderProgram

        shader = ShaderProgram("shaders/vertex.glsl", "shaders/fragment.glsl")
        shader.use()
        shader.set_uniform1f("u_time", 1.5)
        shader.stop()

    :ivar vertex_shader_path: Path to the vertex shader source file.
    :vartype vertex_shader_path: str
    :ivar fragment_shader_path: Path to the fragment shader source file.
    :vartype fragment_shader_path: str
    :ivar program_id: OpenGL handle for the linked shader program.
    :vartype program_id: int | None
    """

    def __init__(self, vertex_shader_path: str, fragment_shader_path: str) -> None:
        """
        Initialize and compile the shader program from the specified vertex and fragment shader files.

        :param vertex_shader_path: Path to the vertex shader file.
        :type vertex_shader_path: str
        :param fragment_shader_path: Path to the fragment shader file.
        :type fragment_shader_path: str
        :raises FileNotFoundError: If a shader source file cannot be found.
        :raises RuntimeError: If shader compilation or program linking fails.
        """
        self.vertex_shader_path = vertex_shader_path
        self.fragment_shader_path = fragment_shader_path
        self.program_id = None

        self._create_program()

    def _read_shader_source(self, path: str) -> str:
        """
        Read the GLSL shader source code from a file.

        :param path: Path to the shader file.
        :type path: str
        :returns: The shader source code as a UTF-8 string.
        :rtype: str
        :raises FileNotFoundError: If the file does not exist.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Shader file not found: {path}")
        with open(path, encoding="utf-8") as file:
            return file.read()

    def _compile_shader(self, source: str, shader_type) -> int:
        """
        Compile a shader from its source code.

        :param source: Shader source code (GLSL).
        :type source: str
        :param shader_type: Shader type constant (``GL_VERTEX_SHADER`` or ``GL_FRAGMENT_SHADER``).
        :type shader_type: int
        :returns: The compiled shader object ID.
        :rtype: int
        :raises RuntimeError: If shader compilation fails, including GLSL error log.
        """
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        compile_status = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not compile_status:
            error_log = glGetShaderInfoLog(shader).decode()
            shader_type_str = {
                GL_VERTEX_SHADER: "VERTEX",
                GL_FRAGMENT_SHADER: "FRAGMENT"
            }.get(shader_type, "UNKNOWN")
            raise RuntimeError(f"{shader_type_str} SHADER COMPILATION ERROR:\n{error_log}")

        return shader

    def _create_program(self) -> None:
        """
        Compile the vertex and fragment shaders, link them into an OpenGL shader program,
        and store the resulting program ID.

        :raises RuntimeError: If shader linking fails.
        """
        vertex_source = self._read_shader_source(self.vertex_shader_path)
        fragment_source = self._read_shader_source(self.fragment_shader_path)

        vertex_shader = self._compile_shader(vertex_source, GL_VERTEX_SHADER)
        fragment_shader = self._compile_shader(fragment_source, GL_FRAGMENT_SHADER)

        program = glCreateProgram()
        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        glLinkProgram(program)

        link_status = glGetProgramiv(program, GL_LINK_STATUS)
        if not link_status:
            error_log = glGetProgramInfoLog(program).decode()
            glDeleteShader(vertex_shader)
            glDeleteShader(fragment_shader)
            glDeleteProgram(program)
            raise RuntimeError(f"SHADER PROGRAM LINK ERROR:\n{error_log}")

        # Clean up shaders after linking
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        self.program_id = program

    def use(self) -> None:
        """
        Activate this shader program for rendering.

        Subsequent OpenGL draw calls will use this program until another is bound
        or :meth:`stop` is called.
        """
        glUseProgram(self.program_id)

    def stop(self) -> None:
        """
        Deactivate the currently active shader program.

        Equivalent to calling ``glUseProgram(0)``.
        """
        glUseProgram(0)

    def get_uniform_location(self, name: str) -> int:
        """
        Retrieve the location of a uniform variable within the shader program.

        :param name: Name of the uniform variable as defined in GLSL.
        :type name: str
        :returns: The uniform location, or ``-1`` if the uniform was not found.
        :rtype: int
        """
        location = glGetUniformLocation(self.program_id, name)
        if location == -1:
            print(f"Warning: Uniform '{name}' not found in shader.")
        return location

    def set_uniform1i(self, name: str, value: int) -> None:
        """
        Set an integer uniform variable in the shader.

        :param name: Name of the uniform variable.
        :type name: str
        :param value: Integer value to assign.
        :type value: int
        """
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform1i(location, value)

    def set_uniform1f(self, name: str, value: float) -> None:
        """
        Set a floating-point uniform variable in the shader.

        :param name: Name of the uniform variable.
        :type name: str
        :param value: Floating-point value to assign.
        :type value: float
        """
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform1f(location, value)

    def set_uniform_vec3(self, name: str, vec3) -> None:
        """
        Set a ``vec3`` (3-component float vector) uniform variable in the shader.

        :param name: Name of the uniform variable.
        :type name: str
        :param vec3: Iterable of 3 float values representing the vector (x, y, z).
        :type vec3: Iterable[float]
        """
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform3f(location, *vec3)

    def set_uniform_mat4(self, name: str, matrix) -> None:
        """
        Set a 4x4 matrix uniform variable (``mat4``) in the shader.

        :param name: Name of the uniform variable.
        :type name: str
        :param matrix: A 4x4 transformation matrix as a NumPy array (``dtype=float32``)
                       or a flat list of 16 floats.
        :type matrix: numpy.ndarray | list[float]
        """
        location = self.get_uniform_location(name)
        if location != -1:
            glUniformMatrix4fv(location, 1, GL_FALSE, matrix)

    def delete(self) -> None:
        """
        Delete this shader program from GPU memory.

        This should be called when the shader program is no longer needed,
        to free GPU resources.
        """
        if self.program_id:
            glDeleteProgram(self.program_id)
            self.program_id = None

    def __repr__(self) -> str:
        """
        Return a string representation of this shader program.

        :returns: Human-readable summary of the shader program.
        :rtype: str
        """
        return (
            f"<ShaderProgram vertex='{self.vertex_shader_path}' "
            f"fragment='{self.fragment_shader_path}' id={self.program_id}>"
        )
