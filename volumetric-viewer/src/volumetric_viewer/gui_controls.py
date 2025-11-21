from tkinter import Tk, filedialog
from dearpygui import dearpygui as dpg
from scipy.interpolate import interp1d
import numpy as np

from volumetric_viewer.event_system import (
    ColorChangedEvent,
    MaxIsovalueChangedEvent,
    MinIsovalueChangedEvent,
    NHDRLoadedEvent,
    RawLoadedEvent,
    TransferFunctionExportedEvent,
    TransferFunctionImportedEvent,
    TransferFunctionUpdateEvent,
    ViewModeChangedEvent,
)

points = []
first_gradient = [
                    [0, 1.0, 0.0, 0.0],
                    [20, 0.0, 1.0, 0.0],
                    [255, 0.0, 0.0, 1.0]
]
second_gradient = [
                    [0, 1.0, 1.0, 0.0],
                    [100, 0.0, 1.0, 1.0],
                    [255, 0.0, 0.0, 1.0]
]
        
third_gradient = [
                    [0, 1.0, 0.0, 1.0],
                    [100, 0.0, 1.0, 1.0],
                    [255, 1.0, 0.0, 1.0]
]

def interp_knots(knots, x):
        if not knots:
            return (0.0, 0.0, 0.0)

        first = knots[0]
        last = knots[-1]

        x_first = first[0] 
        x_last = last[0]    

        if x <= x_first:
            return first[1:]
        if x >= x_last:
            return last[1:]

        for i in range(len(knots) - 1):
            x0 = knots[i][0]  
            x1 = knots[i+1][0]  
            if x0 <= x <= x1:
                t = (x - x0) / (x1 - x0)
                r0, g0, b0 = knots[i][1:]
                r1, g1, b1 = knots[i+1][1:]
                return (
                    r0 * (1 - t) + r1 * t,
                    g0 * (1 - t) + g1 * t,
                    b0 * (1 - t) + b1 * t
                )

        return (0.0, 0.0, 0.0)

def generate_gradient(colors_list):
    gradient_data = []
    for i in range(255):
        r, g, b = interp_knots(colors_list, i)
        gradient_data.append([r, g, b, 1.0])
    return gradient_data

def display_gradient(colors):
    gradient_data = generate_gradient(colors)

    width = 500
    height = 20

    with dpg.drawlist(width=width, height=height) as drawlist:
        for i, (r, g, b, a) in enumerate(gradient_data):
            dpg.draw_rectangle(
                (i, 0),
                (i + 1, height),
                color=(int(r * 255), int(g * 255), int(b * 255), 255),
                fill=True,
                parent=drawlist
            )

# Function to show an error popup
def show_error_popup(message):
    with dpg.window(
        label="Error",
        modal=True,
        no_close=False,
        width=300,
        height=150
    ):
        dpg.add_text(message)
        dpg.add_spacer(height=10)
        dpg.add_button(label="OK", width=75, callback=lambda: dpg.delete_item(dpg.last_container()))

# Function to open a file dialog for file selection
def open_file_dialog(sender, app_data, user_data):
    root = Tk()
    root.withdraw()

    # Open file dialog to select NHDR or Raw file
    file_path = filedialog.askopenfilename(
        title="Select an NHDR or a Raw file",
        filetypes=[(["NHDR Files", "Raw Files"], ["*.nhdr", ".raw"])]
    )

    root.destroy()

    if file_path and file_path.endswith(".nhdr"):
        dpg.set_value("loaded_file_path", file_path)
        if "event_queue" in user_data:
            user_data["event_queue"].push(NHDRLoadedEvent(file_path))
    elif file_path and file_path.endswith(".raw"):
        dpg.set_value("loaded_file_path", file_path)
        if "event_queue" in user_data:
            user_data["event_queue"].push(RawLoadedEvent(file_path))
    elif file_path:
        show_error_popup("Invalid file selected.")

# Event handler for color change
def on_color_changed(sender, app_data, user_data):
    color = tuple(c for c in app_data[:3])
    event_queue = user_data.get("event_queue")
    if event_queue:
        event_queue.push(ColorChangedEvent(color))

# Event handler for the minimum isovalue slider change
def on_min_isovalue_changed(sender, app_data, user_data):
    min_val = app_data
    max_val = dpg.get_value("max_isovalue_slider")

    if min_val >= max_val:
        min_val = max_val
        dpg.set_value("min_isovalue_slider", min_val)

    event_queue = user_data.get("event_queue")
    if event_queue:
        event_queue.push(MinIsovalueChangedEvent(min_val))

