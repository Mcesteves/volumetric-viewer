from pyglm import glm


class ArcballCamera:
    """
    Represents an orbiting camera (arcball-style) that rotates around a target point.
    Useful for inspecting 3D scenes from different angles with mouse input.

    Attributes:
        target (glm.vec3): The point in space the camera orbits around.
        distance (float): Distance from the camera to the target.
        yaw (float): Horizontal rotation angle (in degrees).
        pitch (float): Vertical rotation angle (in degrees).
        sensitivity (float): Mouse sensitivity for rotation.
        zoom_speed (float): Speed at which the camera zooms in/out.
        min_distance (float): Minimum allowed distance to the target (prevents clipping).
        max_distance (float): Maximum allowed distance to the target.
        up (glm.vec3): World up vector, used to maintain the camera's orientation.
        position (glm.vec3): The current world-space position of the camera.
        view_matrix (glm.mat4): Cached view matrix based on position and orientation.
    """

    def __init__(
        self,
        target: glm.vec3,
        distance: float = 3.0,
        yaw: float = -135.0,
        pitch: float = -30.0,
        sensitivity: float = 0.3,
        zoom_speed: float = 1.0,
        min_distance: float = 0.1,
        max_distance: float = 100.0,
    ):
        if target is None:
            target = glm.vec3(0, 0, 0)
        else:   
            self.target = target
        self.distance = distance
        self.yaw = yaw
        self.pitch = pitch
        self.sensitivity = sensitivity
        self.zoom_speed = zoom_speed
        self.min_distance = min_distance
        self.max_distance = max_distance

        self.up = glm.vec3(0, 1, 0)
        self.position = glm.vec3(0)
        self.view_matrix = glm.mat4(1)

        self.update_camera()

    def update_camera(self) -> None:
        """
        Recalculates the camera's position and view matrix based on
        current yaw, pitch, distance, and target.
        """
        rad_yaw = glm.radians(self.yaw)
        rad_pitch = glm.radians(self.pitch)

        # Convert spherical coordinates (yaw, pitch, distance) to Cartesian
        x = self.distance * glm.cos(rad_pitch) * glm.cos(rad_yaw)
        y = self.distance * glm.sin(rad_pitch)
        z = self.distance * glm.cos(rad_pitch) * glm.sin(rad_yaw)

        self.position = glm.vec3(x, y, z) + self.target
        self.view_matrix = glm.lookAt(self.position, self.target, self.up)

    def get_view_matrix(self) -> glm.mat4:
        """
        Returns the view matrix for the current camera configuration.

        Returns:
            glm.mat4: The view matrix.
        """
        return self.view_matrix

    def process_mouse(self, dx: float, dy: float) -> None:
        """
        Updates the yaw and pitch angles based on mouse movement.

        Args:
            dx (float): Horizontal mouse movement in pixels.
            dy (float): Vertical mouse movement in pixels.
        """
        self.yaw += dx * self.sensitivity
        self.pitch += dy * self.sensitivity

        # Clamp pitch to avoid gimbal lock or flipping
        self.pitch = max(-89.0, min(89.0, self.pitch))

        self.update_camera()

    def process_scroll(self, scroll_offset: float) -> None:
        """
        Zooms the camera in or out by adjusting the distance to the target.

        Args:
            scroll_offset (float): Mouse scroll delta.
                Positive values zoom in, negative values zoom out.
        """
        self.distance -= scroll_offset * self.zoom_speed
        self.distance = glm.clamp(self.distance, self.min_distance, self.max_distance)

        self.update_camera()

    def pan(self, dx: float, dy: float) -> None:
        """
        Translates the camera target laterally, allowing side-to-side and up/down movement.

        Args:
            dx (float): Horizontal mouse movement in pixels.
            dy (float): Vertical mouse movement in pixels.
        """
        # Compute local coordinate axes
        direction = glm.normalize(self.target - self.position)
        right = glm.normalize(glm.cross(direction, self.up))
        up = glm.normalize(glm.cross(right, direction))

        # Adjust pan speed based on distance
        factor = self.distance * 0.001

        # Move the target point (and thus the camera orbit center)
        self.target += -right * dx * factor + up * dy * factor

        self.update_camera()
