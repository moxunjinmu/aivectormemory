"""aivectormemory/settings.py 单元测试"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from aivectormemory.settings import get_language, set_language, DEFAULT_LANG, SUPPORTED_LANGS


@pytest.fixture
def tmp_settings(tmp_path):
    """临时 settings.json 路径"""
    path = tmp_path / "settings.json"
    with patch("aivectormemory.settings.SETTINGS_PATH", path):
        yield path


class TestGetLanguage:
    def test_default_when_file_missing(self, tmp_settings):
        assert get_language() == DEFAULT_LANG

    def test_reads_valid_language(self, tmp_settings):
        tmp_settings.write_text(json.dumps({"language": "en"}), encoding="utf-8")
        assert get_language() == "en"

    def test_default_when_invalid_language(self, tmp_settings):
        tmp_settings.write_text(json.dumps({"language": "invalid"}), encoding="utf-8")
        assert get_language() == DEFAULT_LANG

    def test_default_when_empty_language(self, tmp_settings):
        tmp_settings.write_text(json.dumps({"language": ""}), encoding="utf-8")
        assert get_language() == DEFAULT_LANG

    def test_default_when_no_language_key(self, tmp_settings):
        tmp_settings.write_text(json.dumps({"other": "value"}), encoding="utf-8")
        assert get_language() == DEFAULT_LANG

    def test_default_when_invalid_json(self, tmp_settings):
        tmp_settings.write_text("not json", encoding="utf-8")
        assert get_language() == DEFAULT_LANG

    def test_all_supported_langs(self, tmp_settings):
        for lang in SUPPORTED_LANGS:
            tmp_settings.write_text(json.dumps({"language": lang}), encoding="utf-8")
            assert get_language() == lang


class TestSetLanguage:
    def test_creates_file(self, tmp_settings):
        set_language("en")
        data = json.loads(tmp_settings.read_text("utf-8"))
        assert data["language"] == "en"

    def test_preserves_other_fields(self, tmp_settings):
        tmp_settings.write_text(json.dumps({"language": "zh-CN", "other": 42}), encoding="utf-8")
        set_language("ja")
        data = json.loads(tmp_settings.read_text("utf-8"))
        assert data["language"] == "ja"
        assert data["other"] == 42

    def test_rejects_unsupported_language(self, tmp_settings):
        with pytest.raises(ValueError, match="Unsupported language"):
            set_language("invalid")

    def test_overwrites_existing_language(self, tmp_settings):
        set_language("en")
        set_language("fr")
        data = json.loads(tmp_settings.read_text("utf-8"))
        assert data["language"] == "fr"

    def test_creates_parent_directory(self, tmp_path):
        path = tmp_path / "subdir" / "settings.json"
        with patch("aivectormemory.settings.SETTINGS_PATH", path):
            set_language("de")
            assert path.exists()
            data = json.loads(path.read_text("utf-8"))
            assert data["language"] == "de"
