🌐 [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [English](../README.md) | Español | [Deutsch](README.de.md) | [Français](README.fr.md) | [日本語](README.ja.md)

<p align="center">
  <img src="logo.png" alt="AIVectorMemory Logo" width="200">
</p>
<h1 align="center">AIVectorMemory</h1>
<p align="center">
  <strong>Dale memoria a tu asistente de IA — Servidor MCP de memoria persistente entre sesiones</strong>
</p>
<p align="center">
  <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
  <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-green" alt="License"></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
</p>
---

> **¿Sigues usando CLAUDE.md / MEMORY.md como memoria?** Este enfoque de memoria basado en archivos Markdown tiene defectos fatales: el archivo crece sin parar, inyectando todo en cada sesión y consumiendo una enorme cantidad de tokens; el contenido solo permite búsqueda por palabras clave — buscar "timeout de base de datos" no encuentra "error en pool de conexiones MySQL"; compartir un archivo entre proyectos causa contaminación cruzada; no hay seguimiento de tareas, así que el progreso del desarrollo depende solo de tu cabeza; sin mencionar el truncamiento a 200 líneas, el mantenimiento manual y la imposibilidad de deduplicar o fusionar.
>
> **AIVectorMemory es un enfoque completamente diferente.** Almacenamiento en base de datos vectorial local con búsqueda semántica para recuperación precisa (coincide aunque las palabras sean diferentes), recuperación bajo demanda que solo carga memorias relevantes (consumo de tokens baja un 50%+), aislamiento multi-proyecto automático sin interferencia, y seguimiento de problemas + gestión de tareas integrado que permite a la IA automatizar completamente tu flujo de desarrollo. Todos los datos se guardan permanentemente en tu máquina — cero dependencia de la nube, nunca se pierden al cambiar de sesión o de IDE.

## ✨ Características Principales

| Característica | Descripción |
|----------------|-------------|
| 🧠 **Memoria Entre Sesiones** | Tu IA por fin recuerda tu proyecto — errores encontrados, decisiones tomadas, convenciones establecidas, todo persiste entre sesiones |
| 🔍 **Búsqueda Híbrida Inteligente** | FTS5 texto completo + búsqueda semántica vectorial dual, ranking fusionado RRF + puntuación compuesta (recencia × frecuencia × importancia), mucho más precisa que la búsqueda vectorial pura |
| 🐛 **Seguimiento de Problemas** | Issue Tracker integrado — descubrir → investigar → corregir → archivar ciclo completo. La IA gestiona el ciclo de vida de bugs automáticamente |
| 📋 **Gestión de Tareas** | Spec → desglose de tareas → subtareas anidadas → sincronización de estados → archivado vinculado. La IA dirige el flujo de desarrollo completo |
| 🚦 **Estado de Sesión** | Gestión de bloqueos + reanudación desde punto de interrupción + seguimiento de progreso, transición fluida entre sesiones y compresión de contexto |
| 🪝 **Hooks + Steering** | Inyección automática de reglas de trabajo + hooks de guardia de comportamiento, comportamiento consistente de la IA garantizado — sin repetir instrucciones |
| 🧬 **Evolución de Memoria** | Detección de contradicciones reemplaza conocimiento obsoleto + promoción automática corto→largo plazo + archivo automático a 90 días, memoria auto-evolutiva |
| 📊 **App Escritorio + Panel Web** | App de escritorio nativa (macOS/Windows/Linux) + panel Web, red vectorial 3D para ver conexiones de conocimiento de un vistazo |
| 💰 **Ahorro 50%+ Tokens** | Recuperación semántica bajo demanda, adiós a copiar y pegar el contexto del proyecto en cada conversación |
| 🏠 **Completamente Local** | Cero dependencia de la nube. Inferencia local ONNX, sin API Key, los datos nunca salen de tu máquina |
| 🔌 **11 IDEs Cubiertos** | Cursor / Kiro / Claude Code / Windsurf / VSCode / Copilot / OpenCode / Trae / Codex / Antigravity / OpenClaw — instalación y desinstalación con un clic |
| 📁 **Aislamiento Multi-Proyecto** | Una sola BD para todos los proyectos, aislamiento automático sin interferencia, cambio de proyecto transparente |
| 🔄 **Deduplicación Inteligente** | Similitud > 0.95 fusiona automáticamente, la base de memorias siempre limpia — nunca se desordena con el uso |
| 🌐 **7 Idiomas** | 简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語, i18n completa para panel + reglas Steering |

<p align="center">
  QQ群：1085682431 &nbsp;|&nbsp; 微信：changhuibiz<br>
  共同参与项目开发加QQ群或微信交流
</p>

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────┐
│                   AI IDE                         │
│  OpenCode / Codex / Claude Code / Cursor / ...  │
└──────────────────────┬──────────────────────────┘
                       │ MCP Protocol (stdio)
┌──────────────────────▼──────────────────────────┐
│              AIVectorMemory Server               │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ remember │ │  recall   │ │   auto_save      │ │
│  │ forget   │ │  task     │ │   status/track   │ │
│  └────┬─────┘ └────┬─────┘ └───────┬──────────┘ │
│       │            │               │             │
│  ┌────▼────────────▼───────────────▼──────────┐  │
│  │         Embedding Engine (ONNX)            │  │
│  │      intfloat/multilingual-e5-small        │  │
│  └────────────────────┬───────────────────────┘  │
│                       │                          │
│  ┌────────────────────▼───────────────────────┐  │
│  │     SQLite + sqlite-vec (Índice Vectorial) │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 Inicio Rápido

### Opción 1: Instalación con pip (Recomendado)

```bash
# Instalar
pip install aivectormemory

# Actualizar a la última versión
pip install --upgrade aivectormemory

# Ir al directorio de tu proyecto, configuración IDE con un clic
cd /path/to/your/project
run install
```

`run install` te guía interactivamente para seleccionar tu IDE, generando automáticamente la configuración MCP, reglas Steering y Hooks — sin configuración manual.

> **Usuarios de macOS**:
> - Si aparece el error `externally-managed-environment`, agrega `--break-system-packages`
> - Si aparece el error `enable_load_extension`, tu Python no soporta la carga de extensiones SQLite (el Python integrado de macOS y los instaladores de python.org no lo soportan). Usa Homebrew Python:
>   ```bash
>   brew install python
>   /opt/homebrew/bin/python3 -m pip install aivectormemory
>   ```

### Opción 2: uvx (sin instalación)

No necesitas `pip install`, ejecuta directamente:

```bash
cd /path/to/your/project
uvx aivectormemory install
```

> Requiere tener [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado. `uvx` descarga y ejecuta el paquete automáticamente.

### Opción 3: Configuración manual

```json
{
  "mcpServers": {
    "aivectormemory": {
      "command": "run",
      "args": ["--project-dir", "/path/to/your/project"]
    }
  }
}
```

<details>
<summary>📍 Ubicación de archivos de configuración por IDE</summary>

| IDE | Ruta de configuración |
|-----|----------------------|
| Kiro | `.kiro/settings/mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Claude Code | `.mcp.json` |
| Windsurf | `.windsurf/mcp.json` |
| VSCode | `.vscode/mcp.json` |
| Trae | `.trae/mcp.json` |
| OpenCode | `opencode.json` |
| Codex | `.codex/config.toml` |

</details>

Para Codex, usa TOML a nivel de proyecto en lugar de JSON:

```toml
[mcp_servers.aivectormemory]
command = "run"
args = ["--project-dir", "/path/to/your/project"]
```

> Codex solo carga `.codex/config.toml` a nivel de proyecto después de marcar el repositorio como trusted project.

## 🛠️ 9 Herramientas MCP

### `remember` — Almacenar memoria

```
content (string, requerido)   Contenido en formato Markdown
tags    (string[], requerido)  Etiquetas, ej. ["error", "python"]
scope   (string)               "project" (por defecto) / "user" (entre proyectos)
```

Similitud > 0.95 actualiza automáticamente la memoria existente, sin duplicados.

### `recall` — Búsqueda semántica

```
query   (string)     Palabras clave de búsqueda semántica
tags    (string[])   Filtro exacto por etiquetas
scope   (string)     "project" / "user" / "all"
top_k   (integer)    Número de resultados, por defecto 5
```

Coincidencia por similitud vectorial — encuentra memorias relacionadas incluso con palabras diferentes.

### `forget` — Eliminar memorias

```
memory_id  (string)     ID individual
memory_ids (string[])   IDs en lote
```

### `status` — Estado de sesión

```
state (object, opcional)   Omitir para leer, pasar para actualizar
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

Mantiene el progreso de trabajo entre sesiones, restaura contexto automáticamente.

### `track` — Seguimiento de problemas

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   Título del problema
issue_id (integer)  ID del problema
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   Contenido de investigación
```

### `task` — Gestión de tareas

```
action     (string, requerido)  "batch_create" / "update" / "list" / "delete" / "archive"
feature_id (string)             Identificador de funcionalidad asociada (requerido para list)
tasks      (array)              Lista de tareas (batch_create, soporta subtareas)
task_id    (integer)            ID de tarea (update)
status     (string)             "pending" / "in_progress" / "completed" / "skipped"
```

Vinculado a documentos spec mediante feature_id. Update sincroniza automáticamente checkboxes de tasks.md y estado de problemas asociados.

### `readme` — Generación de README

```
action   (string)    "generate" (por defecto) / "diff" (comparar diferencias)
lang     (string)    Idioma: en / zh-TW / ja / de / fr / es
sections (string[])  Secciones específicas: header / tools / deps
```

Genera automáticamente contenido README desde TOOL_DEFINITIONS / pyproject.toml, soporte multiidioma.

### `auto_save` — Guardado automático de preferencias

```
preferences  (string[])  Preferencias técnicas expresadas por el usuario (scope=user fijo, entre proyectos)
extra_tags   (string[])  Etiquetas adicionales
```

Extrae y almacena automáticamente las preferencias del usuario al final de cada conversación, deduplicación inteligente.

### `graph` — Grafo de conocimiento de código

```
action       (string, requerido)  "query" / "trace" / "batch" / "add_node" / "add_edge" / "remove" / "refresh"
name         (string)             Nombre de entidad (add_node/query)
entity_type  (string)             Tipo de entidad: function/class/module/api/table/config (add_node/query)
file_path    (string)             Ruta de archivo, conversión automática a ruta relativa (add_node/query/refresh)
source       (string)             Nombre o ID del nodo origen (add_edge)
target       (string)             Nombre o ID del nodo destino (add_edge)
relation     (string)             Tipo de relación: calls/imports/inherits/uses/depends_on/contains (add_edge/trace)
start        (string)             Nombre o ID del nodo inicial (trace)
direction    (string)             Dirección de recorrido: "up" / "down" / "both" (trace)
max_depth    (integer)            Profundidad máxima de recorrido, por defecto 3 (trace)
```

Gestiona cadenas de llamadas de funciones, flujos de datos y relaciones de dependencia. Trace upstream/downstream antes de cambios de código para evaluar alcance del impacto.

## 📊 Panel Web

```bash
run web --port 9080
run web --port 9080 --quiet          # Suprimir logs de solicitudes
run web --port 9080 --quiet --daemon  # Ejecutar en segundo plano (macOS/Linux)
```

Visita `http://localhost:9080` en tu navegador. Usuario predeterminado `admin`, contraseña `admin123` (se puede cambiar en la configuración después del primer inicio de sesión).

- Cambio entre múltiples proyectos, explorar/buscar/editar/eliminar/exportar/importar memorias
- Búsqueda semántica (coincidencia por similitud vectorial)
- Eliminación de datos de proyecto con un clic
- Estado de sesión, seguimiento de problemas
- Gestión de etiquetas (renombrar, fusionar, eliminación por lotes)
- Protección por autenticación Token
- Visualización 3D de red vectorial de memorias
- 🌐 Soporte multilingüe (简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語)

<p align="center">
  <img src="003.png" alt="Inicio de sesión" width="100%">
  <br>
  <em>Inicio de sesión</em>
</p>

<p align="center">
  <img src="dashboard-projects.png" alt="Selección de Proyecto" width="100%">
  <br>
  <em>Selección de Proyecto</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="Resumen y Visualización de Red Vectorial" width="100%">
  <br>
  <em>Resumen y Visualización de Red Vectorial</em>
</p>

<p align="center">
  <img src="20260306234753_6_1635.jpg" alt="Grupo WeChat" width="280">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="8_1635.jpg" alt="Grupo QQ: 1085682431" width="280">
  <br>
  <em>Escanea para WeChat &nbsp;|&nbsp; Escanea para QQ</em>
</p>

## ⚡ Combinación con Reglas Steering

AIVectorMemory es la capa de almacenamiento. Usa reglas Steering para indicar a la IA **cuándo y cómo** llamar estas herramientas.

Ejecutar `run install` genera automáticamente las reglas Steering y la configuración de Hooks, sin necesidad de escribirlas manualmente.

| IDE | Ubicación de Steering | Hooks |
|-----|----------------------|-------|
| Kiro | `.kiro/steering/aivectormemory.md` | `.kiro/hooks/*.hook` |
| Cursor | `.cursor/rules/aivectormemory.md` | `.cursor/hooks.json` |
| Claude Code | `CLAUDE.md` (añadido) | `.claude/settings.json` |
| Windsurf | `.windsurf/rules/aivectormemory.md` | `.windsurf/hooks.json` |
| VSCode | `.github/copilot-instructions.md` (añadido) | `.claude/settings.json` |
| Trae | `.trae/rules/aivectormemory.md` | — |
| OpenCode | `AGENTS.md` (añadido) | `.opencode/plugins/*.js` |
| Codex | `AGENTS.md` (añadido) | — |

<details>
<summary>📋 Ejemplo de Reglas Steering (generado automáticamente)</summary>

```markdown
# AIVectorMemory - Reglas de Flujo de Trabajo

## 1. Inicio de Nueva Sesión (ejecutar en orden)

1. `recall` (tags: ["conocimiento-proyecto"], scope: "project", top_k: 100) cargar conocimiento del proyecto
2. `recall` (tags: ["preference"], scope: "user", top_k: 20) cargar preferencias del usuario
3. `status` (sin parámetro state) leer estado de sesión
4. Bloqueado → reportar y esperar; No bloqueado → entrar al flujo de procesamiento

## 2. Flujo de Procesamiento de Mensajes

- Paso A: `status` leer estado, esperar si bloqueado
- Paso B: Clasificar tipo de mensaje (chat/corrección/preferencia/problema de código)
- Paso C: `track create` registrar problema
- Paso D: Investigar (`recall` buscar errores + revisar código + encontrar causa raíz)
- Paso E: Presentar plan al usuario, establecer bloqueo esperando confirmación
- Paso F: Modificar código (`recall` buscar errores antes de cambios)
- Paso G: Ejecutar pruebas para verificar
- Paso H: Establecer bloqueo esperando verificación del usuario
- Paso I: Usuario confirma → `track archive` + desbloquear

## 3. Reglas de Bloqueo

Debe `status({ is_blocked: true })` al proponer planes o esperar verificación.
Solo desbloquear tras confirmación explícita del usuario. Nunca auto-desbloquear.

## 4-9. Seguimiento de Problemas / Verificación de Código / Gestión Spec/Tareas / Calidad de Memoria / Referencia de Herramientas / Estándares de Desarrollo

(Reglas completas generadas automáticamente por `run install`)
```

</details>

<details>
<summary>🔗 Ejemplo de Configuración de Hooks (solo Kiro, generado automáticamente)</summary>

Guardado automático al finalizar sesión eliminado. Verificación del flujo de desarrollo (`.kiro/hooks/dev-workflow-check.kiro.hook`):

```json
{
  "enabled": true,
  "name": "Verificación del Flujo de Desarrollo",
  "version": "1",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "Principios: verificar antes de actuar, no probar a ciegas, solo marcar como completado después de pasar las pruebas"
  }
}
```

</details>

## 🇨🇳 Usuarios en China

El modelo de Embedding (~200MB) se descarga automáticamente en la primera ejecución. Si es lento:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

O agregar env en la configuración MCP:

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| Runtime | Python >= 3.10 |
| BD Vectorial | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| Tokenizador | HuggingFace Tokenizers |
| Protocolo | Model Context Protocol (MCP) |
| Web | HTTPServer nativo + Vanilla JS |

## 📋 Registro de Cambios

### v2.4.5

**Parche: Restricciones estrictas contra las tendencias predeterminadas de Opus 4.7**

- 🚫 §1 añadido **Prohibición de preguntas de clarificación**: prohibido volver a preguntar "por fases o de una vez / completo o parcial / ¿debo hacer X? / hacer A o B primero" para comandos imperativos; ante ambigüedad, ejecutar el alcance más completo
- 🚫 §1 añadido **Prohibición de informes defensivos**: prohibido usar "mantenido según instrucción / marcado pending / ruta no crítica / sub-pruebas no necesarias / iteración posterior" como excusa para elementos no ejecutados
- 📋 §1 añadido **Formato de Informe**: prohibido formato de tres secciones Phase A/B/C/D + "Estado Final" + "No Hecho (Mantenido según instrucción)"; cuando el usuario dice "hacer todo", ninguna sección "No Hecho/Mantenido" permitida
- 🎯 Causa raíz: contrarrestar las tendencias predeterminadas "informe defensivo", "preguntas de clarificación" y "lista estructurada" de Opus 4.7 en comparación con 4.6
- 🔄 Archivos de reglas en 7 idiomas (STEERING_CONTENT + DEV_WORKFLOW_PROMPT) totalmente sincronizados con las actualizaciones de CLAUDE.md v2.4.5

### v2.4.4

**Parche: Alineación Completa del Flujo A-I de Procesamiento de Mensajes**

- 🧩 CLAUDE.md §4 rutas de la parte B del flujo de procesamiento totalmente expandidas: las 4 ramas (informal/corrección/preferencia/otros) unificadas para terminar en I(confirmación del usuario y archivar), eliminando flujos incompletos "detenerse en F"
- ⚙️ Sección de juicio de tipo de mensaje de inject-workflow-rules.sh totalmente alineada con §4 B: 4 rutas con granularidad consistente
- 🔧 3 conflictos corregidos: granularidad inconsistente (2 vs 4 rutas) / confusión B/E ("solución+bloqueo" mal ubicado) / flujo G/H/I faltante
- 📝 Cláusula de violación unificada: "Proceder a los pasos C/D/E/F sin mostrar el resultado del juicio = violación"
- 🔄 Archivos de reglas en 7 idiomas (STEERING_CONTENT + DEV_WORKFLOW_PROMPT) totalmente sincronizados con las actualizaciones de CLAUDE.md v2.4.4

### v2.4.3

**Parche: Refuerzo de reglas & Visualización del grafo**
- 🧠 §4.B: Estructura obligatoria de dos pasos (entender mensaje → determinar tipo), saltar = violación
- 📋 §8: Revisión + bloqueo integrados en cada paso Spec, saltar = violación
- 🧬 DEV_WORKFLOW_PROMPT: Añadidas reglas graph trace/batch/add_node para investigación y modificación de código
- 📊 Panel del grafo: Escalado dinámico del layout de fuerza, etiquetas de aristas ocultas por defecto (hover para mostrar), detección de colisión de etiquetas de nodos
- 🔧 Eliminada la sección redundante de "Recordatorios de violaciones frecuentes" del DEV_WORKFLOW_PROMPT
- 📝 Unificado §1 Identidad & Tono en los 7 idiomas (sin traducción)

### v2.4.1

**Parche: Sincronización de reglas i18n**
- 🔄 Sincronizados los 7 archivos de reglas de idiomas (STEERING_CONTENT + DEV_WORKFLOW_PROMPT) con las actualizaciones de CLAUDE.md v2.4.0
- 🧬 Añadidas referencias a la herramienta `graph` en todas las reglas steering (trace/batch/add_node/add_edge/remove)
- ✏️ Actualizado el rol de autoridad de "Arquitecto Líder" a "Responsable del Proyecto" en todos los idiomas
- 📝 Añadidas 3 nuevas reglas de violación + 2 nuevos elementos prohibidos en todos los idiomas

### v2.4.0

**Nuevo: Grafo de Conocimiento de Código**
- 🧬 Herramienta `graph` — Gestiona cadenas de llamadas, flujos de datos y dependencias como un grafo de conocimiento estructurado
- 🔍 Acción `trace` — Recorre cadenas de llamadas upstream/downstream desde cualquier entidad, evalúa el alcance del impacto antes de cambios
- 📊 Página de visualización de grafos en el Panel Web — Explora nodos, aristas y relaciones de llamadas
- 🗃️ Migración DB v15 — Nuevas tablas `graph_nodes` y `graph_edges` para almacenamiento de grafos
- 🌐 Los 7 READMEs en distintos idiomas actualizados en sincronía

### v2.3.1

**Mejora: Revisión completa del sistema de reglas + Soporte OpenClaw**
- 🧠 Corregidas 5 llamadas faltantes al sistema de memoria en las reglas IA: recall trampas antes de investigación (Paso D), antes de operaciones peligrosas (§7), antes de redacción Spec (§8), antes de ejecución de subtarea (§8), remember trampas después de corrección (Paso I)
- 🦞 Soporte OpenClaw IDE añadido — 11 IDEs en total (configuración MCP fusionada en ~/.openclaw/openclaw.json, reglas añadidas a AGENTS.md)
- 🎭 Reglas de auto-prueba Playwright reforzadas — requisito de carga ToolSearch deferred tools añadido, solución alternativa con comando `open` prohibida
- 🔧 Funcionalidades v2.2.0–v2.2.6 fusionadas: sistema Hooks (bash_guard + stop_guard + check_track), mejoras del motor de puntuación, optimizaciones recall, eliminación masiva del panel web, modal de eliminación de memoria escritorio
- ⚠️ DEV_WORKFLOW_PROMPT: 2 nuevos recordatorios de violación (verificar trampas antes de modificar código, guardar después de corrección)
- 🌐 7 archivos de reglas lingüísticas sincronizados

### v2.1.1

**Mejora: Actualización del Sistema de Reglas de IA**
- 📋 CLAUDE.md completado: añadido Identidad y Tono (§1), 7 Principios Fundamentales (§3), ejemplos de juicio de tipo de mensaje, secciones expandidas de seguridad IDE y auto-prueba
- ⚠️ Hook añadido Recordatorio de Violaciones Frecuentes: ejemplos ❌ negativos reforzando las 4 reglas más frecuentemente omitidas (auto-prueba, recall, track create, seguridad IDE)
- 🌐 Los 7 archivos de reglas de idiomas actualizados en sincronía (zh-CN/zh-TW/en/ja/es/de/fr)
- 🔢 Secciones de CLAUDE.md renumeradas a §1–§11, referencias cruzadas actualizadas

### v2.1.0

**Nuevo: Motor de Memoria Inteligente + Desinstalación**
- 🧠 Búsqueda de texto completo FTS5 con tokenización china (jieba) — la búsqueda por palabras clave ahora funciona correctamente para contenido CJK
- 🔀 Recuperación híbrida: vector + FTS5 doble vía con fusión RRF (Reciprocal Rank Fusion)
- 📊 Puntuación compuesta: similitud×0,5 + actualidad×0,3 + frecuencia×0,2, ponderada por importancia
- ⚡ Detección de conflictos: memorias similares (0,85–0,95) se marcan automáticamente como reemplazadas, los datos antiguos se desvanecen
- 📦 Niveles de memoria: las memorias de acceso frecuente se promueven automáticamente a long_term y se buscan primero
- 🗑️ Auto-archivo: memorias a corto plazo expiradas (90 días inactivas + baja importancia) se limpian automáticamente
- 🔗 Expansión de relaciones: superposición de etiquetas ≥ 2 crea enlaces relacionados, expansión de 1 salto descubre memorias conectadas
- 📝 Auto-resumen: memorias largas (>500 caracteres) obtienen resúmenes, el modo brief devuelve resúmenes para ahorrar tokens
- 🧹 Limpieza de código: eliminados 15 elementos de código muerto, 7 patrones duplicados refactorizados en utilidades compartidas
- ❌ `run uninstall` — elimina limpiamente todas las configuraciones IDE (MCP, steering, hooks, permisos) preservando los datos de memoria

### v2.0.9

**Mejora: Seguridad y Optimización de Reglas**
- 🔒 Corregidas vulnerabilidades de inyección SQL, inyección de comandos y recorrido de directorios
- 🛡️ Protección de transacciones añadida para integridad de datos (operaciones de archivo, inserción, actualización)
- 🧠 Fórmula de similitud unificada en todas las rutas de búsqueda
- 📏 Reglas de flujo de trabajo AI comprimidas un 38% (219→136 líneas) sin eliminar procesos
- 🧹 Migración v12 limpia automáticamente memorias basura heredadas
- 🌐 Los 7 idiomas sincronizados

### v2.0.8

**Nuevo: Pruebas de Navegador Playwright Integradas**
- 🎭 `run install` ahora configura automáticamente las pruebas de navegador Playwright — la IA puede abrir un navegador real para verificar cambios en el frontend
- 🎭 Usa un navegador de pruebas dedicado (Chrome for Testing) que no interferirá con tus pestañas personales
- 🔑 Configuración de permisos simplificada — sin más popups de permisos para herramientas comunes
- 📏 Reglas de IA actualizadas en los 7 idiomas para imponer el comportamiento correcto de pruebas de navegador

### v2.0.7

**Mejora: Más Soporte de IDEs**
- 🖥️ Soporte añadido para Antigravity y GitHub Copilot IDEs
- 🔑 `run install` configura automáticamente los permisos de herramientas
- 📏 Reglas de auto-prueba de IA simplificadas

### v2.0.6

**Mejora: Inicio Más Rápido**
- ⚡ Carga de memoria optimizada al inicio de sesión — inicio más rápido con menor uso de contexto
- 🔑 Configuración automática de permisos de Claude Code durante la instalación
- 🌐 7 idiomas sincronizados

### v2.0.5

**Mejora: Reglas Simplificadas**
- 📏 Reglas de flujo de trabajo de IA reestructuradas para mayor claridad y menor uso de tokens
- 💾 La IA ahora guarda automáticamente tus preferencias al final de cada sesión
- 🌐 7 idiomas sincronizados

### v2.0.4

**Corrección: Fiabilidad de Herramientas**
- 🔧 Auditoría y corrección integral de todos los parámetros de herramientas MCP

### v2.0.3

**Mejora: Mejor Búsqueda y Seguridad**
- 🔍 La búsqueda de memoria ahora combina coincidencia semántica y por palabras clave para mayor precisión
- 🛡️ Protección contra operaciones entre proyectos añadida

### v2.0.2

**Mejora: Generalización de Reglas & Corrección de Versión del Escritorio**
- 📏 Nueva regla "recall antes de preguntar al usuario" — la IA debe consultar el sistema de memoria antes de preguntar al usuario por información del proyecto (dirección del servidor, contraseñas, configuración de despliegue, etc.)
- 📏 Regla de verificación pre-operación generalizada — se eliminaron ejemplos específicos para aplicar a todos los escenarios
- 🖥️ Corregida la página de configuración del escritorio que mostraba versión "1.0.0" codificada en vez de la versión real
- 🌐 Reglas de dirección y prompts de flujo de trabajo sincronizados en los 7 idiomas

### v2.0.1

**Corrección: Compatibilidad de Hooks entre proyectos**
- 🔧 `check_track.sh` ahora deriva la ruta del proyecto desde la ubicación del script en vez de `$(pwd)`, corrigiendo fallos de detección de track cuando Claude Code ejecuta hooks desde un directorio diferente
- 🔧 `compact-recovery.sh` ahora usa derivación de ruta relativa en vez de rutas absolutas codificadas
- 🔧 Eliminada la reinyección redundante de CLAUDE.md en compact-recovery (ya se carga automáticamente)
- 🔧 Plantilla de `install.py` sincronizada con todas las correcciones de hooks
- 🌐 Textos de compact-recovery actualizados en los 7 idiomas

### v2.0

**Rendimiento: Cuantización ONNX INT8**
- ⚡ El modelo de embedding se cuantiza automáticamente de FP32 a INT8 en la primera carga, archivo del modelo de 448MB a 113MB
- ⚡ Uso de memoria del MCP Server reducido de ~1,6GB a ~768MB (reducción superior al 50%)
- ⚡ La cuantización es transparente para el usuario — automática en el primer uso, en caché para cargas posteriores, retroceso a FP32 en caso de fallo

**Nuevo: Recordar contraseña**
- 🔐 La página de inicio de sesión en escritorio y panel web ahora tiene un checkbox "Recordar contraseña"
- 🔐 Al activar, las credenciales se guardan en localStorage y se rellenan automáticamente en el próximo inicio de sesión; al desactivar, se eliminan las credenciales guardadas
- 🔐 El checkbox se oculta en modo de registro

**Mejora: Reglas Steering**
- 📝 Sección IDENTITY & TONE fortalecida con restricciones más específicas (sin cortesías, sin traducir mensajes del usuario, etc.)
- 📝 Requisitos de autotest ahora distinguen entre backend puro, MCP Server y cambios visibles en frontend (Playwright requerido para frontend)
- 📝 Reglas de desarrollo ahora exigen autotest después de completar el desarrollo
- 📝 Las 7 versiones de idiomas sincronizadas

### v1.0.11

- 🐛 Comparación de versión del escritorio cambiada a versionado semántico, corrigiendo falsas alertas de actualización cuando la versión local es superior
- 🐛 Nombres de campos de la página de verificación de salud alineados con el backend, corrigiendo el estado de consistencia que siempre mostraba Mismatch
- 🔧 Hook check_track.sh con fallback de Python añadido, resolviendo fallo silencioso del hook sin sqlite3 del sistema (#4)

### v1.0.10

- 🖥️ Instalación con un clic de la app de escritorio + detección de actualización
- 🖥️ Detección automática del estado de instalación de Python y aivectormemory al iniciar
- 🖥️ Botón de instalación con un clic si no está instalado, detección de nuevas versiones de PyPI y escritorio si está instalado
- 🐛 Detección de instalación cambiada a importlib.metadata.version() para versión precisa del paquete

### v1.0.3

**Optimización de búsqueda recall**
- 🔍 `recall` añade parámetro `tags_mode`: `any` (coincidencia OR) / `all` (coincidencia AND)
- 🔍 `query + tags` usa OR por defecto (cualquier etiqueta coincidente entra en candidatos), resolviendo resultados perdidos con múltiples etiquetas
- 🔍 Solo `tags` mantiene AND (navegación precisa por categoría), compatible con versiones anteriores
- 📝 Reglas de Steering actualizadas con directrices de búsqueda

### v0.2.8

**Panel Web**
- 📋 Modal de detalle de problemas archivados: clic en tarjeta archivada muestra detalles de solo lectura (todos los campos estructurados: investigación/causa raíz/solución/resultado de prueba/archivos modificados), botón rojo de eliminación en la parte inferior para eliminación permanente

**Refuerzo de Reglas Steering**
- 📝 `track create` ahora requiere campo `content` obligatorio (describir síntomas y contexto del problema), prohibido enviar solo título
- 📝 `track update` post-investigación requiere campos `investigation` y `root_cause`
- 📝 `track update` post-corrección requiere campos `solution`, `files_changed` y `test_result`
- 📝 Sección 4 añade subsección "Normas de Llenado de Campos" con campos obligatorios por etapa
- 📝 Sección 5 expandida de "Verificación de Modificación de Código" a "Verificación Pre-Operación", añade regla de recall de registros de errores antes de inicio de panel/publicación PyPI/reinicio de servicio
- 📝 `install.py` STEERING_CONTENT sincronizado con todos los cambios

**Optimización de Herramientas**
- 🔧 Descripción del campo `content` de la herramienta `track` cambiada de "contenido de investigación" a "descripción del problema (obligatorio en create)"

### v0.2.7

**Extracción automática de palabras clave**
- 🔑 `remember`/`auto_save` extraen automáticamente palabras clave del contenido y las añaden a los tags — la IA ya no necesita pasar tags completos manualmente
- 🔑 Utiliza segmentación de palabras china jieba + extracción por regex en inglés, extrayendo con precisión palabras clave de alta calidad en contenido mixto chino-inglés
- 🔑 Nueva dependencia `jieba>=0.42`

### v0.2.6

**Reestructuración de reglas Steering**
- 📝 Documento de reglas Steering reescrito de estructura de 3 secciones a 9 secciones (Inicio de sesión / Flujo de procesamiento / Reglas de bloqueo / Seguimiento de problemas / Revisión de código / Gestión de tareas Spec / Calidad de memoria / Referencia de herramientas / Estándares de desarrollo)
- 📝 Plantilla STEERING_CONTENT de `install.py` sincronizada, nuevos proyectos obtienen reglas actualizadas al instalar
- 📝 Tags cambiados de listas fijas a extracción dinámica (palabras clave extraídas del contenido), mejorando la precisión de búsqueda de memoria

**Corrección de errores**
- 🐛 Herramienta `readme` `handle_readme()` faltaba `**_`, causando error MCP `unexpected keyword argument 'engine'`
- 🐛 Corrección de paginación de búsqueda de memoria en panel web (filtrado completo antes de paginar con consulta de búsqueda, corrigiendo resultados incompletos)

**Actualizaciones de documentación**
- 📖 Cantidad de herramientas README 7→8, diagrama de arquitectura `digest`→`task`, añadidas descripciones de herramientas `task`/`readme`
- 📖 Parámetros de `auto_save` actualizados de `decisions[]/modifications[]/pitfalls[]/todos[]` a `preferences[]/extra_tags[]`
- 📖 Ejemplo de reglas Steering actualizado de formato de 3 secciones a resumen de 9 secciones
- 📖 Actualizaciones sincronizadas en 6 versiones de idiomas

### v0.2.5

**Modo de desarrollo dirigido por tareas**
- 🔗 El seguimiento de problemas (track) y la gestión de tareas (task) se conectan mediante `feature_id` en un flujo completo: descubrir problema → crear tarea → ejecutar → sincronización automática de estados → archivado vinculado
- 🔄 `task update` sincroniza automáticamente el estado del problema asociado al actualizar (todo completado→completed, en progreso→in_progress)
- 📦 `track archive` archiva automáticamente las tareas asociadas (vinculación al archivar el último problema activo)
- 📦 Nueva acción `archive` para la herramienta `task`, mueve todas las tareas del grupo funcional a la tabla de archivo `tasks_archive`
- 📊 Las tarjetas de problemas muestran el progreso de tareas asociadas (ej. `5/10`), la página de tareas soporta filtrado por archivos

**Nuevas herramientas**
- 🆕 Herramienta `task` — gestión de tareas (batch_create/update/list/delete/archive), subtareas en árbol, vinculada a documentos spec mediante feature_id
- 🆕 Herramienta `readme` — generación automática de contenido README desde TOOL_DEFINITIONS/pyproject.toml, multiidioma y comparación de diferencias

**Mejoras de herramientas**
- 🔧 `track`: nueva acción delete, 9 campos estructurados (description/investigation/root_cause/solution/test_result/notes/files_changed/feature_id/parent_id), list por issue_id para consulta individual
- 🔧 `recall`: nuevo parámetro source (manual/auto_save) y modo brief (retorna solo content+tags, ahorra contexto)
- 🔧 `auto_save`: marca memorias con source="auto_save", distingue memorias manuales de guardados automáticos

**Refactorización por separación de tablas de conocimiento**
- 🗃️ project_memories + user_memories como tablas independientes, elimina consultas mixtas scope/filter_dir, mejora de rendimiento
- 📊 DB Schema v4→v6: issues añaden 9 campos estructurados + tablas tasks/tasks_archive + campo memories.source

**Panel Web**
- 📊 Página principal con tarjeta de estado de bloqueo (rojo bloqueado/verde normal), clic para ir a la página de estado de sesión
- 📊 Nueva página de gestión de tareas (grupos funcionales plegables, filtrado por estado, búsqueda, CRUD)
- 📊 Navegación lateral optimizada (estado de sesión, problemas, tareas movidos a posición central)
- 📊 Lista de memorias con filtrado source y filtro de exclusión exclude_tags

**Estabilidad y normas**
- 🛡️ Bucle principal del servidor con captura global de excepciones, errores de mensaje individual ya no causan la caída del servidor
- 🛡️ Capa Protocol con salto de líneas vacías y tolerancia a errores de parsing JSON
- 🕐 Marcas de tiempo cambiadas de UTC a zona horaria local
- 🧹 Limpieza de código redundante (métodos no llamados, importaciones redundantes, archivos de respaldo)
- 📝 Plantilla Steering con sección de flujo Spec y gestión de tareas, reglas de continuación context transfer

### v0.2.4

- 🔇 Prompt del hook Stop cambiado a instrucción directa, eliminando respuestas duplicadas de Claude Code
- 🛡️ Reglas de Steering auto_save con protección de cortocircuito, omite otras reglas al finalizar sesión
- 🐛 Corrección de idempotencia de `_copy_check_track_script` (devolver estado de cambio para evitar falsos "sincronizado")
- 🐛 Corrección de incompatibilidad `row.get()` en issue_repo delete con `sqlite3.Row` (usar `row.keys()`)
- 🐛 Corrección de scroll en página de selección de proyectos del panel Web (no se podía desplazar con muchos proyectos)
- 🐛 Corrección de contaminación CSS del panel Web (strReplace reemplazo global corrompió 6 selectores de estilo)
- 🔄 Todos los diálogos confirm() del panel Web reemplazados por modal showConfirm personalizado (eliminar memoria/issue/etiqueta/proyecto)
- 🔄 Operaciones de eliminación del panel Web con manejo de respuesta de error API (toast en lugar de alert)
- 🧹 `.gitignore` añade regla de ignorar directorio legacy `.devmemory/`
- 🧪 Limpieza automática de residuos de proyectos temporales pytest en DB (conftest.py session fixture)

### v0.2.3

- 🛡️ Hook PreToolUse: verificación obligatoria de track issue antes de Edit/Write, rechazo si no hay issues activos (Claude Code / Kiro / OpenCode)
- 🔌 Plugin de OpenCode actualizado al formato SDK `@opencode-ai/plugin` (hook tool.execute.before)
- 🔧 `run install` despliega automáticamente check_track.sh con inyección dinámica de ruta
- 🐛 Corrección de incompatibilidad `row.get()` con `sqlite3.Row` en issue_repo archive/delete
- 🐛 Corrección de condición de carrera de session_id: lectura del último valor desde DB antes de incrementar
- 🐛 Validación de formato de fecha de track (YYYY-MM-DD) + validación de tipo issue_id
- 🐛 Refuerzo del análisis de solicitudes Web API (validación Content-Length + límite 10MB + manejo de errores JSON)
- 🐛 Corrección de lógica scope del filtro de tags (`filter_dir is not None` en lugar de verificación falsy)
- 🐛 Validación de longitud de bytes struct.unpack para exportación de datos vectoriales
- 🐛 Migración versionada del esquema (tabla schema_version + migración incremental v1/v2/v3)
- 🐛 Corrección de sincronización del número de versión `__init__.py`

### v0.2.2

- 🔇 Panel Web: parámetro `--quiet` para suprimir logs de solicitudes
- 🔄 Panel Web: parámetro `--daemon` para ejecución en segundo plano (macOS/Linux)
- 🔧 Corrección de generación de configuración MCP en `run install` (sys.executable + campos completos)
- 📋 Seguimiento de problemas CRUD y archivo (Panel Web agregar/editar/archivar/eliminar + asociación de memorias)
- 👆 Clic en cualquier parte de la fila para abrir modal de edición (memorias/problemas/etiquetas)
- 🔒 Reglas de bloqueo aplicadas en continuaciones de sesión/transferencias de contexto (requiere reconfirmación)

### v0.2.1

- ➕ Agregar proyectos desde el panel Web (explorador de directorios + entrada manual)
- 🏷️ Corrección de contaminación de etiquetas entre proyectos (operaciones limitadas al proyecto actual + memorias globales)
- 📐 Truncamiento con puntos suspensivos en paginación de modales + ancho 80%
- 🔌 OpenCode install genera automáticamente plugin auto_save (evento session.idle)
- 🔗 Claude Code / Cursor / Windsurf install genera automáticamente configuración de Hooks (guardado automático al finalizar sesión)
- 🎯 Mejoras de UX del panel Web (retroalimentación Toast, guías de estado vacío, barra de exportar/importar)
- 🔧 Clic en tarjetas de estadísticas (clic en conteos de memoria/problemas para ver detalles)
- 🏷️ Página de gestión de etiquetas distingue origen proyecto/global (marcadores 📁/🌐)
- 🏷️ Conteo de etiquetas en tarjetas de proyecto incluye etiquetas de memorias globales

### v0.2.0

- 🔐 Autenticación por Token en el panel Web
- ⚡ Caché de vectores Embedding, sin cálculo redundante para contenido idéntico
- 🔍 recall soporta búsqueda combinada query + tags
- 🗑️ forget soporta eliminación por lotes (parámetro memory_ids)
- 📤 Exportación/importación de memorias (formato JSON)
- 🔎 Búsqueda semántica en el panel Web
- 🗂️ Botón de eliminación de proyecto en el panel Web
- 📊 Optimización de rendimiento del panel Web (eliminación de escaneos completos de tabla)
- 🧠 Compresión inteligente de digest
- 💾 Persistencia de session_id
- 📏 Protección de límite de longitud de content
- 🏷️ Referencia dinámica de version (ya no codificada)

### v0.1.x

- Versión inicial: 7 herramientas MCP, panel Web, visualización 3D vectorial, soporte multilingüe

## License

Apache-2.0
