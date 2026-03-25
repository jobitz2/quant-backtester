class BaseStrategy:
    def generate_signals(self, data):
        raise NotImplementedError('Subclasses must implement generate_signals')