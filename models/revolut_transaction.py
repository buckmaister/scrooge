class TransactionRevolut:
    def __init__(self, type, product, started_date, completed_date, description, amount, fee, currency, state, balance):
        self.type = type
        self.product = product
        self.started_date = started_date
        self.completed_date = completed_date
        self.description = description
        self.amount = amount
        self.fee = fee
        self.currency = currency
        self.state = state
        self.balance = balance

    def __repr__(self):
        return f"Transaction(started_date={self.started_date}, completed_date={self.completed_date},type={self.type}, product={self.product}, description={self.description}, amount={self.amount}, fee={self.fee}, currency={self.currency}, state={self.state}, balance={self.balance})"