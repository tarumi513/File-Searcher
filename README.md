# STLデータ検索

NAS上のSTLデータを、ファイル名の情報（納期・材料・シェード・医院番号・通し番号・部位）で検索するツール。

## メイン: `index.html`（サーバー不要）
Chrome / Edge で開き、製作日フォルダをドラッグ＆ドロップして使用。データは外部送信されない。

ファイル名規則: `納期_材料_シェード_医院番号(5桁)_通し番号(3桁)_部位.stl`
例: `20261025_Zir_A2_12345_001_16-17.stl`

## 参考: Streamlit版（サーバーが使える場合）
`app.py` / `scanner.py` / `start.bat`。`pip install -r requirements.txt` 後に `streamlit run app.py`。
