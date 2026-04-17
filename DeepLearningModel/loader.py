import tensorflow as tf
import pickle


class ModelLoader:
    def __init__(self, model_path, scaler_path, mapping_path):
        # load model
        self.model = tf.keras.models.load_model(model_path)

        # load scaler
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
            self.mean = scaler["mean"]
            self.std = scaler["std"]

        # load label mapping
        with open(mapping_path, "rb") as f:
            mapping = pickle.load(f)
            self.class_to_label = mapping["class_to_label"]