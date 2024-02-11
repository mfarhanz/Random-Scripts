Python script utilising Tkinter, Python Imaging Library (Pillow) and OpenCV to create a GUI for displaying sign detection results on static images, videos or live feed.
Uses the YOLOv5 Object Detection Library based on Tensorflow and PyTorch for functioning.

Requirements:-  
- [YOLOv5 Object Detection](https://github.com/ultralytics/yolov5)
- pip (included with Python installation)

Execution:-  
- Run `pip install -r requirements.txt coremltools onnx onnx-simplifier onnxruntime openvino-dev tensorflow-cpu` in terminal
- Extract YOLOv5 to a directory on your pc
- Extract start.py to the YOLOv5 main directory
- Run start.py (double click or `python start.py` in terminal)
- To detect on an image or video file, enter file address in the address bar, and hit Detect
- For detailed logging, run in terminal
