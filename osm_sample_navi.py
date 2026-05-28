#!/usr/bin/env python3
"""
OpenStreetMap + OSRM navigation route sample.

osm_sample.py の「OSMタイルを取得して画像に合成する」処理を使い、
その上にOSRMで取得したナビルートを描画します。

Example:
    python osm_sample_navi.py \
        --start-lat 35.681236 --start-lon 139.767125 \
        --end-lat 35.658581 --end-lon 139.745433 \
        --zoom 15 --output osm_navi_route.png

Notes:
    - OpenStreetMapは地図データです。ルート計算はOSRMを使います。
    - OSRM公開サーバーはデモ用途です。本番利用では自前OSRMや有償APIを検討してください。
      https://project-osrm.org/docs/
"""

from __future__ import annotations

import argparse
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, ImageDraw
except ImportError as exc:
    raise SystemExit(
        "Pillow is required. Install it with: python -m pip install Pillow"
    ) from exc

from osm_sample import DEFAULT_CACHE_DIR, TILE_SIZE, fetch_tile, lat_lon_to_tile


DEFAULT_OUTPUT = Path("osm_navi_route.png")
DEFAULT_USER_AGENT = "cycle-computer-ar-osm-navi-sample/0.1 (local development)"
DEFAULT_OSRM_BASE_URL = "https://router.project-osrm.org"

# LatLon は (緯度, 経度)、LonLat はGeoJSONで使われる (経度, 緯度) です。
LatLon = tuple[float, float]
LonLat = tuple[float, float]


