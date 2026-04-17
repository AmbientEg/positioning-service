
class Preprocessor:
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def normalize(self, window):
        return (window - self.mean) / self.std