import json

class jsonOperations:
    def jsonLoad(jsonName: str) -> dict:
        with open(f"files/{jsonName}.json", "r+") as file:
            return json.load(file) 
    
    def jsonDump(jsonName: str, dumpName: dict):
        with open(f"files/{jsonName}.json", "w") as file:
            json.dump(dumpName, file, indent=4)  