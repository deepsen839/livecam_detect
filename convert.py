from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.export(
    format="onnx",
    imgsz=640,
    dynamic=False,
    simplify=True,
)
from onnxruntime.quantization import (
    quantize_dynamic,
    QuantType,
)

quantize_dynamic(
    "yolov8n.onnx",
    "yolov8n_int8.onnx",
    weight_type=QuantType.QInt8,
)