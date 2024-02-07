from MicroCore.components.types import ImageFileContent
from MicroCore.utils.reusablepool import ReusablePool
from MicroCore.core import MicroCore
from MicroCore._deploy import deploy_using_config

from pydantic import BaseModel, Field
from typing import Dict
from PIL import Image
import imageio,io
import light_side as ls

def create_model_objects():
    model = ls.Enhancer.from_pretrained('zerodce_3-32-16_zerodce')
    model.eval()
    return model

model_pool = ReusablePool(size=10, reusable_factory=create_model_objects) #create resource pool with size 10

class ImageLowLightEnhancementInput(BaseModel):
    image_files: Dict[str, ImageFileContent] = Field(..., mime_type="image/*")

class ImageLowLightEnhancementOutput(BaseModel):
    output_image_files: Dict[str, ImageFileContent] = Field(
        ..., 
        mime_type="image/*", 
        description="Dictionary of low-light enhanced images mapped by filename"
    )

def image_low_light_enhancement(
    input: ImageLowLightEnhancementInput,
) -> ImageLowLightEnhancementOutput:
    
    output_images = {}
    raw_images = []
    raw_images_filename = list(input.image_files.keys())

    with model_pool.auto_release() as model:

        try:
            for raw_image in list(input.image_files.values()):
                raw_image = imageio.imread(io.BytesIO(raw_image.as_bytes()))
                raw_images.append(raw_image)

            result_images = model.predict(raw_images)

            for filename, result_image in zip(raw_images_filename, result_images):
                result_image = Image.fromarray(result_image['enhanced'])
                img_byte_array = io.BytesIO()
                result_image.save(img_byte_array, format="PNG")
                output_images[filename] = img_byte_array.getvalue()

        except Exception as e:
            print(e)

    return ImageLowLightEnhancementOutput(output_image_files=output_images)

if __name__ == "__main__":

    ips = MicroCore(image_low_light_enhancement) #create the service object here
    # deploy_using_config(ips, "./deploy.yaml")
    deploy_using_config(ips, "/home/benjamin/project/MicroCore/examples/enhancement_lowlight_batch/deploy.yaml")