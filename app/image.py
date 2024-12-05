from PIL import Image as _Image
from os import access as _access, W_OK as _W_OK, R_OK as _R_OK
from os.path import isfile as _isfile, dirname as _dirname, exists as _exists
from io import BytesIO as _BytesIO
from pathlib import Path as _Path


DOWNLOADS_PATH = _Path.joinpath(_Path.home(), "Downloads")

class BitmapImage:

    PNG = "PNG"
    ICO = "ICO"
    WEBP = "WEBP"
    JPEG = "JPEG"

    IMAGE_TYPES = {
        PNG: ".png",
        ICO: ".ico",
        WEBP: ".webp",
        JPEG: ".jpg"
    }
    """
    Dictionary of file types with their corresponding extensions.
    Keys are the file type while values are the extensions.
    """

    def __init__(self, path: str):
        """
        Object to resize, and convert to multiple bitmap types.

        :param path: Path to bitmap file.
        :raise IOError: If ``path`` is not a file or inaccessible.
        :raise ValueError: If ``path`` is pointing to an unrecognized file type.
        :raise FileExistsError: If ``path`` is pointing to an ICO file, as nothing can be done with it.
        """
        if not _isfile(path) or not _access(path, _R_OK):
            raise IOError(f"Provided `path` is invalid: {path}")
        self.source_extension = self._extension(path)
        if self.source_extension not in self.IMAGE_TYPES.values():
            raise ValueError(f"Provided `path` has an unrecognized extension: {self.source_extension}")
        if self.source_extension == self.IMAGE_TYPES[self.ICO]:
            raise FileExistsError("Provided `path` seems to point to an ICO file; nothing can be done with it.")
        with open(path, "rb") as image:
            self._source_bytes = image.read()

    @staticmethod
    def _extension(path: str) -> str:
        """
        Detects and returns the extension from the given path.

        :param path: Path to get extension from.
        :return: Extension detected from given path.
        """
        return f".{path.lower().split(".")[-1]}"

    @staticmethod
    def _valid_destination_io(path: str) -> bool:
        """
        Validates the ability to write to the provided destination path.
        If this returns ``False``, it is recommended to throw ``IOError``.

        :param path: Destination path string to validate.
        :return: Boolean indicating if provided destination path is valid.
        """
        directory = _dirname(path)
        if not _exists(directory) or not _access(directory, _W_OK):
            return False
        return True

    def _valid_destination_extension(self, path: str, required_extension: str | None = None) -> bool:
        """
        Validates the extension of the provided destination path.
        If this returns ``False``, it is recommended to throw ``ValueError``.

        :param path: Destination path string to validate.
        :param required_extension: Extension to require in the destination path.
        :return: Boolean indicating if provided destination path is valid.
        """
        extension = self._extension(path)
        if extension not in self.IMAGE_TYPES.values() or extension == self.source_extension:
            return False
        if isinstance(required_extension, str):
            if extension != required_extension:
                return False
        return True

    def bitmap_convert(self, output_path: str) -> None:
        """
        Saves bitmap to the specified path and file format.

        :param output_path: Path to save to. Proper extension required.
        :raise IOError: If provided output path is invalid.
        :raise ValueError: If provided output path has an invalid extension.
        """
        if not self._valid_destination_io(output_path):
            raise IOError(f"Provided output path is invalid: {output_path}")
        if not self._valid_destination_extension(output_path):
            raise ValueError(f"Provided output path has an invalid extension: {self._extension(output_path)}")
        with _Image.open(_BytesIO(self._source_bytes)) as image:
            if self._extension(output_path) == self.IMAGE_TYPES[self.JPEG]:
                image = image.convert("RGB")
            image.save(output_path)

    def is_valid_ico(self, minimum_size: int | None = None) -> bool:
        """
        Checks if the source image is able to convert to ICO.

        :param minimum_size: Optionally provide a minimum size integer. If None provided, this check will be skipped.
        :return: True if source can convert to ICO; False if cannot.
        """
        with _Image.open(_BytesIO(self._source_bytes)) as image:
            if image.width != image.height:
                return False
            if isinstance(minimum_size, int):
                if image.width < minimum_size:
                    return False
        return True

    def bitmap_to_ico(self, output_path: str, *resolutions: int) -> None:
        """
        Saves bitmap to ICO to the specified path. Width and height of the bitmap image must be the same value.

        :param output_path: Path to save to. Must have the proper extension.
        :param resolutions: Integers of resolutions to save to the ICO.
        :raise IOError: If provided output path is invalid.
        :raise ValueError: If provided output path does not have proper extension, or if no resolutions were provided, or if source image has invalid dimensions.
        """
        if not self._valid_destination_io(output_path):
            raise IOError(f"Provided output path is invalid: {output_path}")
        if not self._valid_destination_extension(output_path, self.IMAGE_TYPES[self.ICO]):
            raise ValueError(f"Provided output path must have `.ico` extension.")
        if not len(resolutions):
            raise ValueError("No output resolutions were provided.")
        with _Image.open(_BytesIO(self._source_bytes)) as image:
            if not self.is_valid_ico(max(resolutions)):
                raise ValueError(f"Source dimensions are invalid. Got {max(image.width, image.height)} when {max(resolutions)} was required.")
            sizes = [(size, size) for size in sorted(resolutions, reverse=True)]
            resized_images = [image.resize(size, _Image.Resampling.BICUBIC) for size in sizes]
            resized_images[0].save(output_path, sizes=sizes, append_images=resized_images[1:])