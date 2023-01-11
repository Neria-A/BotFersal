class Shovar:
    def __init__(self, _id, code, amount, expiry_date, is_used):
        self._id = _id
        self.code = code
        self.amount = amount
        self.expiry_date = expiry_date
        self.is_used = is_used


    def for_mongo(self):
        return {"_id": self._id, "code": self.code, "amount": self.amount, "expiry_date": self.expiry_date, "is_used": self.is_used}

    def __str__(self):
        return f"code:{self.code}\nAmount:{self.amount}\nDate:{self.expiry_date}"