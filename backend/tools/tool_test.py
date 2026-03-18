import json
import os

# Pass parts as separate arguments so os.path handles the slash
path = "D:\\Telios_638\\config\\tools.json"
print(path)

try:
    # Adding encoding='utf-8' is a best practice for JSON
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    print(json.dumps(data, indent=4))
    print(type(data))

except FileNotFoundError:
    print(f"Error: The file at {path} was not found.")
except json.JSONDecodeError:
    print(f"Error: Failed to decode JSON from {path}. Check your syntax!")