from tkinter import Tk as _Tk
from tkinter.ttk import (
    Button as _Button,
    Label as _Label,
    LabelFrame as _LabelFrame,
    Frame as _Frame,
    Combobox as _Combobox
)
from tkinter.filedialog import askopenfilename as _askopen, asksaveasfilename as _asksave
from tkinter.messagebox import askyesno as _askyesno, showerror as _showerror
from pathlib import Path as _Path
from sys import platform as _platform
from subprocess import Popen as _Popen
from .image import BitmapImage as _BitmapImage, DOWNLOADS_PATH as _DOWNLOADS_PATH


class App(_Tk):

    _NO_SOURCE_SELECTION_TEXT = "No selection."

    _ICNS = "Apple Icon"
    _ICO_APP = "Program Icon"
    _ICO_FAVICON = "Website Favicon"

    _ICON_PRESET_CHOICES = {
        _ICNS: [16, 32, 48, 128, 256, 512, 1024],
        _ICO_APP: [16, 24, 32, 48, 64, 128, 256],
        _ICO_FAVICON: [16, 32, 48, 64]
    }

    def __init__(self):
        _Tk.__init__(self)
        self._loaded_image: _BitmapImage | None = None
        self.title("Image Tool")
        self.geometry("400x500")
        self.resizable(False, False)
        group_frame = _Frame(self)
        group_frame.pack(fill="both", expand=True)
        select_group = _LabelFrame(group_frame, text="File Selection")
        select_group.pack(fill="both", expand=True, padx=8, pady=8)
        self._file_label = _Label(select_group, text=self._NO_SOURCE_SELECTION_TEXT)
        self._file_label.pack(pady=16)
        _Button(select_group, text="Select A File", command=self._select_input_file).pack(pady=8)
        ico_group = _LabelFrame(group_frame, text="Convert To Icon")
        ico_group.pack(fill="both", expand=True, padx=8, pady=8)
        self._ico_status = _Label(ico_group)
        self._ico_status.pack(pady=16)
        self._ico_size_preset = _Combobox(ico_group, width=30)
        self._ico_size_preset.pack(pady=8)
        self._ico_convert_button = _Button(ico_group, command=self._icon_convert)
        self._ico_convert_button.pack(pady=8)
        self._update_icon_convert_state()
        convert_group = _LabelFrame(group_frame, text="Convert To Other Bitmap")
        convert_group.pack(fill="both", expand=True, padx=8, pady=8)
        self._standard_status = _Label(convert_group, text="You can select the output file type when saving.")
        self._standard_status.pack(pady=16)
        self._convert_button = _Button(convert_group, command=self._common_convert)
        self._convert_button.pack(pady=8)
        self._update_standard_convert_state()

    @staticmethod
    def _conversion_finished(destination_filepath: str) -> None:
        if not _askyesno("Convert", "Conversion complete! Would you like to open the folder of your converted image?"):
            return
        output_directory = str(_Path(destination_filepath).parent)
        if _platform == "win32":
            from os import startfile as _startfile
            _startfile(output_directory)
        elif _platform.startswith("linux"):
            _Popen(["xdg-open", output_directory])
        elif _platform == "darwin":
            _Popen(["open", output_directory])
        else:
            _showerror("Cannot Open Folder", "Cannot open folder with converted image. Platform could not be determined.")

    def _is_source_image_loaded(self) -> bool:
        return isinstance(self._loaded_image, _BitmapImage)

    def _get_icon_sizes(self) -> tuple[str, list[int]]:
        preset = self._ico_size_preset.get()
        return preset, self._ICON_PRESET_CHOICES[preset]

    def _update_icon_convert_state(self) -> None:

        def fully_invalid(status_message: str) -> None:
            self._ico_status.config(text=status_message)
            self._ico_size_preset.config(values=list(self._ICON_PRESET_CHOICES.keys()), state="disabled")
            self._ico_convert_button.config(text="Unavailable", state="disabled")

        self._ico_size_preset.set(self._ICO_APP)
        if not self._is_source_image_loaded():
            fully_invalid(self._NO_SOURCE_SELECTION_TEXT)
            return
        if not self._loaded_image.is_valid_icon():
            fully_invalid("Source file must have equal width and height for icons.")
            return
        filtered_presets = {key: value for key, value in self._ICON_PRESET_CHOICES.items() if self._loaded_image.is_valid_icon(max(value))}
        if not len(filtered_presets):
            fully_invalid("Source file is too small for any icon format.")
            return
        self._ico_status.config(text="Select Size Preset...")
        self._ico_size_preset.config(state="readonly", values=list(filtered_presets.keys()))
        self._ico_convert_button.config(text="Convert", state="normal")

    def _update_standard_convert_state(self) -> None:
        if self._is_source_image_loaded():
            self._standard_status.config(text="Output file type is specified during saving.")
            self._convert_button.config(text="Convert", state="normal")
            return
        self._standard_status.config(text=self._NO_SOURCE_SELECTION_TEXT)
        self._convert_button.config(text="Unavailable", state="disabled")

    def _select_input_file(self) -> None:
        filename = _askopen(parent=self, initialdir=_Path.joinpath(_Path.home(), "Downloads"))
        if not filename:
            return
        try:
            self._loaded_image = _BitmapImage(filename)
        except ValueError:
            self._loaded_image = None
            self._file_label.config(text="Invalid file selected." if filename else "No file selected.")
        except FileExistsError:
            self._loaded_image = None
            self._file_label.config(text="Invalid file selected. Nothing can be done with icon files.")
        else:
            self._file_label.config(text=filename)
        self._update_icon_convert_state()
        self._update_standard_convert_state()

    def _common_convert(self) -> None:
        image_types_copy = self._loaded_image.IMAGE_TYPES.copy()
        valid_types = [
            (label, extensions)
            for label, extensions in image_types_copy.items()
            if self._loaded_image.source_extension not in extensions and label not in (self._loaded_image.ICO, self._loaded_image.ICNS)
        ]
        destination = _asksave(
            parent=self,
            initialdir=_DOWNLOADS_PATH,
            defaultextension=valid_types[0][0],
            filetypes=valid_types,
            confirmoverwrite=True
        )
        if not destination:
            return
        self._loaded_image.bitmap_convert(destination)
        self._conversion_finished(destination)

    def _icon_convert(self) -> None:
        selection, resolutions = self._get_icon_sizes()
        icns = selection == self._ICNS
        filetype = self._loaded_image.ICNS if icns else self._loaded_image.ICO
        extension = self._loaded_image.IMAGE_TYPES[filetype][0]
        destination = _asksave(
            parent=self,
            initialdir=_DOWNLOADS_PATH,
            defaultextension=extension,
            filetypes=[(filetype, extension)],
            confirmoverwrite=True
        )
        if not destination:
            return
        self._loaded_image.bitmap_to_icon(destination, *resolutions)
        self._conversion_finished(destination)
