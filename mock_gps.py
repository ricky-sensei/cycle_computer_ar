import math
import time


class MockGPS:
    def __init__(self, start_lat=30.0125, start_lon=141.0961, altitude_m=100.0):
        self.start_time = time.monotonic()
        self.start_lat = start_lat
        self.start_lon = start_lon
        self.altitude_m = altitude_m

    def read(self):
        elapsed = time.monotonic() - self.start_time
        speed_kmh = self._speed_kmh(elapsed)
        heading_deg = self._heading_deg(elapsed)

        distance_m = (speed_kmh / 3.6) * elapsed
        lat, lon = self._move_from_start(distance_m, heading_deg)

        return {
            "timestamp": elapsed, # 経過時間
            "fix": elapsed >= 3.0, # GPSが測位できているかどうか:
            "lat": lat,
            "lat_dir": "N" if lat >= 0 else "S",
            "lon": lon,
            "lon_dir": "E" if lon >= 0 else "W",
            "speed_kmh": speed_kmh,
            "altitude_m": self.altitude_m + math.sin(elapsed / 20.0) * 3.0,
            "heading_deg": heading_deg,
            "satellites": 8 if elapsed >= 3.0 else 0,
        }

    def _speed_kmh(self, elapsed):
        # 22キロあたりでの数値を吐き出す
        base_speed = 22.0
        variation = math.sin(elapsed / 8.0) * 5.0
        return max(0.0, base_speed + variation)

    def _heading_deg(self, elapsed):
        return (84.0 + math.sin(elapsed / 18.0) * 12.0) % 360.0

    def _move_from_start(self, distance_m, heading_deg):
        earth_radius_m = 6378137.0
        heading_rad = math.radians(heading_deg)
        lat_rad = math.radians(self.start_lat)

        north_m = math.cos(heading_rad) * distance_m
        east_m = math.sin(heading_rad) * distance_m

        lat = self.start_lat + math.degrees(north_m / earth_radius_m)
        lon = self.start_lon + math.degrees(east_m / (earth_radius_m * math.cos(lat_rad)))
        return lat, lon
