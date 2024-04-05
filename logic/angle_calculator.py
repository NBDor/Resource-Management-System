import math
from logic.rekor_dataclasses import Coordinate


def calc_angle_between_two_coordinates(
    agent_latest_location: Coordinate, agent_current_location: Coordinate
) -> float:
    is_latest_location_valid = (
        agent_latest_location is not None
        and agent_latest_location.x != -1
        and agent_latest_location.y != -1
    )
    if is_latest_location_valid:
        return calculate_bearing_between_two_coordinates(
            agent_latest_location, agent_current_location
        )
    else:
        return -1


def calculate_bearing_between_two_coordinates(
    point_a: Coordinate, point_b: Coordinate
) -> float:
    deg2rad = math.pi / 180
    lat_a = point_a.x
    lat_b = point_b.x
    lon_a = point_a.y
    lon_b = point_b.y

    x = math.cos(lat_b) * math.sin((lon_b - lon_a))
    y = math.cos(lat_a) * math.sin(lat_b) - math.sin(lat_a) * math.cos(
        lat_b
    ) * math.cos((lon_b - lon_a))

    bearing = math.atan2(x, y) / deg2rad
    if bearing < 0:
        bearing = bearing + 360

    return bearing
