"""aivectormemory/i18n 模块单元测试"""
import pytest
from unittest.mock import patch

from aivectormemory.i18n import get_steering, get_workflow_prompt, LANG_MODULE_MAP, _load_module
from aivectormemory.settings import SUPPORTED_LANGS


class TestLangModuleMap:
    def test_all_supported_langs_have_mapping(self):
        for lang in SUPPORTED_LANGS:
            assert lang in LANG_MODULE_MAP, f"{lang} missing from LANG_MODULE_MAP"


class TestLoadModule:
    @pytest.mark.parametrize("lang", list(SUPPORTED_LANGS))
    def test_load_all_languages(self, lang):
        mod = _load_module(lang)
        assert hasattr(mod, "STEERING_CONTENT")
        assert hasattr(mod, "DEV_WORKFLOW_PROMPT")

    def test_fallback_on_unknown_lang(self):
        mod = _load_module("unknown")
        assert hasattr(mod, "STEERING_CONTENT")

    def test_fallback_on_import_error(self):
        with patch.dict(LANG_MODULE_MAP, {"test-broken": "nonexistent_module"}):
            mod = _load_module("test-broken")
            assert hasattr(mod, "STEERING_CONTENT")


class TestGetSteering:
    @pytest.mark.parametrize("lang", list(SUPPORTED_LANGS))
    def test_returns_string_for_all_langs(self, lang):
        result = get_steering(lang)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_zh_cn_contains_chinese(self):
        result = get_steering("zh-CN")
        assert "工作规则" in result or "工作規則" in result

    def test_en_contains_english(self):
        result = get_steering("en")
        assert "Workflow Rules" in result

    def test_default_lang_from_settings(self):
        with patch("aivectormemory.i18n.get_language", return_value="en"):
            result = get_steering()
            assert "Workflow Rules" in result


class TestGetWorkflowPrompt:
    @pytest.mark.parametrize("lang", list(SUPPORTED_LANGS))
    def test_returns_string_for_all_langs(self, lang):
        result = get_workflow_prompt(lang)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_zh_cn_prompt_language_line(self):
        result = get_workflow_prompt("zh-CN")
        assert "中文" in result

    def test_en_prompt_language_line(self):
        result = get_workflow_prompt("en")
        assert "English" in result

    def test_ja_prompt_language_line(self):
        result = get_workflow_prompt("ja")
        assert "日本語" in result

    def test_default_lang_from_settings(self):
        with patch("aivectormemory.i18n.get_language", return_value="ja"):
            result = get_workflow_prompt()
            assert "日本語" in result


class TestContentConsistency:
    """验证所有语言文件结构一致"""

    @pytest.mark.parametrize("lang", list(SUPPORTED_LANGS))
    def test_steering_has_9_sections(self, lang):
        content = get_steering(lang)
        # 所有语言都应该有 ## 1. 到 ## 9. 的章节
        for i in range(1, 10):
            assert f"## {i}." in content, f"Language {lang} missing section {i}"

    @pytest.mark.parametrize("lang", list(SUPPORTED_LANGS))
    def test_workflow_prompt_has_identity_section(self, lang):
        content = get_workflow_prompt(lang)
        assert "IDENTITY" in content
