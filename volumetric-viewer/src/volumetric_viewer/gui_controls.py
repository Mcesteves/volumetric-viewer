from tkinter import Tk, filedialog

from dearpygui import dearpygui as dpg

from volumetric_viewer.event_system import (
    ColorChangedEvent,
    IsovalueChangedEvent,
    NHDRLoadedEvent,
    RawLoadedEvent,
    TransferFunctionExportedEvent,
    TransferFunctionImportedEvent,
    ViewModeChangedEvent,
)

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

def open_file_dialog(sender, app_data, user_data):
    root = Tk()
    root.withdraw()

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

    elif file_path:  # invalid extension
        show_error_popup("Invalid file selected.")


def on_color_changed(sender, app_data, user_data):
    color = tuple(c for c in app_data[:3])
    event_queue = user_data.get("event_queue")
    if event_queue:
        event_queue.push(ColorChangedEvent(color))

def on_isovalue_changed(sender, app_data, user_data):
    event_queue = user_data.get("event_queue")
    if event_queue:
        event_queue.push(IsovalueChangedEvent(app_data))

def import_tf_file (sender, app_data, user_data):
    root = Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select a tranfer function file",
        filetypes=[("Transfer Function Files", "*.tfl")]
    )

    root.destroy()

    if file_path and file_path.endswith(".tfl"):
        if "event_queue" in user_data:
            user_data["event_queue"].push(TransferFunctionImportedEvent(file_path))

def export_tf_file (sender, app_data, user_data):
    root = Tk()
    root.withdraw()

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

def default_view_settings(event_queue):
    with dpg.group(tag="default_view_settings_group", indent=40):
        dpg.add_spacer(height=20)
        dpg.add_text("Color:")
        dpg.add_color_picker(
            default_value=(255, 100, 100, 1.0),
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
            width=400,
            min_value=0,
            max_value=255,
            callback=on_isovalue_changed,
            user_data={"event_queue": event_queue}
        )

def tf_view_settings(event_queue):
    with dpg.group(tag="tf_view_settings_group", indent=40):
        dpg.add_spacer(height=20)
        with dpg.group(tag="tf_buttons_group", horizontal=True):
            dpg.add_button(label="Import Transfer Function", tag="import_tf_btn", callback=import_tf_file, user_data={"event_queue": event_queue})
            dpg.add_button(label="Export Transfer Function", tag="export_tf_btn", callback=export_tf_file, user_data={"event_queue": event_queue})


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

def run_gui(position=(100, 100), event_queue=None):
    dpg.create_context()

    dpg.create_viewport(title='Visualization Settings', width=600, height=700, disable_close=True, resizable=False)
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
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    run_gui()