# Event handler for the maximum isovalue slider change
def on_max_isovalue_changed(sender, app_data, user_data):
    max_val = app_data
    min_val = dpg.get_value("min_isovalue_slider")

    if max_val <= min_val:
        max_val = min_val
        dpg.set_value("max_isovalue_slider", max_val)

    event_queue = user_data.get("event_queue")
    if event_queue:
        event_queue.push(MaxIsovalueChangedEvent(max_val))

# Function to import a transfer function (TF) file
def import_tf_file(sender, app_data, user_data):
    root = Tk()
    root.withdraw()

    # Open file dialog to select TF file
    file_path = filedialog.askopenfilename(
        title="Select a transfer function file",
        filetypes=[("Transfer Function Files", "*.tfl")]
    )

    root.destroy()

    colors = get_gradient_colors(dpg.get_value("gradient_radio"))

    if file_path and file_path.endswith(".tfl"):
        if "event_queue" in user_data:
            user_data["event_queue"].push(TransferFunctionImportedEvent(file_path, colors))

# Function to export a transfer function (TF) file
def export_tf_file(sender, app_data, user_data):
    root = Tk()
    root.withdraw()

    # Save file dialog to export TF file
    file_path = filedialog.asksaveasfilename(
        title="Export Transfer Function As...",
        defaultextension=".tfl",
        filetypes=[("Transfer Function Files", "*.tfl")],
        initialfile="transfer_function.tfl"
    )

    root.destroy()

    if file_path:
        print(f"Transfer function exported: {file_path}")
        user_data["event_queue"].push(TransferFunctionExportedEvent(file_path))
    else:
        print("Cancelled.")

# Function to set up the default view settings
def default_view_settings(event_queue):
    with dpg.group(tag="default_view_settings_group", indent=40):
        dpg.add_spacer(height=20)
        dpg.add_text("Color:")
        dpg.add_color_picker(
            default_value=(255, 100, 100),
            no_alpha=True,
            no_side_preview=True,
            display_rgb=True,
            picker_mode=dpg.mvColorPicker_wheel,
            width=200,
            height=200,
            callback=on_color_changed,
            user_data={"event_queue": event_queue}
        )

        dpg.add_spacer(height=10)
        dpg.add_text("Isovalue Inferior Limit:")
        dpg.add_slider_int(
            tag="min_isovalue_slider",
            width=400,
            min_value=0,
            max_value=255,
            callback=on_min_isovalue_changed,
            user_data={"event_queue": event_queue}
        )
        dpg.add_spacer(height=10)
        dpg.add_text("Isovalue Superior Limit:")
        dpg.add_slider_int(
            tag="max_isovalue_slider",
            width=400,
            default_value=255,
            min_value=0,
            max_value=255,
            callback=on_max_isovalue_changed,
            user_data={"event_queue": event_queue}
        )

# Function to update the transfer function plot with points and interpolation
def update_transfer_plot(from_outside = False, event_queue=None):
    if not points:
        dpg.set_value("scatter_series", [[], []])
        dpg.set_value("line_series", [[], []])
        return 

    sorted_pts = sorted(points, key=lambda p: p[0])
    xs, ys = zip(*sorted_pts)

    dpg.set_value("scatter_series", [list(xs), list(ys)])

    f_interp = interp1d(xs, ys, kind='linear', bounds_error=False, fill_value=(ys[0], ys[-1]))

    x_dense = np.linspace(0, 255, 512)
    y_dense = f_interp(x_dense)

    dpg.set_value("line_series", [list(x_dense), list(y_dense)])


# Function to convert mouse position to plot coordinates, excluding the axes area
def mouse_pos_to_plot_coords():
    pos = dpg.get_plot_mouse_pos()
    mouse_pos = dpg.get_mouse_pos()
    
    if pos is None:
        return None, None
    
    plot_min = dpg.get_item_rect_min("tf_plot")
    plot_max = dpg.get_item_rect_max("tf_plot") 
    
    if plot_min is None or plot_max is None:
        return None, None
    
    x_min, y_min = plot_min
    x_max, y_max = plot_max

    axis_padding_left = 55 
    axis_padding_bottom = 55
    
    x_min += axis_padding_left
    y_max -= axis_padding_bottom

    if not (x_min <= mouse_pos[0] <= x_max and y_min <= mouse_pos[1] <= y_max):
        return None, None

    return pos 


