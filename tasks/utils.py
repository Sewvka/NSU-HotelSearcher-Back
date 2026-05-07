
def convert_distance(distance, distance_type: str) -> float:
    if distance_type != "км":
        distance = distance / 1000
    return distance