import numpy as np


class CNNService:
    def __init__(self, loader):
        self.model = loader.model
        self.mean = loader.mean
        self.std = loader.std
        self.class_to_label = loader.class_to_label

    def _normalize(self, window):
        return (window - self.mean) / self.std

    def _majority_vote(self, predictions):
        return max(set(predictions), key=predictions.count)

    def predict(self, rssi_matrix, window_size=20):
        try:
            data = np.array(rssi_matrix)

            if data.shape[0] != 5:
                raise ValueError("Expected 5 beacons")

            predictions = []

            num_windows = data.shape[1] - window_size + 1

            for i in range(num_windows):
                window = data[:, i:i + window_size]

                window = self._normalize(window)

                X = window.reshape(1, 5, window_size, 1).astype("float32")

                pred = self.model.predict(X, verbose=0)
                pred_class = int(np.argmax(pred))

                predictions.append(pred_class)

            if not predictions:
                raise ValueError("Not enough data for prediction")

            final_class = self._majority_vote(predictions)

            return str(self.class_to_label[final_class])

        except Exception as e:
            raise RuntimeError("Prediction failed") from e