# Function for left-click interaction (add points)
def on_left_click(x, y, event_queue):
    print("Left button")
    if not (0 <= x <= 255 and 0 <= y <= 1.0):
        return
    tolerance_y = 0.02
    tolerance_x = 0.5

    for _, (px, py) in enumerate(points):
        if abs(px - x) < tolerance_x and abs(py - y) < tolerance_y:
            return 
    print("Adding point")
    points.append((x, y))
    dpg.set_value("selected_point", len(points) - 1) 
    update_transfer_plot()
    data = {}
    data["alpha_knots"] = points
    data["color_knots"] = get_gradient_colors(dpg.get_value("gradient_radio"))
    event_queue.push(TransferFunctionUpdateEvent(data))

# Function for right-click interaction (remove points)
def on_right_click(x, y, event_queue):
    print("Right button")
    tolerance_y = 0.02
    tolerance_x = 0.5

    for i, (px, py) in enumerate(points):
        if abs(px - x) < tolerance_x and abs(py - y) < tolerance_y:
            points.pop(i) 
            dpg.set_value("selected_point", -1)
            update_transfer_plot() 
            data = {}
            data["alpha_knots"] = points
            data["color_knots"] = get_gradient_colors(dpg.get_value("gradient_radio"))
            event_queue.push(TransferFunctionUpdateEvent(data))
            #print(f"Point removed: {i} ({px}, {py})")
            return
    #print("No point found to remove.")

# Mouse click callback to handle different mouse buttons
def mouse_click_callback(sender, app_data, user_data):
    if dpg.get_value("mode_radio") == "Default View":
        return
    x, y = mouse_pos_to_plot_coords() 
    if x is None or y is None:
        return  

    event_queue = user_data["event_queue"]
    button = app_data
    if button == dpg.mvMouseButton_Left:
        on_left_click(x, y, event_queue)
    elif button == dpg.mvMouseButton_Right:
        on_right_click(x, y, event_queue)

# Mouse release callback to deselect the point
def mouse_release_callback(sender, app_data):
    dpg.set_value("selected_point", -1)

# Function to clear all points on the transfer function plot
def clear_points(sender, app_data, user_data):
    global points
    points.clear()
    dpg.set_value("selected_point", -1)
    update_transfer_plot()
    data = {}
    data["alpha_knots"] = points
    data["color_knots"] = get_gradient_colors(dpg.get_value("gradient_radio"))
    user_data["event_queue"].push(TransferFunctionUpdateEvent(data)) 
    print("All points cleared.")


# Function to create the transfer function editor (plot and controls)
def transfer_function_editor(event_queue):
    with dpg.group(tag="transfer_function_editor_group"):
        with dpg.plot(tag="tf_plot", height=300, width=500, no_menus=True, no_box_select=True):
            dpg.add_plot_axis(dpg.mvXAxis, tag="x_axis", label="Array Value", lock_min=True, lock_max=True)
            dpg.set_axis_limits("x_axis", -10, 265)
            with dpg.plot_axis(dpg.mvYAxis, tag="y_axis", label="Opacity", lock_min=True, lock_max=True):
                dpg.set_axis_limits("y_axis", -0.1, 1.1)
                dpg.add_line_series([], [], tag="line_series", label="Interpolation")
                dpg.add_scatter_series([], [], tag="scatter_series", label="Points")
            with dpg.handler_registry():
                dpg.add_mouse_click_handler(callback=mouse_click_callback,user_data={"event_queue": event_queue})
                dpg.add_mouse_release_handler(callback=mouse_release_callback)
    with dpg.group(tag="editor_btns", horizontal=True):
        dpg.add_button(label="Clear Points", tag="clear_points_btn", callback=clear_points,user_data={"event_queue": event_queue})
        dpg.add_button(label="Import Transfer Function", tag="import_tf_btn", callback=import_tf_file, user_data={"event_queue": event_queue})
        dpg.add_button(label="Export Transfer Function", tag="export_tf_btn", callback=export_tf_file, user_data={"event_queue": event_queue}) 

    update_transfer_plot()

def on_gradient_changed(sender, app_data, user_data):
    data = {}
    global first_gradient, second_gradient, third_gradient
    data["alpha_knots"] = points
    data["color_knots"] = get_gradient_colors(app_data)

    event_queue = user_data.get("event_queue")
    if event_queue:
        event_queue.push(TransferFunctionUpdateEvent(data))

def get_gradient_colors(select_gradient):
    global first_gradient, second_gradient, third_gradient
    if select_gradient == "Gradient 1":
        return first_gradient
    elif select_gradient == "Gradient 2":
        return second_gradient
    elif select_gradient == "Gradient 3":
        return third_gradient

