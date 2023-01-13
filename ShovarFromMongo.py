import json

class ShovarFromMongo:

    def __init__(self, dict1):
        self.__dict__.update(dict1)

    def dict_to_shovar(dict):
        # using json.loads method and passing json.dumps
        # method and custom object hook as arguments
        return json.loads(json.dumps(dict, indent=3, sort_keys=True, default=str), object_hook=ShovarFromMongo)
