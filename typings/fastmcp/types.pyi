from typing import Any, List, Union

class TextContent:
    content: str

class ImageContent:
    content: bytes

class EmbeddedResource:
    content: Union[str, bytes]

class TextResourceContents:
    content: str

class BlobResourceContents:
    content: bytes