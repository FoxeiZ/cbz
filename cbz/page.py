from __future__ import annotations

import io
import base64

from typing import Union

from pathlib import Path

import magic
import mimetypes
import imagesize

from cbz.constants import IMAGE_FORMAT
from cbz.models import PageModel


class PageInfo(PageModel):
    """
    Model for representing comic book pages with additional content handling capabilities.
    """

    def __init__(self, content: bytes, **kwargs):
        """
        Initializes a PageInfo instance.

        Args:
            content (bytes): The content of the page in bytes.
            **kwargs: Additional keyword arguments passed to the base class initializer.
        """
        super(PageInfo, self).__init__(**kwargs)
        self.content = content

    @property
    def content(self) -> bytes:
        """
        Getter property for the content of the page.

        Returns:
            bytes: The content of the page.
        """
        return self.__content

    @content.setter
    def content(self, value: bytes) -> None:
        """
        Setter property for the content of the page. Automatically extracts image metadata.

        Args:
            value (bytes): The content of the page in bytes.
        """

        filetype = magic.from_buffer(value, mime=True)
        self.suffix = mimetypes.guess_extension(filetype) or ".bin"
        assert self.suffix in IMAGE_FORMAT, f"Unsupported image format: {self.suffix}"

        with io.BytesIO(value) as file_io:
            file_io.seek(0)
            width, height = imagesize.get(file_io)

        if not isinstance(width, int) or not isinstance(height, int):
            width, height = 0, 0

        self.image_width = width
        self.image_height = height
        self.image_size = len(value)
        self.__content = value

    @classmethod
    def loads(cls, data: Union[str, bytes], **kwargs) -> PageInfo:
        """
        Class method to create a PageInfo instance from bytes or base64-encoded data.

        Args:
            data (Union[str, bytes]): The data representing the page content.
            **kwargs: Additional keyword arguments passed to the PageInfo initializer.

        Returns:
            PageInfo: The created PageInfo instance.

        Raises:
            ValueError: If the data type is neither str nor bytes.
        """
        if isinstance(data, str):
            data = base64.b64decode(data)
        if not isinstance(data, bytes):
            raise ValueError(f"Expecting Bytes or Base64 input, got {data!r}")
        return cls(data, **kwargs)

    @classmethod
    def load(cls, path: Union[Path, str], **kwargs) -> PageInfo:
        """
        Class method to create a PageInfo instance from a file path.

        Args:
            path (Union[Path, str]): The path to the file containing the page content.
            **kwargs: Additional keyword arguments passed to the PageInfo initializer.

        Returns:
            PageInfo: The created PageInfo instance.

        Raises:
            ValueError: If the path type is neither Path nor str.
            FileNotFoundError: If the specified file path does not exist.
        """
        if not isinstance(path, (Path, str)):
            raise ValueError(f"Expecting Path object or path string, got {path!r}")
        with Path(path).open(mode="rb") as f:
            return cls(f.read(), **kwargs)

    def save(self, path: Union[Path, str]) -> None:
        """
        Saves the page content to a file.

        Args:
            path (Union[Path, str]): The path where the content should be saved.
        """
        with Path(path).open(mode="wb") as f:
            f.write(self.content)
