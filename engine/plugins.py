import importlib
import os
import sys
import json


class PluginManager:
    def __init__(self, plugin_dir=None, config_file="plugin_config.json"):
        self.plugin_dir = plugin_dir or self.get_default_plugin_dir()
        self.plugins = {}
        self.plugin_metadata = {}
        self.formats = {}
        self.enabled_plugins = set()
        self.config_file = config_file
        self.load_enabled_plugins()
        self.load_plugins()
        self.load_external_format_files()

    def load_enabled_plugins(self):
        if os.path.isfile(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    enabled = data.get("enabled_plugins", [])
                    if isinstance(enabled, list):
                        self.enabled_plugins = set(enabled)
            except Exception as e:
                print(f"プラグイン設定ファイルの読み込み失敗: {e}")

    def save_enabled_plugins(self):
        data = {
            "enabled_plugins": list(self.enabled_plugins)
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"プラグイン設定ファイルの保存失敗: {e}")

    def get_default_plugin_dir(self):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, "plugins")

    def load_plugins(self):
        if not os.path.isdir(self.plugin_dir):
            print(f"プラグインフォルダが存在しません: {self.plugin_dir}")
            return

        for file in os.listdir(self.plugin_dir):
            if file.endswith(".py") and not file.startswith("_"):
                name = file[:-3]

                try:
                    if self.config.get('enabled_plugins') and name not in self.config['enabled_plugins']:
                        continue
                except Exception as e:
                    print(f"プラグイン設定の参照エラー: {e}")

                try:
                    if self.plugin_dir not in sys.path:
                        sys.path.insert(0, self.plugin_dir)
                    module = importlib.import_module(name)
                except (ModuleNotFoundError, ImportError) as e:
                    print(f"プラグイン読み込み失敗 (インポートエラー) {name}: {e}")
                    continue
                except Exception as e:
                    print(f"プラグイン読み込み失敗 (不明なエラー) {name}: {e}")
                    continue

                self.plugins[name] = module

                try:
                    meta = {
                        "name": getattr(module, "name", name),
                        "version": getattr(module, "version", "unknown"),
                        "description": getattr(module, "description", ""),
                    }
                except Exception as e:
                    print(f"プラグインメタ情報取得失敗 {name}: {e}")
                    meta = {"name": name, "version": "unknown", "description": ""}

                self.plugin_metadata[name] = meta

                try:
                    if hasattr(module, 'initialize'):
                        module.initialize()
                except Exception as e:
                    print(f"プラグイン初期化失敗 {name}: {e}")

                try:
                    if hasattr(module, 'get_formats'):
                        fmts = module.get_formats()
                        if isinstance(fmts, dict):
                            self.formats.update(fmts)
                except Exception as e:
                    print(f"プラグインフォーマット取得失敗 {name}: {e}")

                try:
                    if hasattr(module, 'register'):
                        module.register()
                except Exception as e:
                    print(f"プラグイン登録処理失敗 {name}: {e}")

    def load_external_format_files(self):
        if not os.path.isdir(self.plugin_dir):
            return

        for file in os.listdir(self.plugin_dir):
            if file.startswith("formats_") and file.endswith(".json"):
                path = os.path.join(self.plugin_dir, file)
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            self.formats.update(data)
                except Exception as e:
                    print(f"フォーマットJSON読み込み失敗: {file} - {e}")

    def run_plugin(self, name, **kwargs):
        module = self.plugins.get(name)
        if module and hasattr(module, 'run'):
            module.run(**kwargs)

    def get_all_formats(self):
        default_formats = {
            "best (デフォルト)": "bestvideo+bestaudio/best",
            "音声のみ": "bestaudio/best",
            "動画のみ": "bestvideo/best",
        }
        return {**default_formats, **self.formats}

    def enable_plugin(self, name):
        self.enabled_plugins.add(name)
        self.save_enabled_plugins()

    def disable_plugin(self, name):
        self.enabled_plugins.discard(name)
        self.save_enabled_plugins()
