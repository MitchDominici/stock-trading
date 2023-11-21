class TradeSignal:
    signal: str
    name: str
    description: str

    def __init__(self, signal: str, name: str, description: str):
        self.signal = signal
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            'signal': self.signal,
            'name': self.name,
            'description': self.description
        }
