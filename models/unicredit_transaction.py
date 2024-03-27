class TransactionUnicredit:
    def __init__(self, data, description, importo, currency):
        self.data = data
        self.description = description
        self.importo = importo
        self.currency = currency

    def __repr__(self):
        return f"Transaction(data={self.data}, description={self.description}, importo={self.importo}, currency={self.currency})"
