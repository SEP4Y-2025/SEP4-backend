from bson import ObjectId


def some_utility_function(param1, param2):
    # Example utility function that performs a calculation
    return param1 + param2


def another_utility_function(data):
    # Example utility function that processes data
    processed_data = [item for item in data if item is not None]
    return processed_data


def convert_object_ids(obj):
    if isinstance(obj, dict):  # If obj is a dictionary, recursively convert values.
        return {k: convert_object_ids(v) for k, v in obj.items()}
    elif isinstance(obj, list):  # If obj is a list, recursively convert items.
        return [convert_object_ids(item) for item in obj]
    elif isinstance(obj, ObjectId):  # If it's an ObjectId, convert to string.
        return str(obj)
    else:
        return obj


# Additional utility functions can be added here as needed.
