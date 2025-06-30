# COM Commander

COM Commanderは、シリアルポート（COMポート）通信のためのGUIアプリケーションです。
`customtkinter`を使用したモダンなUIで、送受信データを直感的に監視、操作することができます。

## 主な機能

- **シリアル接続管理:**
  - 利用可能なCOMポートの自動検出と選択
  - ボーレート、バイトサイズ、パリティ、ストップビットの詳細な設定
  - 接続・切断のワンクリック操作

- **データ表示:**
  - 送信（TX）と受信（RX）データをタイムスタンプ付きでリアルタイムに表示
  - 見やすいバブル形式のUI
  - 表示形式をASCII, HEX, BINから動的に切り替え可能
  - 自動スクロール機能のON/OFF

- **データ送信:**
  - 送信するデータのエンコード形式をASCII, HEX, BINから選択可能

- **ログフィルタリング:**
  - 指定した時間範囲（開始時刻・終了時刻）でログをフィルタリング表示

## 動作環境

- Python 3.x

## インストール方法

1. **リポジトリをクローンします。**
   ```bash
   git clone https://github.com/USERNAME/COMCommander.git
   cd COMCommander
   ```

2. **必要なライブラリをインストールします。**
   ```bash
   pip install -r requirements.txt
   ```

## 使い方

以下のコマンドでアプリケーションを起動します。

```bash
python main.py
```


## 依存ライブラリ

- [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
- [pyserial](https://github.com/pyserial/pyserial)


