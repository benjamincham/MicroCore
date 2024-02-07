import base64
from typing import Any, Dict
from PIL import Image
from io import BytesIO
import numpy as np

class ImageFileContent(str):
    ALLOWED_FORMATS = ['PNG', 'BMP','JPEG','TIFF']
    
    def as_bytes(self) -> bytes:
        return base64.b64decode(self)

    def as_str(self) -> str:
        return self.as_bytes().decode()
    
    def as_np_image(self):
        return np.frombuffer(self.as_bytes(),np.uint8)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="byte")
        
    @classmethod
    def validate_image_byte_string(cls, value):
        if isinstance(value, str):
            try:
                byte_string = base64.b64decode(value, validate=True)
                image_io = BytesIO(byte_string)
                img = Image.open(image_io)
                image_format = img.format.upper()

                if image_format not in cls.ALLOWED_FORMATS:
                    raise ValueError(f"Unsupported format: {image_format}. Allowed formats are {', '.join(cls.ALLOWED_FORMATS)}")

                
            except Exception as e:
                raise ValueError(f"The byte string is not a valid image. Reason: {str(e)}")
        return value
        
    @classmethod
    def __get_validators__(cls) -> Any:  # type: ignore
        yield cls.validate_image_byte_string
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "ImageFileContent":
        if isinstance(value, ImageFileContent):
            return value
        elif isinstance(value, str):
            return ImageFileContent(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return ImageFileContent(base64.b64encode(value).decode())
        else:
            raise Exception("Wrong type")

class FileContent(str):
    def as_bytes(self) -> bytes:
        return base64.b64decode(self, validate=True)

    def as_str(self) -> str:
        return self.as_bytes().decode()

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="byte")

    @classmethod
    def __get_validators__(cls) -> Any:  # type: ignore
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "FileContent":
        if isinstance(value, FileContent):
            return value
        elif isinstance(value, str):
            return FileContent(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return FileContent(base64.b64encode(value).decode())
        else:
            raise Exception("Wrong type")
