# TODO

最終更新: 2026-05-28

## 目的

Raspberry Pi 側でサイクルコンピュータ本体、カメラ、GPS、ログ生成を動かし、iOS アプリ側で接続確認、目的地入力、ログ受信、過去走行記録の閲覧をできるようにする。

## 現在の状態

- [x] Raspberry Pi 側に Pygame ベースの全画面表示処理がある
- [x] Raspberry Pi 側に OpenCV を使った後方カメラ表示処理がある
- [x] Raspberry Pi 側に `MockGPS` を使った GPS 風データ表示がある
- [x] Raspberry Pi 側に起動アニメーション用のコードと素材がある
- [x] iOS 側に `cycle_computer_iosAPP` サブプロジェクトがある
- [x] iOS 側は SwiftUI 初期テンプレートの状態
- [x] `.gitignore` に Xcode / Swift 向けの除外設定がある

## 全体方針

- [ ] Raspberry Pi 側を Python アプリ本体と HTTP API サーバーに分ける
- [ ] iOS 側は Raspberry Pi の HTTP API に接続するクライアントとして実装する
- [ ] 初期実装では iPhone から Raspberry Pi に問い合わせる polling 方式でログ受信する
- [ ] USB 接続より先に、同一ネットワーク上の IP 通信で MVP を作る
- [ ] Raspberry Pi 側で生成したログを iOS 側に保存し、未接続時も閲覧できる構成にする

# 技術選定候補

- [ ] Raspberry Pi 側 API サーバー: FastAPI
- [ ] Raspberry Pi 側 API サーバー代替候補: Flask
- [ ] Raspberry Pi 側 ASGI サーバー: uvicorn
- [ ] Raspberry Pi 側画面表示: Pygame
- [ ] Raspberry Pi 側カメラ取得: OpenCV
- [ ] Raspberry Pi 側 GPS 読み取り: pyserial
- [ ] Raspberry Pi 側ログ形式: JSON
- [ ] Raspberry Pi 側ログ形式の補助候補: CSV
- [ ] Raspberry Pi 側ログエクスポート候補: GPX
- [ ] Raspberry Pi 側自動起動: systemd
- [ ] Raspberry Pi と iPhone の通信方式: HTTP polling
- [ ] Raspberry Pi と iPhone のリアルタイム通信候補: WebSocket
- [ ] Raspberry Pi と iPhone の接続方式: 同一 Wi-Fi
- [ ] Raspberry Pi と iPhone の接続方式: iPhone テザリング
- [ ] Raspberry Pi と iPhone の接続方式の後続候補: USB 直接通信
- [ ] Raspberry Pi の名前解決: 固定 IP
- [ ] Raspberry Pi の名前解決: mDNS
- [ ] iOS 側 UI: SwiftUI
- [ ] iOS 側 HTTP 通信: URLSession
- [ ] iOS 側地図表示: MapKit
- [ ] iOS 側ローカルログ保存: Documents ディレクトリ
- [ ] iOS 側ログ一覧メタ情報保存: JSON インデックス
- [ ] iOS 側ローカルデータ管理の後続候補: SwiftData

## Raspberry Pi 側 TODO

- [ ] 現在の `main.py` の責務を整理する
- [ ] 画面表示、カメラ、GPS、ログ、API サーバーをファイル分割する
- [ ] Python API サーバーの候補を決める
- [ ] FastAPI を使う場合は `requirements.txt` に `fastapi` と `uvicorn` を追加する
- [ ] Raspberry Pi 接続確認用の `GET /health` を実装する
- [ ] 目的地受信用の `POST /destination` または `POST /start-navigation` を実装する
- [ ] 目的地データの形式を決める
- [ ] 目的地データに名称、緯度、経度、作成日時を含める
- [ ] 目的地受信時に走行セッションを開始する処理を実装する
- [ ] API 経由で Pygame アプリ本体の状態を更新できる設計にする
- [ ] 走行中、停止中、ログ準備完了などの状態管理を実装する
- [ ] 状態確認用の `GET /status` を実装する
- [ ] 最新ログ取得用の `GET /logs/latest` を実装する
- [ ] ログ一覧取得用の `GET /logs` を実装する
- [ ] 特定ログ取得用の `GET /logs/{id}` を実装する
- [ ] ログファイルの保存先ディレクトリを決める
- [ ] ログファイル形式を決める
- [ ] 最初は JSON または CSV で走行ログを保存する
- [ ] 後で地図表示しやすいように時刻、緯度、経度、速度、方位、高度を保存する
- [ ] ダミーログ生成処理を作り、iOS 側の受信テストに使えるようにする
- [ ] 実 GPS 読み取り用の `gps_reader.py` を作る
- [ ] NEO-6M の NMEA データを読み取る
- [ ] GPS の fix 状態、緯度、経度、速度、方位、高度、衛星数を取得する
- [ ] `MockGPS` と実 GPS を切り替えられる設定を作る
- [ ] 後方カメラ処理を `rear_camera.py` に閉じ込める
- [ ] Linux 環境では `/dev/v4l/by-path/` で USB カメラを固定指定する
- [ ] カメラが開けない場合のエラー表示を画面に出す
- [ ] Raspberry Pi OS 上で Pygame + OpenCV 表示を確認する
- [ ] AR グラスへの HDMI 出力を確認する
- [ ] 起動時に API サーバーと画面表示アプリを自動起動する方法を決める
- [ ] systemd で自動起動する unit ファイルを用意する
- [ ] iPhone のテザリング、Raspberry Pi AP、同一 Wi-Fi のどれを標準接続方式にするか決める
- [ ] Raspberry Pi の IP アドレス固定またはホスト名解決方法を決める
- [ ] mDNS を使う場合は `raspberrypi.local` などで接続できるか確認する
- [ ] API のタイムアウト、接続失敗、再接続の挙動を決める
- [ ] 実走行用に電源、防水、防振、発熱対策を確認する

