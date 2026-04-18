import onnxruntime as ort
import pickle


class ModelLoader:
    def __init__(self, model_path, scaler_path, mapping_path):

        # load ONNX model
        self.session = ort.InferenceSession(model_path)

        # load scaler
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
            self.mean = scaler["mean"]
            self.std = scaler["std"]

        # load label mapping
        with open(mapping_path, "rb") as f:
            mapping = pickle.load(f)
            self.class_to_label = mapping["class_to_label"]