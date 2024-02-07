from MicroCore.components.types import FileContent
from MicroCore.utils.reusablepool import ReusablePool
from MicroCore.core import MicroCore
from MicroCore._deploy import deploy_using_config,launch_api

from ultralytics import YOLO
from pydantic import BaseModel, Json, Field
import json
from typing import Any,Dict
from PIL import Image
import imageio,io,uuid,tracemalloc
from time import time

def create_model_objects():
    model  = YOLO("yolov8n.pt")
    return model

model_pool = ReusablePool(size=5, reusable_factory=create_model_objects) #create resource pool with size 10

class yolov8_Input(BaseModel):
    image_file: FileContent = Field(
        ..., mime_type="image/*"
    )

class yolov8_Output(BaseModel):
    output_json: Dict[str, Any] = Field(
        ...,
        mime_type="application/json",
        description="yolov8 detection bbox",
    )

def yolov8_detection(
    input: yolov8_Input,
) -> yolov8_Output:

    detection_bbox_list = None
    results_dict = None

    with model_pool.auto_release() as model:

        try:
            image = imageio.imread(io.BytesIO(input.image_file.as_bytes()))

            # start memory profiling and timing
            tracemalloc.start()
            start_time = time()
            try:
                results = model.predict(image)
                detection_bbox = results[0].boxes.data #detection_bbox is a tensor object
                detection_bbox_list = detection_bbox.cpu().numpy().tolist()
            except Exception as e:
                print(e)
            
            # record memory used and duration
            _, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            duration = time() - start_time

            results_dict = {
                "Unique ID": str(uuid.uuid4()),
                "Outcome": "object detected",
                "Peak memory": f"{peak_mem/(1024**2):.2f} MB",
                "Duration": f"{duration} seconds",
                "Results": detection_bbox_list
            }
        except Exception as e:
            print(e)
    return yolov8_Output(output_json=results_dict)

if __name__ == "__main__":

    service_core = MicroCore(yolov8_detection) #create the service object here
    launch_api(service_core,host="0.0.0.0",port=8080)
