import threading

import glfw
import numpy as np
from OpenGL.GL import (
    GL_BLEND,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_SRC_ALPHA,
    glBlendFunc,
    glClearColor,
    glEnable,
    glViewport,
)
from pyglm import glm

from volumetric_viewer.arcball_camera import ArcballCamera
from volumetric_viewer.event_system import (
    ColorChangedEvent,
    EventQueue,
    MaxIsovalueChangedEvent,
    MinIsovalueChangedEvent,
    NHDRLoadedEvent,
    RawLoadedEvent,
    TransferFunctionExportedEvent,
    TransferFunctionImportedEvent,
    TransferFunctionUpdateEvent,
    ViewModeChangedEvent,
)
from volumetric_viewer.gui_controls import run_gui
from volumetric_viewer.nhdr_reader import NHDRReader
from volumetric_viewer.raw_reader import RawReader
from volumetric_viewer.renderer import Renderer
from volumetric_viewer.shader_program import ShaderProgram
from volumetric_viewer.transfer_function_manager import TransferFunctionManager
from volumetric_viewer.volume import Volume

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
ASPECT_RATIO = WINDOW_WIDTH / WINDOW_HEIGHT

def main():
    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Volume Renderer", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create GLFW window")

    glfw.make_context_current(window)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Calculates positions to make pygui window appear next to the render window
    x_pos, y_pos = glfw.get_window_pos(window)
    width, height = glfw.get_window_size(window)

    gui_x = x_pos + width
    gui_y = y_pos
    event_queue = EventQueue()
    gui_event_queue = EventQueue()
    threading.Thread(target=(run_gui), args=((gui_x, gui_y), event_queue, gui_event_queue), daemon=True).start()

    camera = ArcballCamera(
        target=glm.vec3(0.5, 0.5, 0.5),
        distance=2.5
    )

    last_x, last_y = 0, 0
    left_pressed = False
    middle_pressed = False

    def mouse_button_callback(window, button, action, mods):
        nonlocal left_pressed, middle_pressed
        if button == glfw.MOUSE_BUTTON_LEFT:
            left_pressed = (action == glfw.PRESS)
        elif button == glfw.MOUSE_BUTTON_MIDDLE:
            middle_pressed = (action == glfw.PRESS)

    def mouse_move_callback(window, xpos, ypos):
        nonlocal last_x, last_y
        dx = xpos - last_x
        dy = ypos - last_y
        last_x = xpos
        last_y = ypos

        if left_pressed:
            camera.process_mouse(dx, dy)
        elif middle_pressed:
            camera.pan(dx, dy)

    def scroll_callback(window, xoffset, yoffset):
        camera.process_scroll(yoffset)
    
    def framebuffer_size_callback(window, width, height):
        if height != 0:
            window_ratio = width / height
        else: 
            window_ratio = ASPECT_RATIO

        if window_ratio > ASPECT_RATIO:
            viewport_height = height
            viewport_width = int(height * ASPECT_RATIO)
            viewport_x = (width - viewport_width) // 2
            viewport_y = 0
        else:
            viewport_width = width
            viewport_height = int(width / ASPECT_RATIO)
            viewport_x = 0
            viewport_y = (height - viewport_height) // 2

        glViewport(viewport_x, viewport_y, viewport_width, viewport_height)

    glfw.set_cursor_pos_callback(window, mouse_move_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    transfer_function_manager = TransferFunctionManager()
    shader = ShaderProgram("src/shaders/vertex.glsl", "src/shaders/fragment.glsl")
    renderer = Renderer(shader.program_id)
    volume = None
    view_mode = 0
    isovalue_min = 0
    isovalue_max = 255
    color = (1, 100/255.0, 100/255.0)

    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    current_volume_loaded = None

    while not glfw.window_should_close(window):
        glfw.poll_events()

        for event in event_queue.pop_all():
            if isinstance(event, NHDRLoadedEvent):
                if current_volume_loaded != event.filepath:
                    current_volume_loaded = event.filepath       
                    reader = NHDRReader(current_volume_loaded)
                    volume = Volume(
                        reader.data,
                        (reader.dim_x, reader.dim_y, reader.dim_z),
                        (reader.spacing_x, reader.spacing_y, reader.spacing_z)
                    )
                    renderer.update_volume(volume)
                    volume.upload_to_gpu()
            elif isinstance(event, RawLoadedEvent):
                if current_volume_loaded != event.filepath:
                    current_volume_loaded = event.filepath       
                    reader = RawReader(current_volume_loaded)
                    volume = Volume(
                        reader.data,
                        (reader.dim_x, reader.dim_y, reader.dim_z),
                        (reader.spacing_x, reader.spacing_y, reader.spacing_z)
                    )
                    renderer.update_volume(volume)
                    volume.upload_to_gpu()
                print(event)
            elif isinstance(event, ColorChangedEvent):
                color = event.color
            elif isinstance(event, MinIsovalueChangedEvent):
                isovalue_min = event.isovalue
            elif isinstance(event, MaxIsovalueChangedEvent):
                isovalue_max = event.isovalue
            elif isinstance(event, ViewModeChangedEvent):
                view_mode = event.view_mode
            elif isinstance(event, TransferFunctionImportedEvent):
                data = transfer_function_manager.read_file(event.filepath)
                transfer_function_manager.update_transfer_function(data)
                gui_event_queue.push(TransferFunctionUpdateEvent(data)) 
            elif isinstance(event, TransferFunctionExportedEvent):
                #transfer_function_manager.write_file(event.filepath)
                print(event)
                pass 

        from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glClear
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shader.use()

        model = glm.mat4(1.0)
        projection = glm.perspective(glm.radians(45.0), WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100.0)
        view = camera.get_view_matrix()

        shader.set_uniform_mat4("model", np.array(model.to_list(), dtype=np.float32))
        shader.set_uniform_mat4("projection", np.array(projection.to_list(), dtype=np.float32))
        shader.set_uniform_mat4("view", np.array(view.to_list(), dtype=np.float32))

        model_inv = glm.inverse(model)
        cam_pos_world = glm.vec4(camera.position.x, camera.position.y, camera.position.z, 1.0)
        cam_pos_model = model_inv * cam_pos_world
        shader.set_uniform_vec3("cameraPos", [cam_pos_model.x, cam_pos_model.y, cam_pos_model.z])

        shader.set_uniform_vec3("volumeScale", [
            renderer.scale_factors[0],
            renderer.scale_factors[1],
            renderer.scale_factors[2]
        ])

        shader.set_uniform1i("viewMode", view_mode)

        if view_mode == 0:
            shader.set_uniform_vec3("volumeColor", [color[0], color[1], color[2]])
            min_normalized_isovalue = isovalue_min/255.0
            max_normalized_isovalue = isovalue_max/255.0
            shader.set_uniform1f("minIsovalueLimit", min_normalized_isovalue)
            shader.set_uniform1f("maxIsovalueLimit", max_normalized_isovalue)

        else:
            transfer_function_manager.bind_transfer_function(1)
            shader.set_uniform1i("transferFuncTex", 1)

        renderer.render()
        glfw.swap_buffers(window)

    if volume:
        volume.delete()
    shader.delete()
    glfw.terminate()

if __name__ == "__main__":
    main()