def transfer_function_gradient_selector(event_queue):
    global first_gradient, second_gradient, third_gradient
    dpg.add_spacer(height=10)
    dpg.add_text("Choose the color gradient:")
    with dpg.group():
        dpg.add_radio_button(
                tag="gradient_radio",
                items=["Gradient 1", "Gradient 2", "Gradient 3"],
                default_value="Gradient 1",
                horizontal=True,
                callback=on_gradient_changed,
                user_data={"event_queue": event_queue}
            )
        with dpg.group(horizontal=True):
            with dpg.child_window(width=280, height=35, no_scroll_with_mouse=True, no_scrollbar=True):
                display_gradient(first_gradient)
            dpg.add_text(default_value="Gradient 1")
        with dpg.group(horizontal=True):
            with dpg.child_window(width=280, height=35, no_scroll_with_mouse=True, no_scrollbar=True):
                display_gradient(second_gradient)
            dpg.add_text(default_value="Gradient 2")
        with dpg.group(horizontal=True):
            with dpg.child_window(width=280, height=35, no_scroll_with_mouse=True, no_scrollbar=True):
                display_gradient(third_gradient)
            dpg.add_text(default_value="Gradient 3")   

# Function to set up transfer function view settings (import/export)
def tf_view_settings(event_queue):
    with dpg.group(tag="tf_view_settings_group", indent=40):
        transfer_function_editor(event_queue)
        transfer_function_gradient_selector(event_queue)
        
# Function to toggle between default view and transfer function view
def toggle_view_mode(sender, app_data, user_data):
    view_mode = 0
    if app_data == "Default View":
        dpg.configure_item("default_view_group", show=True)
        dpg.configure_item("tf_view_group", show=False)
    elif app_data == "Transfer Function View":
        dpg.configure_item("default_view_group", show=False)
        dpg.configure_item("tf_view_group", show=True)
        view_mode = 1

    event_queue = user_data.get("event_queue")
    if event_queue:
        event_queue.push(ViewModeChangedEvent(view_mode))

def on_transfer_function_updated(sender, app_data):
    event_data = app_data

    alpha_knots = event_data.get("alpha_knots", [])

    global points
    points = [(x, y) for x, y in alpha_knots]

    update_transfer_plot()

# Main function to set up and run the GUI
def run_gui(position=(100, 100), event_queue=None, gui_event_queue=None):
    dpg.create_context()
    with dpg.value_registry():
         dpg.add_int_value(tag="selected_point", default_value=-1)

    dpg.create_viewport(title='Visualization Settings', width=600, height=750, disable_close=True, resizable=False, always_on_top=True)
    dpg.set_viewport_pos(position)

    viewport_width = dpg.get_viewport_client_width()
    viewport_height = dpg.get_viewport_client_height()

    with dpg.theme() as upload_btn_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 150, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 200, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 100, 200, 255))

    with dpg.window(label="", pos=(0, 0),
                    width=viewport_width, height=viewport_height,
                    no_title_bar=True, no_move=True, no_resize=True, no_collapse=True):
        
        dpg.add_separator(label="Volume Uploading")
        dpg.add_text("Volume Data File:")
        with dpg.group(tag="upload_group", horizontal=True):
            dpg.add_input_text(tag="loaded_file_path",
                               default_value="",
                               width=400,
                               readonly=True)

            upload_btn = dpg.add_button(label="Select File...", width=100, callback=open_file_dialog,
                                        user_data={"event_queue": event_queue})
            dpg.bind_item_theme(upload_btn, upload_btn_theme)

        dpg.add_spacer(height=20)
        dpg.add_separator(label="View Options")

        with dpg.group(tag="view_mode_group", indent=20):
            dpg.add_text("Select View Mode:")
            dpg.add_radio_button(
                tag="mode_radio",
                items=["Default View", "Transfer Function View"],
                default_value=0,
                callback=toggle_view_mode, 
                user_data={"event_queue": event_queue},
                horizontal=True
            )

        with dpg.group(tag="default_view_group"):
            default_view_settings(event_queue)

        with dpg.group(tag="tf_view_group"):
            tf_view_settings(event_queue)

    dpg.configure_item("default_view_group", show=True)
    dpg.configure_item("tf_view_group", show=False)

    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        for event in gui_event_queue.pop_all():
            if isinstance(event, TransferFunctionUpdateEvent):
                on_transfer_function_updated(None, event.data)
                
                pass
        dpg.render_dearpygui_frame()
    dpg.destroy_context()
    

if __name__ == "__main__":
    run_gui()
