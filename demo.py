import io

import numpy as np
from pydantic import BaseModel, Field
from src.MicroCore.components.types import FileContent
from src.MicroCore.utils.reusablepool import ReusablePool
from src.MicroCore.core import MicroCore
from src.MicroCore.communication import launch_api
from src.MicroCore.gui import launch_dash_ui
from src.MicroCore._deploy import deploy_using_config
from PIL import Image
import imageio
import light_side as ls

def create_model_objects():
    model = ls.Enhancer.from_pretrained('zerodce_3-32-16_zerodce')
    model.eval()
    return model

model_pool = ReusablePool(size=10, reusable_factory=create_model_objects) #create resource pool with size 10

class ImageLowLightEnhancementInput(BaseModel):
    image_file: FileContent = Field(..., mime_type="image/*")


class ImageLowLightEnhancementOutput(BaseModel):
    output_image_file: FileContent = Field(
        ...,
        mime_type="image/*",
        description="low-light image enhancement",
    )


def image_low_light_enhancement(
    input: ImageLowLightEnhancementInput,
) -> ImageLowLightEnhancementOutput:
    
    image = imageio.imread(io.BytesIO(input.image_file.as_bytes()))

    model = model_pool.acquire()
    results = Image.fromarray(model.predict(image)[0]['enhanced'])
    model_pool.release(model)

    img_byte_array = io.BytesIO()
    results.save(img_byte_array, format="PNG")
    return ImageLowLightEnhancementOutput(output_image_file=img_byte_array.getvalue())


if __name__ == "__main__":
    ips = MicroCore(image_low_light_enhancement) #create the service object here

    deploy_using_config(ips, "/home/benjamin/project/MicroCore/examples/enhancement_lowlight/deploy.yaml")

    # launch_api(ips, 8080, "0.0.0.0")
    # launch_dash_ui(ips,port=8052)