## iOS 側 TODO

- [ ] SwiftUI の初期画面をアプリ用の画面構成に置き換える
- [ ] 接続状態表示、目的地入力、走行状態、ログ一覧の画面を用意する
- [ ] Raspberry Pi の接続先 IP またはホスト名を保存できる設定画面を作る
- [ ] アプリ起動時に `GET /health` で Raspberry Pi との接続確認を行う
- [ ] 接続成功、接続失敗、確認中の UI 状態を実装する
- [ ] 接続失敗時でも過去ログ一覧を表示できるようにする
- [ ] Raspberry Pi API 用の Swift クライアントを作る
- [ ] API クライアントでタイムアウト、リトライ、エラー表示を扱う
- [ ] 目的地入力フォームを作る
- [ ] 目的地に名称、緯度、経度を入力または選択できるようにする
- [ ] 最初は手入力で目的地を送信できるようにする
- [ ] 後で MapKit 検索から目的地を選べるようにする
- [ ] 目的地送信用に `POST /destination` または `POST /start-navigation` を呼び出す
- [ ] 目的地送信後に Raspberry Pi 側の走行状態を表示する
- [ ] `GET /status` を定期実行してログ準備状態を確認する
- [ ] ログ準備完了時に `GET /logs/latest` でログをダウンロードする
- [ ] ダウンロードしたログを iPhone 内の Documents ディレクトリに保存する
- [ ] ログ一覧表示用のメタ情報を保存する
- [ ] 保存方式として SwiftData、CoreData、SQLite、JSON インデックスのどれを使うか決める
- [ ] 最初は JSON インデックスまたは SwiftData で実装する
- [ ] 保存済みログ一覧画面を作る
- [ ] ログ詳細画面を作る
- [ ] ログ詳細で走行日時、距離、平均速度、最高速度を表示する
- [ ] ログに位置情報がある場合は MapKit で走行ルートを表示する
- [ ] 未接続時でも保存済みログを開けることを確認する
- [ ] iOS Simulator で API 通信をテストする
- [ ] 実機 iPhone で同一ネットワーク上の Raspberry Pi に接続できるか確認する
- [ ] HTTP 通信を使う場合の App Transport Security 設定を確認する
- [ ] ローカルネットワークアクセス権限の説明文を `Info.plist` に追加する
- [ ] バックグラウンド中のログ受信を必要とするか判断する
- [ ] まずはアプリが前面にある間だけログ取得する仕様にする

## 通信 API TODO

- [ ] API のベース URL を決める
- [ ] Raspberry Pi 側の標準ポートを決める
- [ ] `GET /health` のレスポンス形式を決める
- [ ] `POST /destination` のリクエスト形式を決める
- [ ] `GET /status` のレスポンス形式を決める
- [ ] `GET /logs/latest` のレスポンス形式を決める
- [ ] ログファイルの MIME type を決める
- [ ] API エラー時の JSON 形式を決める
- [ ] iOS 側と Raspberry Pi 側で共有する API 仕様メモを作る
- [ ] 最低限の疎通確認用 curl コマンドを README または TODO に記録する

## MVP 実装順

- [ ] Raspberry Pi 側に `GET /health` を作る
- [ ] iOS 側から `GET /health` を呼び、接続状態を表示する
- [ ] Raspberry Pi 側に `POST /destination` を作る
- [ ] iOS 側から目的地 JSON を送信する
- [ ] Raspberry Pi 側で目的地受信時にダミーログを生成する
- [ ] Raspberry Pi 側に `GET /status` と `GET /logs/latest` を作る
- [ ] iOS 側でログ準備完了を検知してログを保存する
- [ ] iOS 側で保存済みログ一覧を表示する
- [ ] iOS 側でログ詳細を表示する
- [ ] Raspberry Pi 実機と iPhone 実機で一連の流れを確認する

## 後回し

- [ ] WebSocket によるリアルタイム通知
- [ ] iOS 側を受信サーバーにする構成
- [ ] USB 経由の直接通信
- [ ] MapKit による目的地検索
- [ ] オフライン地図の `.mbtiles` 対応
- [ ] ケイデンスセンサー連携
- [ ] ホイール回転センサー連携
- [ ] BLE センサー連携
- [ ] 走行ログの GPX エクスポート
- [ ] iCloud 同期
