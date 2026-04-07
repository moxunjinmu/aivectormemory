🌐 [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [English](../README.md) | [Español](README.es.md) | [Deutsch](README.de.md) | Français | [日本語](README.ja.md)

<p align="center">
  <img src="logo.png" alt="AIVectorMemory Logo" width="200">
</p>
<h1 align="center">AIVectorMemory</h1>
<p align="center">
  <strong>Plus qu'une mémoire — Mémoire + Suivi de problèmes + Gestion de tâches, un moteur de workflow de développement IA tout-en-un</strong>
</p>
<p align="center">
  <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
  <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-green" alt="License"></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
</p>
---

> **Les autres outils de mémoire IA (mem0, Cline Memory Bank, etc.) ne font qu'une seule chose : stocker et récupérer des mémoires.** L'IA se souvient du contexte, et ensuite ? Les bugs ne sont pas suivis, les tâches de développement ne sont pas gérées, la progression est perdue au changement de session, et les règles que vous avez écrites sont ignorées de toute façon. La mémoire n'est que le point de départ, pas la ligne d'arrivée.
>
> **AIVectorMemory est le seul serveur MCP qui combine mémoire, suivi de problèmes et gestion de tâches en un.** Recherche sémantique avec rappel précis (chercher « timeout base de données » trouve « piège du pool de connexions MySQL »), `track` suivi de problèmes + `task` gestion de tâches intégrés pour que l'IA exécute automatiquement tout le workflow de développement, `status` pour la synchronisation d'état inter-sessions sans perte de progression, et Hooks pour imposer les règles de workflow. Installation en un clic sur 10 IDEs, toutes les données stockées localement sans dépendance cloud.

## ✨ Fonctionnalités Principales


**Ce que les autres n'ont pas :**

| Capacité Unique | Description | mem0 / Cline MB l'a ? |
|-----------------|-------------|----------------------|
| 🔗 **Suivi de problèmes (track)** | Bug trouvé → investigation → correction → test → archivage, gestion complète du cycle de vie | ❌ Aucun des deux |
| 📋 **Gestion de tâches (task)** | requirements → design → tasks, les exigences multi-étapes sont auto-découpées et exécutées | ❌ Aucun des deux |
| 📡 **État inter-sessions (status)** | État de blocage, tâche en cours, progression — rien de perdu au changement de session | ❌ Aucun des deux |
| 🛡️ **Hooks application des règles** | bash_guard / stop_guard / check_track, blocage dur des violations de règles | ❌ Aucun des deux |

**Capacités de base également en tête :**

| Fonctionnalité | Description |
|----------------|-------------|
| 🧠 **Mémoire Inter-Sessions** | Erreurs, décisions, conventions — tout persiste entre les sessions |
| 🔍 **Recherche Sémantique** | Correspondance par similarité vectorielle, rappel précis même avec des termes différents |
| 💰 **Économie 50%+ Tokens** | Récupération à la demande, ne charge que les mémoires pertinentes, adieu l'injection massive |
| 🏠 **Entièrement Local** | Inférence locale ONNX, zéro dépendance cloud, les données ne quittent jamais votre machine |
| 🔌 **10 IDEs** | Cursor / Kiro / Claude Code / Windsurf / VSCode / Copilot / OpenCode / Trae / Codex / Gemini CLI |
| 📊 **App Desktop + Tableau de Bord Web** | Gestion visuelle des mémoires et tâches, réseau vectoriel 3D pour voir les connexions de connaissances |
| 🔄 **Déduplication Intelligente** | Similarité > 0.95 fusionne automatiquement, la base de mémoires reste toujours propre |
| 🌐 **7 Langues** | 简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語 |

<p align="center">
  QQ群：1085682431 &nbsp;|&nbsp; 微信：changhuibiz<br>
  共同参与项目开发加QQ群或微信交流
</p>

## 🏗️ Architecture

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
│  │     SQLite + sqlite-vec (Index Vectoriel)  │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 Démarrage Rapide

### Option 1 : Installation pip (Recommandé)

```bash
# Installer
pip install aivectormemory

# Mettre à jour vers la dernière version
pip install --upgrade aivectormemory

# Aller dans votre répertoire de projet, configuration IDE en un clic
cd /path/to/your/project
avmrun install
```

`avmrun install` vous guide interactivement pour choisir votre IDE, génère automatiquement la configuration MCP, les règles Steering et les Hooks — aucune configuration manuelle nécessaire.

> **Utilisateurs macOS attention** :
> - En cas d'erreur `externally-managed-environment`, ajoutez `--break-system-packages`
> - En cas d'erreur `enable_load_extension`, votre Python ne supporte pas le chargement d'extensions SQLite (le Python intégré de macOS et les installateurs python.org ne le supportent pas). Utilisez Homebrew Python :
>   ```bash
>   brew install python
>   /opt/homebrew/bin/python3 -m pip install aivectormemory
>   ```

### Option 2 : uvx (sans installation)

Pas besoin de `pip install`, exécutez directement :

```bash
cd /path/to/your/project
uvx aivectormemory install
```

> [uv](https://docs.astral.sh/uv/getting-started/installation/) doit être installé. `uvx` télécharge et exécute automatiquement le paquet.

### Option 3 : Configuration manuelle

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
<summary>📍 Emplacements des fichiers de configuration par IDE</summary>

| IDE | Chemin de configuration |
|-----|------------------------|
| Kiro | `.kiro/settings/mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Claude Code | `.mcp.json` |
| Windsurf | `.windsurf/mcp.json` |
| VSCode | `.vscode/mcp.json` |
| Trae | `.trae/mcp.json` |
| OpenCode | `opencode.json` |
| Codex | `.codex/config.toml` |

</details>

Pour Codex, utilisez une configuration TOML au niveau du projet au lieu de JSON :

```toml
[mcp_servers.aivectormemory]
command = "run"
args = ["--project-dir", "/path/to/your/project"]
```

> Codex ne charge le `.codex/config.toml` du projet qu'après avoir marqué le dépôt comme trusted project.

## 🛠️ 8 Outils MCP

### `remember` — Stocker une mémoire

```
content (string, requis)   Contenu au format Markdown
tags    (string[], requis)  Étiquettes, ex. ["erreur", "python"]
scope   (string)            "project" (par défaut) / "user" (inter-projets)
```

Similarité > 0.95 met à jour automatiquement la mémoire existante, sans doublons.

### `recall` — Recherche sémantique

```
query   (string)     Mots-clés de recherche sémantique
tags    (string[])   Filtre exact par étiquettes
scope   (string)     "project" / "user" / "all"
top_k   (integer)    Nombre de résultats, par défaut 5
```

Correspondance par similarité vectorielle — trouve des mémoires liées même avec des mots différents.

### `forget` — Supprimer des mémoires

```
memory_id  (string)     ID unique
memory_ids (string[])   IDs en lot
```

### `status` — État de session

```
state (object, optionnel)   Omettre pour lire, passer pour mettre à jour
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

Maintient la progression du travail entre les sessions, restaure automatiquement le contexte.

### `track` — Suivi des problèmes

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   Titre du problème
issue_id (integer)  ID du problème
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   Contenu d'investigation
```

### `task` — Gestion des tâches

```
action     (string, requis)  "batch_create" / "update" / "list" / "delete" / "archive"
feature_id (string)          Identifiant de fonctionnalité associée (requis pour list)
tasks      (array)           Liste de tâches (batch_create, sous-tâches supportées)
task_id    (integer)         ID de tâche (update)
status     (string)          "pending" / "in_progress" / "completed" / "skipped"
```

Lié aux documents spec via feature_id. Update synchronise automatiquement les checkboxes tasks.md et le statut des problèmes associés.

### `readme` — Génération de README

```
action   (string)    "generate" (par défaut) / "diff" (comparer les différences)
lang     (string)    Langue : en / zh-TW / ja / de / fr / es
sections (string[])  Sections spécifiques : header / tools / deps
```

Génère automatiquement le contenu README depuis TOOL_DEFINITIONS / pyproject.toml, support multilingue.

### `auto_save` — Sauvegarde automatique des préférences

```
preferences  (string[])  Préférences techniques exprimées par l'utilisateur (scope=user fixe, inter-projets)
extra_tags   (string[])  Étiquettes supplémentaires
```

Extrait et stocke automatiquement les préférences utilisateur à la fin de chaque conversation, déduplication intelligente.

## 📊 Tableau de Bord Web

```bash
avmrun web --port 9080
avmrun web --port 9080 --quiet          # Supprimer les logs de requêtes
avmrun web --port 9080 --quiet --daemon  # Exécuter en arrière-plan (macOS/Linux)
```

Visitez `http://localhost:9080` dans votre navigateur. Nom d'utilisateur par défaut `admin`, mot de passe `admin123` (modifiable dans les paramètres après la première connexion).

- Basculement entre projets, parcourir/rechercher/modifier/supprimer/exporter/importer les mémoires
- Recherche sémantique (correspondance par similarité vectorielle)
- Suppression des données de projet en un clic
- État de session, suivi des problèmes
- Gestion des étiquettes (renommer, fusionner, suppression par lots)
- Protection par authentification Token
- Visualisation 3D du réseau vectoriel de mémoires
- 🌐 Support multilingue (简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語)

<p align="center">
  <img src="003.png" alt="Connexion" width="100%">
  <br>
  <em>Connexion</em>
</p>

<p align="center">
  <img src="dashboard-projects.png" alt="Sélection de Projet" width="100%">
  <br>
  <em>Sélection de Projet</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="Aperçu & Visualisation du Réseau Vectoriel" width="100%">
  <br>
  <em>Aperçu & Visualisation du Réseau Vectoriel</em>
</p>

<p align="center">
  <img src="20260306234753_6_1635.jpg" alt="Groupe WeChat" width="280">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="8_1635.jpg" alt="Groupe QQ : 1085682431" width="280">
  <br>
  <em>Rejoindre le groupe WeChat &nbsp;|&nbsp; Rejoindre le groupe QQ</em>
</p>

## ⚡ Combinaison avec les Règles Steering

AIVectorMemory est la couche de stockage. Utilisez les règles Steering pour indiquer à l'IA **quand et comment** appeler ces outils.

L'exécution de `avmrun install` génère automatiquement les règles Steering et la configuration des Hooks — aucune configuration manuelle nécessaire.

| IDE | Emplacement Steering | Hooks |
|-----|---------------------|-------|
| Kiro | `.kiro/steering/aivectormemory.md` | `.kiro/hooks/*.hook` |
| Cursor | `.cursor/rules/aivectormemory.md` | `.cursor/hooks.json` |
| Claude Code | `CLAUDE.md` (ajouté) | `.claude/settings.json` |
| Windsurf | `.windsurf/rules/aivectormemory.md` | `.windsurf/hooks.json` |
| VSCode | `.github/copilot-instructions.md` (ajouté) | `.claude/settings.json` |
| Trae | `.trae/rules/aivectormemory.md` | — |
| OpenCode | `AGENTS.md` (ajouté) | `.opencode/plugins/*.js` |
| Codex | `AGENTS.md` (ajouté) | — |

<details>
<summary>📋 Exemple de Règles Steering (généré automatiquement)</summary>

```markdown
# AIVectorMemory - Règles de Workflow

## ⚠️ Classification du Type de Message
Classifier → discussion : répondre directement ; problème/bug : track create → flux de suivi des problèmes ; fonctionnalité multi-étapes : flux Spec

## ⚠️ Flux de Suivi des Problèmes
1. track create → 2. investiguer (recall + examiner le code) → 3. présenter la solution, bloquer
→ 4. utilisateur confirme, modifier le code → 5. exécuter les tests + grep effets secondaires → 6. track update
→ 7. bloquer pour vérification → 8. utilisateur confirme, track archive

## ⚠️ Flux de Gestion des Tâches (Spec)
1. track create → 2. créer le répertoire spec → 3. requirements.md → 4. design.md → 5. tasks.md
→ 6. task batch_create → 7. exécuter les sous-tâches dans l'ordre → 8. auto-test complet, bloquer

## ⚠️ Règles de Blocage / Standards d'Auto-test / Standards de Développement
(Règles complètes générées automatiquement par `avmrun install`)
```

</details>

<details>
<summary>🔗 Exemple de Configuration Hooks (Kiro uniquement, généré automatiquement)</summary>

Sauvegarde automatique en fin de session supprimée. Vérification du workflow de développement (`.kiro/hooks/dev-workflow-check.kiro.hook`) :

```json
{
  "enabled": true,
  "name": "Vérification du Workflow de Développement",
  "version": "1",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "Principes : vérifier avant d'agir, pas de tests à l'aveugle, ne marquer comme terminé qu'après réussite des tests"
  }
}
```

</details>

## 🇨🇳 Utilisateurs en Chine

Le modèle d'Embedding (~200Mo) est téléchargé automatiquement au premier lancement. Si c'est lent :

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

Ou ajouter env dans la configuration MCP :

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 Stack Technique

| Composant | Technologie |
|-----------|-----------|
| Runtime | Python >= 3.10 |
| BD Vectorielle | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| Tokenizer | HuggingFace Tokenizers |
| Protocole | Model Context Protocol (MCP) |
| Web | HTTPServer natif + Vanilla JS |

## 📋 Journal des Modifications

### v2.2.6

**Synchronisation des règles : DEV_WORKFLOW_PROMPT entièrement aligné avec STEERING_CONTENT**
- 📝 Ajout de la ligne « Interdit », ajout de la ligne « suivre le flux correspondant »
- 📝 Principes fondamentaux restaurés en version complète, ajout de la section « Comment exécuter (standards d'exécution) »
- 🌐 Les 7 fichiers de langues synchronisés

### v2.2.5

**Refactorisation : Principes fondamentaux simplifiés + standards d'exécution + suppression du hook check_track**
- 📝 Principes fondamentaux réduits de 11 à 9 — colmatage des failles, blocage des voies de contournement
- 📝 Ajout du bloc de standards d'exécution « Comment faire » : vérification = appeler l'outil, trouver la cause racine = afficher la correspondance, test réussi = montrer la sortie brute, recall doit précéder les opérations non-code
- 🛡️ Suppression du hook preToolUse check_track (l'interception erronée des opérations Write poussait l'IA à contourner via Bash)
- 🛡️ Description de bash_guard corrigée (ne trompe plus l'IA en lui faisant croire que le déploiement est bloqué)
- 🌐 Les 7 langues synchronisées

### v2.2.3

**Amélioration : Restructuration des règles — workflow simplifié avec séparation claire des flux**
- 📝 Restructuration de 19 sections numérotées en 9 sections thématiques (sans numérotation)
- 📝 Flux de suivi des problèmes (8 étapes) et flux de gestion des tâches / Spec (8 étapes) séparés
- 📝 Standards d'auto-test ajoutés en section autonome avec sélection claire de la méthode de test
- 📝 Injection Hooks (inject-workflow-rules.sh) simplifiée — sécurité IDE, checklist post-édition et exemples de violations supprimés
- 📝 Hook check_track : les fichiers non-code (.md/.sh/.json/.yaml etc.) contournent la vérification de suivi des problèmes
- 🌐 Les 7 langues synchronisées

### v2.2.2

**Amélioration : Restructuration de la numérotation — A-I → 1-19 numérotation plate**
- 📝 19 règles avec numérotation plate, 7 langues synchronisées

### v2.2.1

**Hotfix : Suppression du blocage dur git commit/push + Détection d'opérations manuelles élargie**
- 🐛 bash_guard ne bloque plus git commit/push. Règles steering + stop_guard
- 🛡️ stop_guard liste de mots élargie
- 📝 G1-G4 checklist : « exécuter immédiatement » ajouté

### v2.2.0

**Majeur : Hooks Universels — 8 IDEs, 7 Langues, Multiplateforme, Mise à Jour Auto**
- 🛡️ Hooks migrés de .sh vers modules Python (`python3 -m aivectormemory.hooks.xxx`) — multiplateforme, pip upgrade appliqué instantanément
- 🛡️ `bash_guard` étendu à 7 règles : + blocage git commit/push + blocage commandes de déploiement
- 🛡️ `stop_guard` étendu à 7 vérifications : + tests backend + grep effets de bord + track update + status blocage
- 🌐 Tous les messages d'erreur des hooks en 7 langues
- 🔌 bash_guard déployé sur tous les IDEs : Cursor, Windsurf, Kiro, Codex CLI, Copilot, Gemini CLI
- 🆕 Nouveaux IDEs supportés : Codex CLI, GitHub Copilot, Gemini CLI
- ✅ Suite de tests : 48 → 114 tests

### v2.1.11

**Correction : Suppression de mémoire bureau + Suppression par lot du tableau de bord web**
- 🐛 Corrigé la suppression de mémoire non fonctionnelle dans l'app bureau — remplacé `confirm()` natif (non supporté dans Wails WebView) par un composant Modal personnalisé
- ✨ Ajout de l'interface de suppression par lot aux pages de mémoire du tableau de bord web (projet + global) — bouton mode lot, sélection checkbox, tout sélectionner, suppression par lot avec confirmation
- 🌐 Ajout des traductions de suppression par lot dans les 7 langues

### v2.1.10

**Amélioration : Règle d'auto-correction — l'AI doit corriger ses propres erreurs sans demander**
- 📝 Principe fondamental #5 renforcé (7 langues synchronisées) : « Ses propres erreurs opérationnelles doivent être corrigées par soi-même — ne jamais demander à l'utilisateur s'il faut les corriger »

### v2.1.9

**Amélioration : Application des règles par Hooks — Bash Guard + Stop Guard + Arbre de décision des tests**
- 🛡️ Nouveau `bash_guard.sh` (PreToolUse Bash) : bloque `open http` (utiliser Playwright MCP), `python3 -c` multiligne, combinaisons `$()+pipe`, `mysql -e` instructions multiples
- 🛡️ Nouveau `stop_guard.sh` (Stop hook) : analyse le transcript pour détecter — code modifié sans vérification Playwright + réponse contenant des mots d'« opération manuelle ». L'AI doit utiliser Playwright ou déclarer explicitement « cette modification n'affecte pas les pages frontend »
- 🎯 Arbre de décision des tests ajouté à la règle G1 (7 langues synchronisées) : choisir la méthode de test selon la portée de l'impact (code frontend→Playwright, API affecte la page→curl+Playwright, backend pur→pytest/curl, incertain→Playwright)
- 🔧 Suppression de `_cleanup_legacy_playwright` (la réinstallation ne supprime plus la configuration Playwright existante)
- 🔧 Valeur par défaut d'installation Playwright MCP changée de N à Y
- 🔧 Règles d'auto-test renforcées : charger Playwright MCP avec ToolSearch avant utilisation, ne jamais supposer que les outils ne sont pas disponibles

### v2.1.8

**Amélioration : Restauration des Règles de Travail — Étapes de Flux Détaillées + Protection Anti-Omission**
- 📝 Restauration des étapes détaillées du flux de travail de la version pré-simplification (étapes C/D/E/F/I avec formats recall explicites, points de contrôle d'investigation, gestion des interruptions)
- 🛡️ Nouvelle règle de protection : lorsque l'utilisateur mentionne des mots négatifs (« incorrect/ne marche pas/manquant/erreur ») → par défaut `track create` — l'IA ne peut plus juger « c'est par conception » et sauter l'enregistrement
- ⚠️ Les 11 en-têtes de section sont maintenant préfixés par ⚠️ pour une priorité d'attention plus élevée
- 🌐 Section 1 unifiée en `IDENTITY & TONE` avec des clés de champ en anglais (Role/Language/Voice/Authority) dans les 7 langues
- 🔧 Correction de l'ancre `_write_steering` pour supporter les formats d'en-têtes flexibles

### v2.1.7

**Correction : Configuration Playwright MCP Plus Forcée**
- 🔧 Playwright MCP est désormais optionnel lors de `install` (demandé uniquement si `npx` est disponible, défaut : Non)
- 🩹 `install` nettoie automatiquement les configurations Playwright héritées des anciennes versions — corrige le crash OpenCode « mcp.playwright: Invalid input »
- 🗑️ Suppression de `auto_repair_playwright_config` au démarrage du serveur (inaccessible en cas d'échec de validation de configuration)
- ➕ Ajout de `avmrun` comme alias CLI court (`avmrun install`, `avmrun web`, etc.)

### v2.1.6

**Correction : Point d'Entrée CLI Renommé**
- 🔧 Point d'entrée CLI renommé de `run` en `aivectormemory` — `uvx aivectormemory` fonctionne désormais directement sans contournement `--from`
- ♻️ Nom `prog` d'argparse et configuration d'installation mis à jour en synchronisation

### v2.1.5

**Correction : Compatibilité de Configuration Playwright MCP**
- 🔧 Correction de l'erreur `mcp.playwright: Invalid input` sur OpenCode après mise à jour — `_build_playwright_config` manquait le traitement du format OpenCode (absence de `type: local` + `command` en tableau)
- ♻️ Refactorisation de `_build_playwright_config` pour réutiliser la logique de format de `_build_config` — élimine les branches dupliquées, s'adapte automatiquement à tous les formats d'IDE
- 🩹 Ajout de `auto_repair_playwright_config` : le serveur MCP détecte et répare automatiquement les configurations Playwright incorrectes au démarrage — mise à jour transparente, aucune réinstallation manuelle nécessaire

### v2.1.4

**Correction : Visibilité des Mémoires Remplacées**
- 🔓 Suppression du filtre dur qui masquait complètement les mémoires remplacées des résultats de recall — auparavant `exclude_superseded=true` (par défaut) bloquait les mémoires avant le scoring, les rendant définitivement invisibles
- 📊 Les mémoires remplacées sont désormais classées naturellement via la réduction d'importance (`×0.3`) + scoring `sqrt(importance)` — elles apparaissent plus bas dans les résultats au lieu de disparaître entièrement
- 🧹 Suppression de la fonction `_load_superseded_ids` et du code mort associé

### v2.1.3

**Correction : Refonte du Moteur de Scoring**
- 🧮 Correction d'un bug critique : le score composite utilise désormais la similarité vectorielle originale au lieu du score de rang RRF — auparavant une similarité de ~0.8 était remplacée par un score RRF de ~0.015, détruisant le signal de pertinence sémantique
- √ importance passe d'un multiplicateur direct à `sqrt(importance)` — réduit la pénalité extrême (0.15 → 0.387 au lieu de 0.15) tout en préservant la suppression supersede
- 🛡️ Plancher de similarité : les souvenirs avec une similarité ≥ 0.85 obtiennent un score minimum garanti, empêchant les souvenirs à haute pertinence d'être enfouis par une faible importance
- ⚖️ Rééquilibrage des poids : similarity 0.55 (avant 0.5), recency 0.30, frequency 0.15 (avant 0.2) — la pertinence sémantique domine désormais le classement
- 📉 Repli FTS-uniquement réduit de 0.5 à 0.3 — les correspondances purement par mots-clés n'obtiennent plus de scores de similarité gonflés

### v2.1.2

**Correction : Précision de la Recherche de Mémoire**
- 🔍 Correction de la coupure gloutonne dans la recherche par niveaux : les résultats `long_term` empêchaient la recherche des mémoires `short_term`, rendant invisibles des mémoires très pertinentes
- 🔧 Les deux niveaux sont maintenant recherchés simultanément, classés par score composite (similarité × récence × fréquence × importance)
- 🛡️ Correction du bug de mutation du dictionnaire `filters` dans `_search_tier`

### v2.1.1

**Amélioration : Mise à niveau du système de règles IA**
- 📋 CLAUDE.md complété : ajout Identité et Ton (§1), 7 Principes Fondamentaux (§3), exemples de jugement de type de message, sections sécurité IDE et auto-test étendues
- ⚠️ Hook avec Rappel des Violations Fréquentes : exemples ❌ négatifs renforçant les 4 règles les plus fréquemment oubliées (auto-test, recall, track create, sécurité IDE)
- 🌐 Les 7 fichiers de règles linguistiques mis à jour en synchronisation (zh-CN/zh-TW/en/ja/es/de/fr)
- 🔢 Sections de CLAUDE.md renumérotées en §1–§11, références croisées mises à jour

### v2.1.0

**Nouveau : Moteur de Mémoire Intelligent + Désinstallation**
- 🧠 Recherche plein texte FTS5 avec tokenisation chinoise (jieba) — la recherche par mots-clés fonctionne désormais correctement pour le contenu CJK
- 🔀 Recherche hybride : vecteur + FTS5 double voie avec fusion RRF (Reciprocal Rank Fusion)
- 📊 Score composite : similarité×0,5 + récence×0,3 + fréquence×0,2, pondéré par l'importance
- ⚡ Détection de conflits : les mémoires similaires (0,85–0,95) sont automatiquement marquées comme remplacées, les anciens faits s'estompent
- 📦 Niveaux de mémoire : les mémoires fréquemment consultées sont automatiquement promues en long_term et recherchées en priorité
- 🗑️ Auto-archivage : les mémoires à court terme expirées (90 jours d'inactivité + faible importance) sont nettoyées automatiquement
- 🔗 Expansion des relations : chevauchement de tags ≥ 2 crée des liens associés, expansion à 1 saut pour découvrir les mémoires connexes
- 📝 Auto-résumé : les mémoires longues (>500 caractères) reçoivent des résumés, le mode brief renvoie les résumés pour économiser des tokens
- 🧹 Nettoyage du code : 15 éléments de code mort supprimés, 7 motifs dupliqués refactorisés en utilitaires partagés
- ❌ `avmrun uninstall` — supprime proprement toutes les configurations IDE (MCP, steering, hooks, permissions) en préservant les données de mémoire

### v2.0.9

**Amélioration : Sécurité et Optimisation des Règles**
- 🔒 Correction des vulnérabilités d'injection SQL, d'injection de commandes et de traversée de répertoires
- 🛡️ Protection transactionnelle ajoutée pour l'intégrité des données (opérations d'archivage, insertion, mise à jour)
- 🧠 Formule de similarité unifiée sur tous les chemins de recherche
- 📏 Règles de flux de travail AI compressées de 38% (219→136 lignes) sans suppression de processus
- 🧹 Migration v12 nettoie automatiquement les mémoires obsolètes
- 🌐 Les 7 langues synchronisées

### v2.0.8

**Nouveau : Tests Navigateur Playwright Intégrés**
- 🎭 `avmrun install` configure maintenant automatiquement les tests navigateur Playwright — l'IA peut ouvrir un vrai navigateur pour vérifier les changements frontend
- 🎭 Utilise un navigateur de test dédié (Chrome for Testing) qui n'interfère pas avec vos onglets personnels
- 🔑 Configuration des permissions simplifiée — plus de popups de permissions pour les outils courants
- 📏 Règles IA mises à jour dans les 7 langues pour imposer le bon comportement de test navigateur

### v2.0.7

**Amélioration : Plus de Support IDEs**
- 🖥️ Support ajouté pour Antigravity et GitHub Copilot IDEs
- 🔑 `avmrun install` configure automatiquement les permissions des outils
- 📏 Règles d'auto-test IA simplifiées

### v2.0.6

**Amélioration : Démarrage Plus Rapide**
- ⚡ Chargement mémoire optimisé au démarrage de session — démarrage plus rapide avec moins d'utilisation de contexte
- 🔑 Configuration automatique des permissions Claude Code lors de l'installation
- 🌐 7 langues synchronisées

### v2.0.5

**Amélioration : Règles Simplifiées**
- 📏 Règles de workflow IA restructurées pour plus de clarté et réduction de l'utilisation de tokens
- 💾 L'IA sauvegarde maintenant automatiquement vos préférences à la fin de chaque session
- 🌐 7 langues synchronisées

### v2.0.4

**Correction : Fiabilité des Outils**
- 🔧 Audit et correction complets de tous les paramètres des outils MCP

### v2.0.3

**Amélioration : Meilleure Recherche & Sécurité**
- 🔍 La recherche mémoire combine maintenant correspondance sémantique et par mots-clés pour plus de précision
- 🛡️ Protection contre les opérations inter-projets ajoutée

### v2.0.2

**Amélioration : Généralisation des Règles & Correction Version Bureau**
- 📏 Nouvelle règle « recall avant de demander à l'utilisateur » — l'IA doit interroger le système de mémoire avant de demander des informations projet à l'utilisateur (adresse serveur, mots de passe, configuration de déploiement, etc.)
- 📏 Règle de vérification pré-opération généralisée — exemples spécifiques supprimés pour s'appliquer à tous les scénarios
- 🖥️ Correction de la page de paramètres du bureau affichant la version "1.0.0" codée en dur au lieu de la version réelle
- 🌐 Règles de direction et prompts de flux de travail synchronisés dans les 7 langues

### v2.0.1

**Correction : Compatibilité des Hooks entre projets**
- 🔧 `check_track.sh` dérive désormais le chemin du projet depuis l'emplacement du script au lieu de `$(pwd)`, corrigeant l'échec de détection de track quand Claude Code exécute les hooks depuis un autre répertoire
- 🔧 `compact-recovery.sh` utilise désormais la dérivation de chemin relatif au lieu de chemins absolus codés en dur
- 🔧 Suppression de la réinjection redondante de CLAUDE.md dans compact-recovery (déjà chargé automatiquement)
- 🔧 Modèle `install.py` synchronisé avec toutes les corrections de hooks
- 🌐 Textes d'indication compact-recovery mis à jour dans les 7 langues

### v2.0

**Performance : Quantification ONNX INT8**
- ⚡ Le modèle d'embedding est automatiquement quantifié de FP32 à INT8 au premier chargement, fichier modèle de 448Mo à 113Mo
- ⚡ Utilisation mémoire du MCP Server réduite de ~1,6Go à ~768Mo (réduction de plus de 50%)
- ⚡ La quantification est transparente pour l'utilisateur — automatique à la première utilisation, mise en cache pour les chargements suivants, retour au FP32 en cas d'échec

**Nouveau : Se souvenir du mot de passe**
- 🔐 La page de connexion du client de bureau et du tableau de bord web dispose désormais d'une case "Se souvenir du mot de passe"
- 🔐 Lorsque cochée, les identifiants sont sauvegardés dans localStorage et remplis automatiquement à la prochaine connexion ; lorsque décochée, les identifiants sauvegardés sont supprimés
- 🔐 La case est masquée en mode inscription

**Renforcement : Règles Steering**
- 📝 Section IDENTITY & TONE renforcée avec des contraintes plus spécifiques (pas de formules de politesse, pas de traduction des messages utilisateur, etc.)
- 📝 Les exigences d'auto-test distinguent désormais entre backend pur, MCP Server et changements visibles en frontend (Playwright requis pour le frontend)
- 📝 Les règles de développement exigent désormais l'auto-test après la fin du développement
- 📝 Les 7 versions linguistiques synchronisées

### v1.0.11

- 🐛 Comparaison de version du client de bureau passée au versionnage sémantique, correction des fausses alertes de mise à jour quand la version locale est supérieure
- 🐛 Noms des champs de la page de vérification de santé alignés avec le backend, correction du statut de cohérence affichant toujours Mismatch
- 🔧 Hook check_track.sh avec fallback Python ajouté, résolution de l'échec silencieux du hook sans sqlite3 système (#4)

### v1.0.10

- 🖥️ Installation en un clic du client de bureau + détection de mise à jour
- 🖥️ Détection automatique de l'état d'installation de Python et aivectormemory au démarrage
- 🖥️ Bouton d'installation en un clic si non installé, détection des nouvelles versions PyPI et bureau si installé
- 🐛 Détection d'installation passée à importlib.metadata.version() pour une version de paquet précise

### v1.0.3

**Optimisation de la recherche recall**
- 🔍 `recall` ajoute le paramètre `tags_mode` : `any` (correspondance OR) / `all` (correspondance AND)
- 🔍 `query + tags` utilise OR par défaut (tout tag correspondant entre dans les candidats), résolvant les résultats manqués avec plusieurs tags
- 🔍 `tags` seul conserve AND (navigation précise par catégorie), rétrocompatible
- 📝 Règles de Steering mises à jour avec directives de recherche

### v0.2.8

**Tableau de Bord Web**
- 📋 Modal de détail des problèmes archivés : clic sur une carte archivée affiche les détails en lecture seule (tous les champs structurés : investigation/cause racine/solution/résultat de test/fichiers modifiés), bouton rouge de suppression en bas pour suppression permanente

**Renforcement des Règles Steering**
- 📝 `track create` exige désormais le champ `content` obligatoire (décrire les symptômes et le contexte du problème), interdit d'envoyer uniquement le titre
- 📝 `track update` post-investigation exige les champs `investigation` et `root_cause`
- 📝 `track update` post-correction exige les champs `solution`, `files_changed` et `test_result`
- 📝 Section 4 ajoute la sous-section "Normes de Remplissage des Champs" avec les champs obligatoires par étape
- 📝 Section 5 étendue de "Vérification de Modification de Code" à "Vérification Pré-Opération", ajout de la règle recall des enregistrements d'erreurs avant démarrage du tableau de bord/publication PyPI/redémarrage de service
- 📝 `install.py` STEERING_CONTENT synchronisé avec toutes les modifications

**Optimisation des Outils**
- 🔧 Description du champ `content` de l'outil `track` changée de "contenu d'investigation" à "description du problème (obligatoire lors du create)"

### v0.2.7

**Extraction automatique de mots-clés**
- 🔑 `remember`/`auto_save` extraient automatiquement les mots-clés du contenu pour compléter les tags — l'IA n'a plus besoin de transmettre manuellement des tags complets
- 🔑 Utilise la segmentation chinoise jieba + extraction par regex anglaise, extraction précise de mots-clés pour les contenus mixtes chinois-anglais
- 🔑 Nouvelle dépendance `jieba>=0.42`

### v0.2.6

**Restructuration des règles Steering**
- 📝 Document de règles Steering réécrit de l'ancienne structure à 3 sections vers 9 sections (Démarrage de session / Flux de traitement / Règles de blocage / Suivi des problèmes / Revue de code / Gestion des tâches Spec / Qualité de mémoire / Référence des outils / Standards de développement)
- 📝 Modèle STEERING_CONTENT de `install.py` synchronisé, les nouveaux projets obtiennent les règles mises à jour à l'installation
- 📝 Tags passés de listes fixes à extraction dynamique (mots-clés extraits du contenu), améliorant la précision de recherche de mémoire

**Corrections de bugs**
- 🐛 Outil `readme` `handle_readme()` manquait `**_`, causant l'erreur MCP `unexpected keyword argument 'engine'`
- 🐛 Correction de la pagination de recherche de mémoire du tableau de bord web (filtrage complet avant pagination avec requête de recherche, corrigeant les résultats incomplets)

**Mises à jour de documentation**
- 📖 Nombre d'outils README 7→8, diagramme d'architecture `digest`→`task`, descriptions d'outils `task`/`readme` ajoutées
- 📖 Paramètres `auto_save` mis à jour de `decisions[]/modifications[]/pitfalls[]/todos[]` vers `preferences[]/extra_tags[]`
- 📖 Exemple de règles Steering mis à jour du format 3 sections vers le résumé de structure 9 sections
- 📖 Mises à jour synchronisées sur 6 versions linguistiques

### v0.2.5

**Mode de développement piloté par les tâches**
- 🔗 Le suivi des problèmes (track) et la gestion des tâches (task) sont reliés par `feature_id` en un flux complet : découverte du problème → création de tâche → exécution → synchronisation automatique des statuts → archivage lié
- 🔄 `task update` synchronise automatiquement le statut du problème associé lors de la mise à jour (tout terminé→completed, en cours→in_progress)
- 📦 `track archive` archive automatiquement les tâches associées (liaison lors de l'archivage du dernier problème actif)
- 📦 Nouvelle action `archive` pour l'outil `task`, déplace toutes les tâches du groupe fonctionnel dans la table d'archives `tasks_archive`
- 📊 Les cartes de problèmes affichent la progression des tâches associées (ex. `5/10`), la page des tâches supporte le filtrage par archives

**Nouveaux outils**
- 🆕 Outil `task` — gestion des tâches (batch_create/update/list/delete/archive), sous-tâches arborescentes, lié aux documents spec via feature_id
- 🆕 Outil `readme` — génération automatique du contenu README depuis TOOL_DEFINITIONS/pyproject.toml, multilingue et comparaison de différences

**Améliorations des outils**
- 🔧 `track` : nouvelle action delete, 9 champs structurés (description/investigation/root_cause/solution/test_result/notes/files_changed/feature_id/parent_id), list par issue_id pour élément unique
- 🔧 `recall` : nouveau paramètre source (manual/auto_save) et mode brief (retourne uniquement content+tags, économise le contexte)
- 🔧 `auto_save` : marque les mémoires avec source="auto_save", distingue les mémoires manuelles des sauvegardes automatiques

**Refactorisation par séparation des tables de connaissances**
- 🗃️ project_memories + user_memories en tables indépendantes, élimine les requêtes mixtes scope/filter_dir, amélioration des performances
- 📊 DB Schema v4→v6 : issues ajoutent 9 champs structurés + tables tasks/tasks_archive + champ memories.source

**Tableau de bord Web**
- 📊 Page d'accueil avec carte d'état de blocage (rouge bloqué/vert normal), clic pour accéder à la page d'état de session
- 📊 Nouvelle page de gestion des tâches (groupes fonctionnels pliables, filtrage par statut, recherche, CRUD)
- 📊 Navigation latérale optimisée (état de session, problèmes, tâches remontés en position centrale)
- 📊 Liste des mémoires avec filtrage source et filtre d'exclusion exclude_tags

**Stabilité et normes**
- 🛡️ Boucle principale du serveur avec capture globale des exceptions, les erreurs de message unique ne font plus planter le serveur
- 🛡️ Couche Protocol avec saut de lignes vides et tolérance aux erreurs de parsing JSON
- 🕐 Horodatages changés d'UTC au fuseau horaire local
- 🧹 Nettoyage du code redondant (méthodes non appelées, imports redondants, fichiers de sauvegarde)
- 📝 Modèle Steering avec section workflow Spec et gestion des tâches, règles de continuation context transfer

### v0.2.4

- 🔇 Prompt du hook Stop changé en instruction directe, éliminant les réponses dupliquées de Claude Code
- 🛡️ Règles Steering auto_save avec protection court-circuit, ignore les autres règles en fin de session
- 🐛 Correction d'idempotence de `_copy_check_track_script` (retourner l'état de changement pour éviter les faux "synchronisé")
- 🐛 Correction d'incompatibilité `row.get()` dans issue_repo delete avec `sqlite3.Row` (utiliser `row.keys()`)
- 🐛 Correction du défilement de la page de sélection de projets du tableau de bord Web (impossible de défiler avec beaucoup de projets)
- 🐛 Correction de pollution CSS du tableau de bord Web (strReplace remplacement global a corrompu 6 sélecteurs de style)
- 🔄 Tous les dialogues confirm() du tableau de bord Web remplacés par modal showConfirm personnalisé (supprimer mémoire/issue/tag/projet)
- 🔄 Opérations de suppression du tableau de bord Web avec gestion des réponses d'erreur API (toast au lieu d'alert)
- 🧹 `.gitignore` ajoute la règle d'ignorance du répertoire legacy `.devmemory/`
- 🧪 Nettoyage automatique des résidus de projets temporaires pytest en DB (conftest.py session fixture)

### v0.2.3

- 🛡️ Hook PreToolUse : vérification obligatoire du track issue avant Edit/Write, rejet si aucun issue actif (Claude Code / Kiro / OpenCode)
- 🔌 Plugin OpenCode mis à niveau au format SDK `@opencode-ai/plugin` (hook tool.execute.before)
- 🔧 `avmrun install` déploie automatiquement check_track.sh avec injection dynamique du chemin
- 🐛 Correction de l'incompatibilité `row.get()` avec `sqlite3.Row` dans issue_repo archive/delete
- 🐛 Correction de la condition de concurrence session_id : lecture de la dernière valeur depuis la DB avant incrémentation
- 🐛 Validation du format date de track (YYYY-MM-DD) + validation du type issue_id
- 🐛 Renforcement de l'analyse des requêtes Web API (validation Content-Length + limite 10MB + gestion des erreurs JSON)
- 🐛 Correction de la logique scope du filtre de tags (`filter_dir is not None` au lieu de vérification falsy)
- 🐛 Validation de la longueur des octets struct.unpack pour l'export des données vectorielles
- 🐛 Migration versionnée du schéma (table schema_version + migration incrémentielle v1/v2/v3)
- 🐛 Correction de la synchronisation du numéro de version `__init__.py`

### v0.2.2

- 🔇 Tableau de bord Web : paramètre `--quiet` pour supprimer les logs de requêtes
- 🔄 Tableau de bord Web : paramètre `--daemon` pour exécution en arrière-plan (macOS/Linux)
- 🔧 Correction de la génération de configuration MCP dans `avmrun install` (sys.executable + champs complets)
- 📋 Suivi des problèmes CRUD et archivage (Tableau de bord Web ajout/édition/archivage/suppression + association mémoires)
- 👆 Clic n'importe où sur la ligne pour ouvrir le modal d'édition (mémoires/problèmes/tags)
- 🔒 Règles de blocage appliquées lors des continuations de session/transferts de contexte (reconfirmation requise)

### v0.2.1

- ➕ Ajouter des projets depuis le tableau de bord Web (navigateur de répertoires + saisie manuelle)
- 🏷️ Correction de la contamination des tags entre projets (opérations limitées au projet actuel + mémoires globales)
- 📐 Troncature par points de suspension dans la pagination des modales + largeur 80%
- 🔌 OpenCode install génère automatiquement le plugin auto_save (événement session.idle)
- 🔗 Claude Code / Cursor / Windsurf install génère automatiquement la configuration Hooks (sauvegarde automatique en fin de session)
- 🎯 Améliorations UX du tableau de bord Web (retour Toast, guides d'état vide, barre d'export/import)
- 🔧 Clic sur les cartes de statistiques (clic sur les compteurs mémoire/problèmes pour voir les détails)
- 🏷️ Page de gestion des tags distingue les sources projet/global (marqueurs 📁/🌐)
- 🏷️ Le nombre de tags des cartes projet inclut désormais les tags des mémoires globales

### v0.2.0

- 🔐 Authentification par Token du tableau de bord Web
- ⚡ Cache de vecteurs Embedding, pas de calcul redondant pour un contenu identique
- 🔍 recall supporte la recherche combinée query + tags
- 🗑️ forget supporte la suppression par lots (paramètre memory_ids)
- 📤 Export/import de mémoires (format JSON)
- 🔎 Recherche sémantique dans le tableau de bord Web
- 🗂️ Bouton de suppression de projet dans le tableau de bord Web
- 📊 Optimisation des performances du tableau de bord Web (élimination des analyses complètes de table)
- 🧠 Compression intelligente de digest
- 💾 Persistance de session_id
- 📏 Protection de limite de longueur de content
- 🏷️ Référence dynamique de version (plus codée en dur)

### v0.1.x

- Version initiale : 7 outils MCP, tableau de bord Web, visualisation 3D vectorielle, support multilingue

## License

Apache-2.0
