<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '../stores/settings'
import { useThemeStore, type ThemeMode } from '../stores/theme'
import { LANGS } from '../i18n'
import { DetectPython, SetAutoStart, SetLanguage, LaunchWebDashboard, StopWebDashboard, IsWebDashboardRunning } from '../../wailsjs/go/main/App'

const { t, locale } = useI18n()
const settingsStore = useSettingsStore()
const themeStore = useThemeStore()

const settings = computed(() => settingsStore.settings)
const detectedPython = ref('')
const webDashboardRunning = ref(false)

onMounted(async () => {
  try { detectedPython.value = await DetectPython() } catch {}
  try { webDashboardRunning.value = await IsWebDashboardRunning() } catch {}
})

// Theme
function onThemeChange(e: Event) {
  const mode = (e.target as HTMLSelectElement).value as ThemeMode
  themeStore.setMode(mode)
  settingsStore.save({ theme: mode })
}

// Language
function onLangChange(e: Event) {
  const lang = (e.target as HTMLSelectElement).value
  locale.value = lang
  settingsStore.save({ language: lang })
  SetLanguage(lang).catch((err: Error) => console.error('SetLanguage failed:', err))
}

// DB path
function onDBPathChange(e: Event) {
  settingsStore.save({ db_path: (e.target as HTMLInputElement).value })
}

// Python path
function onPythonChange(e: Event) {
  settingsStore.save({ python_path: (e.target as HTMLInputElement).value })
}

// Web port
function onPortChange(e: Event) {
  settingsStore.save({ web_port: parseInt((e.target as HTMLInputElement).value) || 9080 })
}

// Auto start
async function onAutoStartChange(e: Event) {
  const checked = (e.target as HTMLInputElement).checked
  try {
    await SetAutoStart(checked)
    settingsStore.save({ auto_start: checked })
  } catch (err: any) {
    window.__toast?.show(err?.message || 'Failed', 'error')
  }
}

// Web dashboard
async function toggleWebDashboard() {
  try {
    if (webDashboardRunning.value) {
      await StopWebDashboard()
      webDashboardRunning.value = false
      window.__toast?.show(t('webDashboardStopped'), 'success')
    } else {
      await LaunchWebDashboard()
      webDashboardRunning.value = true
      window.__toast?.show(t('webDashboardRunning'), 'success')
    }
  } catch (e: any) {
    window.__toast?.show(e?.message || 'Failed', 'error')
  }
}
</script>

<template>
  <div class="settings-view">
    <div class="page-header">
      <h2 class="page-title">{{ t('settings') }}</h2>
    </div>

    <!-- Appearance -->
    <section class="settings-section">
      <h3 class="settings-section__title">{{ t('appearance') }}</h3>
      <div class="settings-row">
        <label class="settings-label">{{ t('appearance') }}</label>
        <select class="filter-select" :value="settings.theme" @change="onThemeChange">
          <option value="dark">{{ t('themeDark') }}</option>
          <option value="light">{{ t('themeLight') }}</option>
          <option value="system">{{ t('themeSystem') }}</option>
        </select>
      </div>
      <div class="settings-row">
        <label class="settings-label">{{ t('language') }}</label>
        <select class="filter-select" :value="locale" @change="onLangChange">
          <option v-for="(lang, code) in LANGS" :key="code" :value="code">{{ lang.label }}</option>
        </select>
      </div>
    </section>

    <!-- Data -->
    <section class="settings-section">
      <h3 class="settings-section__title">{{ t('dataSettings') }}</h3>
      <div class="settings-row">
        <label class="settings-label">{{ t('dbPath') }}</label>
        <input class="form-input" :value="settings.db_path" @change="onDBPathChange" placeholder="~/.aivectormemory/memory.db" />
      </div>
      <div class="settings-row">
        <label class="settings-label">{{ t('pythonPath') }}</label>
        <input class="form-input" :value="settings.python_path" @change="onPythonChange" :placeholder="detectedPython || 'python3'" />
        <span v-if="detectedPython && !settings.python_path" class="settings-hint">{{ t('autoDetected') }}: {{ detectedPython }}</span>
      </div>
    </section>

    <!-- Web Dashboard -->
    <section class="settings-section">
      <h3 class="settings-section__title">{{ t('webDashboard') }}</h3>
      <div class="settings-row">
        <label class="settings-label">{{ t('port') }}</label>
        <input class="form-input" type="number" :value="settings.web_port" @change="onPortChange" style="width: 120px" />
      </div>
      <div class="settings-row">
        <label class="settings-label">{{ t('webDashboard') }}</label>
        <button class="btn" :class="webDashboardRunning ? 'btn--danger' : 'btn--primary'" @click="toggleWebDashboard">
          {{ webDashboardRunning ? t('stopWebDashboard') : t('launchWebDashboard') }}
        </button>
      </div>
    </section>

    <!-- System -->
    <section class="settings-section">
      <h3 class="settings-section__title">{{ t('system') }}</h3>
      <div class="settings-row">
        <label class="settings-label">{{ t('autoStart') }}</label>
        <label class="toggle">
          <input type="checkbox" :checked="settings.auto_start" @change="onAutoStartChange" />
          <span class="toggle__slider" />
        </label>
      </div>
    </section>

    <!-- About -->
    <section class="settings-section">
      <h3 class="settings-section__title">{{ t('about') }}</h3>
      <div class="settings-row">
        <label class="settings-label">{{ t('version') }}</label>
        <span class="settings-value">1.0.0</span>
      </div>
      <div class="settings-row">
        <span class="settings-value" style="font-size: 12px; color: var(--text-muted)">
          Wails 2 + Go + Vue 3 + Pinia + vue-i18n
        </span>
      </div>
    </section>
  </div>
</template>

<style scoped>
.settings-view { display: flex; flex-direction: column; flex: 1; max-width: 640px; }
.settings-section { margin-bottom: 28px; }
.settings-section__title {
  font-family: var(--font-mono); font-size: 14px; font-weight: 600; color: var(--text-heading);
  margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--border);
}
.settings-row { display: flex; align-items: center; gap: 16px; margin-bottom: 12px; }
.settings-label { font-size: 13px; color: var(--text-secondary); min-width: 120px; flex-shrink: 0; }
.settings-value { font-size: 14px; color: var(--text-primary); }
.settings-hint { font-size: 11px; color: var(--text-muted); font-family: var(--font-mono); }
.settings-row .form-input { flex: 1; }
.settings-row .filter-select { min-width: 160px; }

/* Toggle switch */
.toggle { position: relative; display: inline-block; width: 44px; height: 24px; }
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle__slider {
  position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
  background: var(--border); border-radius: 12px; transition: 0.3s;
}
.toggle__slider::before {
  content: ''; position: absolute; height: 18px; width: 18px; left: 3px; bottom: 3px;
  background: white; border-radius: 50%; transition: 0.3s;
}
.toggle input:checked + .toggle__slider { background: var(--accent); }
.toggle input:checked + .toggle__slider::before { transform: translateX(20px); }
</style>
