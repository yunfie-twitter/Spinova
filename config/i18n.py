import json
import os


class I18N:
    def __init__(self, locale="ja", dir_path="langs"):
        self.trans = {}
        self.locale = locale
        self.dir_path = dir_path
        self.language_info = {}
        self.load(locale)

    def load(self, locale):
        path = os.path.join(self.dir_path, f"locale_{locale}.json")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                self.trans = data.get("translations", {})
                self.language_info = data.get("language_info", {})
                self.locale = locale
        except Exception as e:
            print(f"翻訳ファイル読み込み失敗: {e}")
            self.trans = {}
            self.language_info = {}

    def t(self, key):
        return self.trans.get(key, key)

    def get_language_name(self):
        return self.language_info.get("name", "Unknown")

    def get_language_code(self):
        return self.language_info.get("code", "unknown")

    def get_available_locales(self):
        available = []
        if os.path.exists(self.dir_path):
            for file in os.listdir(self.dir_path):
                if file.startswith("locale_") and file.endswith(".json"):
                    locale_code = file[7:-5]  # locale_ja.json -> ja
                    available.append(locale_code)
        return available
