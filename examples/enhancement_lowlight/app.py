from MicroCore.components.types import FileContent
from MicroCore.utils.reusablepool import ReusablePool
from MicroCore.core import MicroCore
from MicroCore._deploy import deploy_using_config
from MicroCore.communication import launch_api

from pydantic import BaseModel, Field
from PIL import Image
import imageio,io
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
    
    output = None

    with model_pool.auto_release() as model:

        try:
            image = imageio.imread(io.BytesIO(input.image_file.as_bytes()))

            results = Image.fromarray(model.predict(image)[0]['enhanced'])

            img_byte_array = io.BytesIO()
            results.save(img_byte_array, format="PNG")
            output = img_byte_array.getvalue()

        except Exception as e:
            print(e)

    return ImageLowLightEnhancementOutput(output_image_file=output)

if __name__ == "__main__":

    ips = MicroCore(image_low_light_enhancement) #create the service object here
    # deploy_using_config(ips, "./deploy.yaml")
    launch_api(instance_micro_core=ips,port=8080)