def lat_lon_to_pixel(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    # ルート線を描くため、緯度経度を世界地図全体でのピクセル位置に変換します。
    lat_rad = math.radians(lat)
    scale = 2**zoom * TILE_SIZE
    x = (lon + 180.0) / 360.0 * scale
    y = (
        (1.0 - math.asinh(math.tan(lat_rad)) / math.pi)
        / 2.0
        * scale
    )
    return x, y


def osrm_route_url(
    base_url: str,
    profile: str,
    start: LatLon,
    end: LatLon,
) -> str:
    # OSRM APIは「経度,緯度」の順で座標を渡します。
    coordinates = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    query = urllib.parse.urlencode(
        {
            "overview": "full",
            "geometries": "geojson",
            "steps": "true",
        }
    )
    return f"{base_url.rstrip('/')}/route/v1/{profile}/{coordinates}?{query}"


def fetch_route(
    base_url: str,
    profile: str,
    start: LatLon,
    end: LatLon,
    user_agent: str,
) -> tuple[list[LonLat], float, float, list[str]]:
    # OSRMに出発地から目的地までのルートを問い合わせます。
    request = urllib.request.Request(
        osrm_route_url(base_url, profile, start, end),
        headers={"User-Agent": user_agent},
    )

    print(f"Requesting route with OSRM profile: {profile}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP error while requesting OSRM route: {exc}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error while requesting OSRM route: {exc}") from exc

    if data.get("code") != "Ok" or not data.get("routes"):
        raise RuntimeError(f"OSRM did not return a route: {data.get('code')}")

    route = data["routes"][0]
    coordinates = [
        (float(lon), float(lat))
        for lon, lat in route["geometry"]["coordinates"]
    ]
    instructions = extract_instructions(route)
    return coordinates, float(route["distance"]), float(route["duration"]), instructions


def extract_instructions(route: dict) -> list[str]:
    # 画像描画が主目的なので、案内文はコンソール確認用に簡単な形で作ります。
    instructions: list[str] = []
    for leg in route.get("legs", []):
        for step in leg.get("steps", []):
            maneuver = step.get("maneuver", {})
            name = step.get("name") or "unnamed road"
            modifier = maneuver.get("modifier")
            kind = maneuver.get("type", "continue")
            distance = float(step.get("distance", 0.0))
            direction = f" {modifier}" if modifier else ""
            instructions.append(f"{kind}{direction} onto {name} ({distance:.0f}m)")
    return instructions


def route_bounds(route: Iterable[LonLat], start: LatLon, end: LatLon) -> tuple[float, float, float, float]:
    # ルート全体が収まる緯度経度の範囲を求めます。
    lats = [start[0], end[0]]
    lons = [start[1], end[1]]
    for lon, lat in route:
        lats.append(lat)
        lons.append(lon)
    return min(lats), min(lons), max(lats), max(lons)


def tile_range_for_bounds(
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    zoom: int,
    padding_tiles: int,
) -> tuple[int, int, int, int]:
    # osm_sample.py の lat_lon_to_tile を使い、ルート範囲に必要なタイル番号を求めます。
    min_x, max_y = lat_lon_to_tile(min_lat, min_lon, zoom)
    max_x, min_y = lat_lon_to_tile(max_lat, max_lon, zoom)
    return (
        min_x - padding_tiles,
        min_y - padding_tiles,
        max_x + padding_tiles,
        max_y + padding_tiles,
    )


def build_base_map(
    zoom: int,
    min_tile_x: int,
    min_tile_y: int,
    max_tile_x: int,
    max_tile_y: int,
    cache_dir: Path,
    user_agent: str,
    delay_seconds: float,
) -> Image.Image:
    # osm_sample.py の fetch_tile を使ってタイルを取得し、ルート全体の背景地図を作ります。
    width = (max_tile_x - min_tile_x + 1) * TILE_SIZE
    height = (max_tile_y - min_tile_y + 1) * TILE_SIZE
    image = Image.new("RGB", (width, height), "white")

    for tile_y in range(min_tile_y, max_tile_y + 1):
        for tile_x in range(min_tile_x, max_tile_x + 1):
            path = fetch_tile(
                tile_x,
                tile_y,
                zoom,
                cache_dir,
                user_agent,
                delay_seconds,
            )
            tile = Image.open(path).convert("RGB")
            paste_x = (tile_x - min_tile_x) * TILE_SIZE
            paste_y = (tile_y - min_tile_y) * TILE_SIZE
            image.paste(tile, (paste_x, paste_y))
    return image


def route_to_image_points(route: list[LonLat], zoom: int, min_tile_x: int, min_tile_y: int) -> list[tuple[int, int]]:
    # 世界全体でのピクセル位置から、この画像の左上位置を引くと画像内座標になります。
    offset_x = min_tile_x * TILE_SIZE
    offset_y = min_tile_y * TILE_SIZE
    points = []
    for lon, lat in route:
        pixel_x, pixel_y = lat_lon_to_pixel(lat, lon, zoom)
        points.append((round(pixel_x - offset_x), round(pixel_y - offset_y)))
    return points


def draw_route(
    image: Image.Image,
    route: list[LonLat],
    start: LatLon,
    end: LatLon,
    zoom: int,
    min_tile_x: int,
    min_tile_y: int,
) -> None:
    draw = ImageDraw.Draw(image)
    points = route_to_image_points(route, zoom, min_tile_x, min_tile_y)
    if len(points) >= 2:
        # 白い太線の上に青い線を重ねると、地図上でルートが見やすくなります。
        draw.line(points, fill=(255, 255, 255), width=12)
        draw.line(points, fill=(0, 96, 255), width=7)

    draw_marker(draw, start, zoom, min_tile_x, min_tile_y, fill=(0, 170, 80), label="S")
    draw_marker(draw, end, zoom, min_tile_x, min_tile_y, fill=(220, 40, 40), label="G")


def draw_marker(
    draw: ImageDraw.ImageDraw,
    lat_lon: LatLon,
    zoom: int,
    min_tile_x: int,
    min_tile_y: int,
    fill: tuple[int, int, int],
    label: str,
) -> None:
    pixel_x, pixel_y = lat_lon_to_pixel(lat_lon[0], lat_lon[1], zoom)
    x = round(pixel_x - min_tile_x * TILE_SIZE)
    y = round(pixel_y - min_tile_y * TILE_SIZE)
    radius = 12

    draw.ellipse(
        (x - radius, y - radius, x + radius, y + radius),
        fill=fill,
        outline=(255, 255, 255),
        width=3,
    )
    draw.text((x - 4, y - 7), label, fill=(255, 255, 255))


def save_navi_map(
    start: LatLon,
    end: LatLon,
    zoom: int,
    padding_tiles: int,
    max_tiles: int,
    profile: str,
    osrm_base_url: str,
    cache_dir: Path,
    output_path: Path,
    user_agent: str,
    delay_seconds: float,
) -> None:
    route, distance_m, duration_s, instructions = fetch_route(
        osrm_base_url,
        profile,
        start,
        end,
        user_agent,
    )
    min_lat, min_lon, max_lat, max_lon = route_bounds(route, start, end)
    min_tile_x, min_tile_y, max_tile_x, max_tile_y = tile_range_for_bounds(
        min_lat,
        min_lon,
        max_lat,
        max_lon,
        zoom,
        padding_tiles,
    )

    # 高ズームや長距離指定でタイルを取りすぎないための安全装置です。
    tile_count = (max_tile_x - min_tile_x + 1) * (max_tile_y - min_tile_y + 1)
    if tile_count > max_tiles:
        raise SystemExit(
            f"Route would fetch {tile_count} tiles. "
            f"Lower --zoom, reduce --padding-tiles, or raise --max-tiles."
        )

    image = build_base_map(
        zoom,
        min_tile_x,
        min_tile_y,
        max_tile_x,
        max_tile_y,
        cache_dir,
        user_agent,
        delay_seconds,
    )
    draw_route(image, route, start, end, zoom, min_tile_x, min_tile_y)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)

    print(f"Saved: {output_path}")
    print(f"Distance: {distance_m / 1000:.2f}km")
    print(f"Duration: {duration_s / 60:.1f}min")
    print(f"Tiles: {tile_count}")
    if instructions:
        print("First instructions:")
        for instruction in instructions[:5]:
            print(f"  - {instruction}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Draw an OSRM navigation route on OpenStreetMap tiles."
    )
    parser.add_argument("--start-lat", type=float, required=True)
    parser.add_argument("--start-lon", type=float, required=True)
    parser.add_argument("--end-lat", type=float, required=True)
    parser.add_argument("--end-lon", type=float, required=True)
    parser.add_argument("--zoom", type=int, default=15)
    parser.add_argument(
        "--profile",
        default="driving",
        help=(
            "OSRM profile name. The public demo server commonly supports "
            "'driving'; use 'bike' when your OSRM server provides it."
        ),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--osrm-base-url", default=DEFAULT_OSRM_BASE_URL)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--padding-tiles", type=int, default=1)
    parser.add_argument(
        "--max-tiles",
        type=int,
        default=64,
        help="Safety limit for OSM tile downloads. Default: 64.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not (0 <= args.zoom <= 19):
        raise SystemExit("--zoom must be between 0 and 19.")
    if args.padding_tiles < 0:
        raise SystemExit("--padding-tiles must be 0 or greater.")
    if args.max_tiles <= 0:
        raise SystemExit("--max-tiles must be greater than 0.")

    save_navi_map(
        start=(args.start_lat, args.start_lon),
        end=(args.end_lat, args.end_lon),
        zoom=args.zoom,
        padding_tiles=args.padding_tiles,
        max_tiles=args.max_tiles,
        profile=args.profile,
        osrm_base_url=args.osrm_base_url,
        cache_dir=args.cache_dir,
        output_path=args.output,
        user_agent=args.user_agent,
        delay_seconds=args.delay,
    )


if __name__ == "__main__":
    main()
