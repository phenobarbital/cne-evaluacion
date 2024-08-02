"""This module contains the DirectoryIterator class.
"""
from typing import Union
import asyncio
from pathlib import Path, PurePath
from navconfig.conf import EXTENSION_ACTAS as extensions

class DirectoryIterator:
    """DirectoryIterator.

    This class is a simple iterator that iterates over the files
    in a directory with subdirectories
    """
    def __init__(
        self,
        directory: Union[str, PurePath],
        destination: Union[str, PurePath],
        extensions: list = extensions
    ) -> None:
        if isinstance(directory, str):
            self.directory = Path(directory).resolve()
        elif isinstance(directory, PurePath):
            self.directory = directory
        else:
            raise ValueError(
                (
                    "directory must be a string or a PurePath"
                    f" not {type(directory)}"
                )
            )
        # destination directory:
        if isinstance(destination, str):
            self._destination = Path(destination).resolve()
        else:
            self._destination = destination
        # getting current files on directory
        self.files = self.directory.rglob('*')
        self.ext = extensions
        self._current = None

    def current(self) -> PurePath:
        """current.

        Return current Image Path.
        Returns:
            PurePath: current Image file
        """
        return self._current

    def __aiter__(self):
        return self

    async def __anext__(self):
        loop = asyncio.get_event_loop()
        self._current = await loop.run_in_executor(
            None,
            self._next_file
        )
        if self._current is None:
            raise StopAsyncIteration
        return self._current

    def _next_file(self):
        for image_path in self.files:
            if image_path.is_file() and image_path.suffix.lower() in self.ext:
                relative_path = image_path.parent.relative_to(self.directory)
                destination_path = Path(self._destination).joinpath(
                    relative_path
                ).joinpath(image_path.name)
                return relative_path, destination_path, image_path
        return None

    def make_dir(self, filename):
        """Helper function to create the destination directory, if not exists.
        """
        if filename.parent.exists() is False:
            # Create the destination directory:
            filename.parent.mkdir(parents=True, exist_ok=True)
