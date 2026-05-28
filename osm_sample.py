#!/usr/bin/env python3
"""
OpenStreetMap tile sample.

指定した緯度経度の周辺地図タイルを取得し、1枚のPNG画像に合成します。

Example:
    python osm_sample.py --lat 35.681236 --lon 139.767125 --zoom 16 --radius 1

Notes:
    - OpenStreetMap公式タイルサーバーは共有資源です。
      User-Agentを明示し、取得済みタイルはローカルキャッシュを使います。
    - 大量取得や事前の広範囲ダウンロードには使わないでください。
      https://operations.osmfoundation.org/policies/tiles/
"""

from __future__ import annotations

import argparse
import math
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    # Pillowは画像を読み込んだり、複数の画像を1枚に合成したりするライブラリです。
    from PIL import Image
except ImportError as exc:
    raise SystemExit(
        "Pillow is required. Install it with: python -m pip install Pillow"
    ) from exc


# OSMの標準的な地図タイルは 256x256 ピクセルです。
TILE_SIZE = 256

# 一度ダウンロードした地図タイルはここに保存します。
# 2回目以降はネットワーク通信せず、このキャッシュを読みます。
DEFAULT_CACHE_DIR = Path(".osm_tile_cache")

# 何も指定しない場合の出力ファイル名です。
DEFAULT_OUTPUT = Path("osm_map.png")

# OSM公式タイルサーバーの利用ポリシーでは、アプリを識別できるUser-Agentが必要です。
DEFAULT_USER_AGENT = "cycle-computer-ar-osm-sample/0.1 (local development)"


def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    """緯度経度を、OSMのタイル番号 x/y に変換します。"""
    # OSMの地図はズームごとに細かい正方形タイルへ分割されています。
    # 例えば zoom=0 は世界全体が1枚、zoomが1増えるごとに縦横2倍に分割されます。
    lat_rad = math.radians(lat)
    scale = 2**zoom

    # 経度は -180 から +180 の範囲なので、0からscaleまでの値に変換します。
    x = int((lon + 180.0) / 360.0 * scale)

    # 緯度はメルカトル図法の計算式でタイル上のy座標へ変換します。
    # 北に行くほどyが小さく、南に行くほどyが大きくなります。
    y = int(
        (1.0 - math.asinh(math.tan(lat_rad)) / math.pi)
        / 2.0
        * scale
    )
    return x, y


def tile_url(x: int, y: int, zoom: int) -> str:
    # OSM公式タイルサーバーのURL形式です。
    # z=ズーム、x/y=タイル番号です。
    return f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"


def cache_path(cache_dir: Path, x: int, y: int, zoom: int) -> Path:
    # キャッシュは zoom/x/y.png という階層で保存します。
    # URLの構造に近いので、どのタイルか分かりやすくなります。
    return cache_dir / str(zoom) / str(x) / f"{y}.png"


def fetch_tile(
    x: int,
    y: int,
    zoom: int,
    cache_dir: Path,
    user_agent: str,
    delay_seconds: float,
) -> Path:
    """タイル1枚を取得します。既にキャッシュがあれば通信しません。"""
    path = cache_path(cache_dir, x, y, zoom)

    # 既に保存済みなら、そのファイルをそのまま使います。
    # GPS更新のたびに同じ地図を取りに行かないための重要な処理です。
    if path.exists():
        return path

    # 保存先フォルダが無ければ作ります。
    path.parent.mkdir(parents=True, exist_ok=True)

    # urllibでHTTPリクエストを作ります。
    # User-Agentを入れて、どのアプリからのアクセスか分かるようにします。
    request = urllib.request.Request(
        tile_url(x, y, zoom),
        headers={"User-Agent": user_agent},
    )

    print(f"Downloading z={zoom} x={x} y={y}")
    try:
        # タイル画像をダウンロードして、そのままPNGファイルとして保存します。
        with urllib.request.urlopen(request, timeout=15) as response:
            path.write_bytes(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP error while fetching {tile_url(x, y, zoom)}: {exc}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error while fetching {tile_url(x, y, zoom)}: {exc}") from exc

    if delay_seconds > 0:
        # 短時間に連続アクセスしすぎないよう、少し待ちます。
        time.sleep(delay_seconds)
    return path


def build_map_image(
    center_lat: float,
    center_lon: float,
    zoom: int,
    radius: int,
    cache_dir: Path,
    output_path: Path,
    user_agent: str,
    delay_seconds: float,
) -> None:
    # 指定された中心座標が含まれるタイル番号を求めます。
    center_x, center_y = lat_lon_to_tile(center_lat, center_lon, zoom)

    # radius=1なら 3x3、radius=2なら 5x5 のタイルを取得します。
    tile_count = radius * 2 + 1

    # 合成先の空画像を作ります。
    # 例: 3x3タイルなら 768x768 ピクセルになります。
    image = Image.new("RGB", (tile_count * TILE_SIZE, tile_count * TILE_SIZE))

    # 中心タイルの周囲を順番に取得して、1枚の大きな画像に貼り付けます。
    for tile_y in range(center_y - radius, center_y + radius + 1):
        for tile_x in range(center_x - radius, center_x + radius + 1):
            path = fetch_tile(
                tile_x,
                tile_y,
                zoom,
                cache_dir,
                user_agent,
                delay_seconds,
            )
            tile = Image.open(path).convert("RGB")

            # タイル番号から、合成画像内の貼り付け位置を計算します。
            paste_x = (tile_x - (center_x - radius)) * TILE_SIZE
            paste_y = (tile_y - (center_y - radius)) * TILE_SIZE
            image.paste(tile, (paste_x, paste_y))

    # 出力先フォルダが無ければ作り、完成画像を保存します。
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    print(f"Saved: {output_path}")
    print(f"Center tile: z={zoom} x={center_x} y={center_y}")
    print(f"Tile requests needed without cache: {tile_count * tile_count}")


def parse_args() -> argparse.Namespace:
    # コマンドライン引数を定義します。
    # 例: --lat 35.681236 のように指定できるようになります。
    parser = argparse.ArgumentParser(
        description="Download nearby OpenStreetMap tiles and merge them into one PNG."
    )
    parser.add_argument("--lat", type=float, required=True, help="Center latitude.")
    parser.add_argument("--lon", type=float, required=True, help="Center longitude.")
    parser.add_argument("--zoom", type=int, default=16, help="OSM zoom level. Default: 16.")
    parser.add_argument(
        "--radius",
        type=int,
        default=1,
        help="Tile radius around the center tile. 1 means 3x3 tiles. Default: 1.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output PNG path. Default: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_CACHE_DIR,
        help=f"Tile cache directory. Default: {DEFAULT_CACHE_DIR}",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="User-Agent sent to tile.openstreetmap.org.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Delay between new tile downloads in seconds. Default: 0.2.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ズームレベルが大きいほど詳細な地図になりますが、必要なタイル枚数も増えます。
    if not (0 <= args.zoom <= 19):
        raise SystemExit("--zoom must be between 0 and 19.")

    # radiusが負の値だとタイル範囲を作れないので止めます。
    if args.radius < 0:
        raise SystemExit("--radius must be 0 or greater.")

    build_map_image(
        center_lat=args.lat,
        center_lon=args.lon,
        zoom=args.zoom,
        radius=args.radius,
        cache_dir=args.cache_dir,
        output_path=args.output,
        user_agent=args.user_agent,
        delay_seconds=args.delay,
    )


if __name__ == "__main__":
    main()
