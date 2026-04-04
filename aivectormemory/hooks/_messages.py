"""AIVectorMemory Hooks — 7 语言错误消息模板

支持：zh-CN / zh-TW / en / ja / de / fr / es
"""

MESSAGES: dict[str, dict[str, str]] = {
    "zh-CN": {
        "open_http_blocked": "⚠️ 禁止使用 open 命令打开浏览器。请使用 Playwright MCP（ToolSearch 加载后 browser_navigate）进行前端测试。",
        "python_multiline_blocked": "⚠️ 禁止 python3 -c 执行多行脚本（超过2行）。请写成 .py 文件用 python3 xxx.py 执行。",
        "subshell_pipe_blocked": "⚠️ 禁止 $(…) + 管道组合，可能导致 IDE 卡死。请拆成多步独立执行。",
        "mysql_multi_blocked": "⚠️ 禁止 MySQL -e 执行多条语句。请写入 .sql 文件用 < data/xxx.sql 执行。",
        "git_commit_blocked": "⚠️ 禁止自行 git commit。必须先完成自测检查清单（G1-G4）并设阻塞等待用户确认后才能提交。",
        "git_push_blocked": "⚠️ 禁止自行 git push。必须先完成自测检查清单并设阻塞等待用户确认，由用户决定是否推送。",
        "deploy_blocked": "⚠️ 禁止自行部署。必须用户明确指示后才能执行部署操作。",
        "no_track_issue": "⚠️ 当前项目没有活跃的 track issue。请先调用 track(action: create) 记录问题后再修改代码。",
        "no_in_progress_task": "⚠️ spec 任务 [{feature_id}] 有待执行的子任务但没有 in_progress 的子任务。请先调用 task(action: update, task_id: X, status: in_progress) 标记当前正在执行的子任务后再修改代码。",
        "manual_words_detected": "⚠️ 回复中包含让用户手动操作的内容（手动/刷新浏览器/请用户等）。禁止让用户手动操作，请自行使用 Playwright MCP 或 curl/pytest 完成验证。",
        "frontend_no_playwright": "⚠️ 前端代码已修改但未使用 Playwright MCP 验证。影响前端 → browser_navigate + browser_snapshot 验证；不影响 → 明确说明「此改动不影响前端」及理由。",
        "backend_no_test": "⚠️ 后端代码已修改但未运行测试（pytest/curl）。请先运行测试验证功能正常。不影响后端 → 明确说明「此改动不影响后端」及理由。",
        "commit_before_test": "⚠️ 检测到 git commit 但在提交前未运行测试。必须先完成 G1-G4 检查清单，测试通过后才能提交。",
        "no_grep_after_edit": "⚠️ 代码已修改但未执行副作用检查（grep 改动涉及的函数/变量名）。请 grep 确认其他调用方不受影响。",
        "no_track_update_after_edit": "⚠️ 代码已修改但未调用 track update 填写 solution/files_changed/test_result。请完成 G4 检查项。",
        "no_status_blocked": "⚠️ 代码已修改并完成测试，但未调用 status 设置阻塞等待用户验证。请调用 status({is_blocked: true, block_reason: '修复完成等待验证'})。",
    },
    "zh-TW": {
        "open_http_blocked": "⚠️ 禁止使用 open 命令開啟瀏覽器。請使用 Playwright MCP（ToolSearch 載入後 browser_navigate）進行前端測試。",
        "python_multiline_blocked": "⚠️ 禁止 python3 -c 執行多行腳本（超過2行）。請寫成 .py 檔案用 python3 xxx.py 執行。",
        "subshell_pipe_blocked": "⚠️ 禁止 $(…) + 管道組合，可能導致 IDE 卡住。請拆成多步獨立執行。",
        "mysql_multi_blocked": "⚠️ 禁止 MySQL -e 執行多條語句。請寫入 .sql 檔案用 < data/xxx.sql 執行。",
        "git_commit_blocked": "⚠️ 禁止自行 git commit。必須先完成自測檢查清單（G1-G4）並設阻塞等待使用者確認後才能提交。",
        "git_push_blocked": "⚠️ 禁止自行 git push。必須先完成自測檢查清單並設阻塞等待使用者確認，由使用者決定是否推送。",
        "deploy_blocked": "⚠️ 禁止自行部署。必須使用者明確指示後才能執行部署操作。",
        "no_track_issue": "⚠️ 當前專案沒有活躍的 track issue。請先呼叫 track(action: create) 記錄問題後再修改程式碼。",
        "no_in_progress_task": "⚠️ spec 任務 [{feature_id}] 有待執行的子任務但沒有 in_progress 的子任務。請先呼叫 task(action: update, task_id: X, status: in_progress) 標記當前正在執行的子任務後再修改程式碼。",
        "manual_words_detected": "⚠️ 回覆中包含讓使用者手動操作的內容。禁止讓使用者手動操作，請自行使用 Playwright MCP 或 curl/pytest 完成驗證。",
        "frontend_no_playwright": "⚠️ 前端程式碼已修改但未使用 Playwright MCP 驗證。影響前端 → browser_navigate + browser_snapshot 驗證；不影響 → 明確說明「此改動不影響前端」及理由。",
        "backend_no_test": "⚠️ 後端程式碼已修改但未執行測試（pytest/curl）。請先執行測試驗證功能正常。",
        "commit_before_test": "⚠️ 偵測到 git commit 但在提交前未執行測試。必須先完成 G1-G4 檢查清單，測試通過後才能提交。",
        "no_grep_after_edit": "⚠️ 程式碼已修改但未執行副作用檢查（grep 改動涉及的函式/變數名）。請 grep 確認其他呼叫方不受影響。",
        "no_track_update_after_edit": "⚠️ 程式碼已修改但未呼叫 track update 填寫 solution/files_changed/test_result。請完成 G4 檢查項。",
        "no_status_blocked": "⚠️ 程式碼已修改並完成測試，但未呼叫 status 設置阻塞等待使用者驗證。",
    },
    "en": {
        "open_http_blocked": "⚠️ Do not use 'open' to launch a browser. Use Playwright MCP (ToolSearch → browser_navigate) for frontend testing.",
        "python_multiline_blocked": "⚠️ Do not use python3 -c for multiline scripts (>2 lines). Write a .py file and run python3 xxx.py instead.",
        "subshell_pipe_blocked": "⚠️ Do not combine $(...) with pipes — it may freeze the IDE. Split into separate commands.",
        "mysql_multi_blocked": "⚠️ Do not use mysql -e with multiple statements. Write a .sql file and execute with < data/xxx.sql.",
        "git_commit_blocked": "⚠️ git commit blocked. Complete the self-test checklist (G1-G4) and wait for user confirmation before committing.",
        "git_push_blocked": "⚠️ git push blocked. Complete the self-test checklist and wait for user confirmation before pushing.",
        "deploy_blocked": "⚠️ Deployment blocked. Only deploy when the user explicitly instructs you to.",
        "no_track_issue": "⚠️ No active track issue found. Call track(action: create) to log the issue before modifying code.",
        "no_in_progress_task": "⚠️ Spec task [{feature_id}] has pending subtasks but none are in_progress. Call task(action: update, task_id: X, status: in_progress) first.",
        "manual_words_detected": "⚠️ Response contains instructions for manual user actions. Do not ask the user to perform manual operations — use Playwright MCP or curl/pytest for verification.",
        "frontend_no_playwright": "⚠️ Frontend code modified but Playwright MCP not used for verification. Use browser_navigate + browser_snapshot, or state 'this change does not affect the frontend' with reasoning.",
        "backend_no_test": "⚠️ Backend code modified but no test (pytest/curl) was run. Run tests to verify, or state 'this change does not affect the backend' with reasoning.",
        "commit_before_test": "⚠️ git commit detected without running tests first. Complete G1-G4 checklist and pass tests before committing.",
        "no_grep_after_edit": "⚠️ Code modified but no side-effect check (grep for affected functions/variables). Grep to confirm no other callers are impacted.",
        "no_track_update_after_edit": "⚠️ Code modified but track update not called with solution/files_changed/test_result. Complete G4 checklist item.",
        "no_status_blocked": "⚠️ Code modified and tested, but status not set to blocked for user verification. Call status({is_blocked: true}).",
    },
    "ja": {
        "open_http_blocked": "⚠️ open コマンドでブラウザを開くことは禁止です。Playwright MCP（ToolSearch → browser_navigate）を使用してください。",
        "python_multiline_blocked": "⚠️ python3 -c で複数行スクリプト（2行超）の実行は禁止です。.py ファイルに書いて python3 xxx.py で実行してください。",
        "subshell_pipe_blocked": "⚠️ $(...) + パイプの組み合わせは禁止です。IDE がフリーズする可能性があります。別々のコマンドに分割してください。",
        "mysql_multi_blocked": "⚠️ mysql -e で複数ステートメントの実行は禁止です。.sql ファイルに書いて < data/xxx.sql で実行してください。",
        "git_commit_blocked": "⚠️ git commit がブロックされました。セルフテストチェックリスト（G1-G4）を完了し、ユーザーの確認を待ってからコミットしてください。",
        "git_push_blocked": "⚠️ git push がブロックされました。セルフテストチェックリストを完了し、ユーザーの確認を待ってからプッシュしてください。",
        "deploy_blocked": "⚠️ デプロイがブロックされました。ユーザーが明示的に指示した場合のみデプロイを実行してください。",
        "no_track_issue": "⚠️ アクティブな track issue がありません。track(action: create) で問題を記録してからコードを変更してください。",
        "no_in_progress_task": "⚠️ spec タスク [{feature_id}] に保留中のサブタスクがありますが、in_progress のサブタスクがありません。",
        "manual_words_detected": "⚠️ 手動操作を求める内容が含まれています。ユーザーに手動操作を求めないでください。",
        "frontend_no_playwright": "⚠️ フロントエンドコードが変更されましたが、Playwright MCP で検証されていません。",
        "backend_no_test": "⚠️ バックエンドコードが変更されましたが、テスト（pytest/curl）が実行されていません。",
        "commit_before_test": "⚠️ テスト実行前に git commit が検出されました。G1-G4 チェックリストを完了してからコミットしてください。",
        "no_grep_after_edit": "⚠️ コードが変更されましたが、副作用チェック（grep）が実行されていません。影響を受ける他の呼び出し元を確認してください。",
        "no_track_update_after_edit": "⚠️ コードが変更されましたが、track update が呼び出されていません。G4 チェック項目を完了してください。",
        "no_status_blocked": "⚠️ コードが変更されテストが完了しましたが、status がブロック状態に設定されていません。",
    },
    "de": {
        "open_http_blocked": "⚠️ Verwendung von 'open' zum Öffnen eines Browsers ist verboten. Verwenden Sie Playwright MCP (ToolSearch → browser_navigate).",
        "python_multiline_blocked": "⚠️ python3 -c mit mehrzeiligen Skripten (>2 Zeilen) ist verboten. Schreiben Sie eine .py-Datei und führen Sie python3 xxx.py aus.",
        "subshell_pipe_blocked": "⚠️ $(...) + Pipe-Kombination ist verboten — kann die IDE einfrieren. In separate Befehle aufteilen.",
        "mysql_multi_blocked": "⚠️ mysql -e mit mehreren Anweisungen ist verboten. In .sql-Datei schreiben und mit < data/xxx.sql ausführen.",
        "git_commit_blocked": "⚠️ git commit blockiert. Vervollständigen Sie die Selbsttest-Checkliste (G1-G4) und warten Sie auf Benutzerbestätigung.",
        "git_push_blocked": "⚠️ git push blockiert. Vervollständigen Sie die Selbsttest-Checkliste und warten Sie auf Benutzerbestätigung.",
        "deploy_blocked": "⚠️ Deployment blockiert. Nur auf ausdrückliche Benutzeranweisung deployen.",
        "no_track_issue": "⚠️ Kein aktives Track-Issue gefunden. Rufen Sie track(action: create) auf, bevor Sie Code ändern.",
        "no_in_progress_task": "⚠️ Spec-Aufgabe [{feature_id}] hat ausstehende Unteraufgaben, aber keine ist in_progress.",
        "manual_words_detected": "⚠️ Antwort enthält Anweisungen für manuelle Benutzeraktionen. Verwenden Sie Playwright MCP oder curl/pytest.",
        "frontend_no_playwright": "⚠️ Frontend-Code geändert, aber Playwright MCP nicht zur Verifizierung verwendet.",
        "backend_no_test": "⚠️ Backend-Code geändert, aber kein Test (pytest/curl) ausgeführt.",
        "commit_before_test": "⚠️ git commit ohne vorherigen Test erkannt. G1-G4 Checkliste abschließen.",
        "no_grep_after_edit": "⚠️ Code geändert, aber keine Seiteneffekt-Prüfung (grep) durchgeführt. Bestätigen Sie, dass andere Aufrufer nicht betroffen sind.",
        "no_track_update_after_edit": "⚠️ Code geändert, aber track update nicht aufgerufen. G4 Checkliste abschließen.",
        "no_status_blocked": "⚠️ Code geändert und getestet, aber Status nicht auf blockiert gesetzt.",
    },
    "fr": {
        "open_http_blocked": "⚠️ L'utilisation de 'open' pour lancer un navigateur est interdite. Utilisez Playwright MCP (ToolSearch → browser_navigate).",
        "python_multiline_blocked": "⚠️ python3 -c avec scripts multilignes (>2 lignes) est interdit. Écrivez un fichier .py et exécutez python3 xxx.py.",
        "subshell_pipe_blocked": "⚠️ La combinaison $(...) + pipe est interdite — peut geler l'IDE. Séparez en commandes distinctes.",
        "mysql_multi_blocked": "⚠️ mysql -e avec plusieurs instructions est interdit. Écrivez dans un fichier .sql et exécutez avec < data/xxx.sql.",
        "git_commit_blocked": "⚠️ git commit bloqué. Complétez la checklist d'auto-test (G1-G4) et attendez la confirmation de l'utilisateur.",
        "git_push_blocked": "⚠️ git push bloqué. Complétez la checklist et attendez la confirmation de l'utilisateur.",
        "deploy_blocked": "⚠️ Déploiement bloqué. Ne déployez que sur instruction explicite de l'utilisateur.",
        "no_track_issue": "⚠️ Aucun track issue actif trouvé. Appelez track(action: create) avant de modifier le code.",
        "no_in_progress_task": "⚠️ La tâche spec [{feature_id}] a des sous-tâches en attente mais aucune n'est in_progress.",
        "manual_words_detected": "⚠️ La réponse contient des instructions d'opérations manuelles. Utilisez Playwright MCP ou curl/pytest.",
        "frontend_no_playwright": "⚠️ Code frontend modifié mais Playwright MCP non utilisé pour la vérification.",
        "backend_no_test": "⚠️ Code backend modifié mais aucun test (pytest/curl) exécuté.",
        "commit_before_test": "⚠️ git commit détecté sans test préalable. Complétez la checklist G1-G4.",
        "no_grep_after_edit": "⚠️ Code modifié mais pas de vérification d'effets de bord (grep). Vérifiez que les autres appelants ne sont pas affectés.",
        "no_track_update_after_edit": "⚠️ Code modifié mais track update non appelé. Complétez l'élément G4 de la checklist.",
        "no_status_blocked": "⚠️ Code modifié et testé, mais statut non défini en blocage pour vérification utilisateur.",
    },
    "es": {
        "open_http_blocked": "⚠️ Prohibido usar 'open' para abrir un navegador. Use Playwright MCP (ToolSearch → browser_navigate).",
        "python_multiline_blocked": "⚠️ Prohibido python3 -c con scripts multilínea (>2 líneas). Escriba un archivo .py y ejecute python3 xxx.py.",
        "subshell_pipe_blocked": "⚠️ Prohibida la combinación $(...) + pipe — puede congelar el IDE. Separe en comandos independientes.",
        "mysql_multi_blocked": "⚠️ Prohibido mysql -e con múltiples sentencias. Escriba en archivo .sql y ejecute con < data/xxx.sql.",
        "git_commit_blocked": "⚠️ git commit bloqueado. Complete la lista de verificación (G1-G4) y espere la confirmación del usuario.",
        "git_push_blocked": "⚠️ git push bloqueado. Complete la lista de verificación y espere la confirmación del usuario.",
        "deploy_blocked": "⚠️ Despliegue bloqueado. Solo despliegue cuando el usuario lo indique explícitamente.",
        "no_track_issue": "⚠️ No se encontró track issue activo. Llame a track(action: create) antes de modificar código.",
        "no_in_progress_task": "⚠️ La tarea spec [{feature_id}] tiene subtareas pendientes pero ninguna está in_progress.",
        "manual_words_detected": "⚠️ La respuesta contiene instrucciones de operaciones manuales. Use Playwright MCP o curl/pytest.",
        "frontend_no_playwright": "⚠️ Código frontend modificado pero Playwright MCP no usado para verificación.",
        "backend_no_test": "⚠️ Código backend modificado pero no se ejecutó ningún test (pytest/curl).",
        "commit_before_test": "⚠️ git commit detectado sin ejecutar tests previos. Complete la checklist G1-G4.",
        "no_grep_after_edit": "⚠️ Código modificado pero no se realizó verificación de efectos secundarios (grep). Confirme que otros llamantes no se ven afectados.",
        "no_track_update_after_edit": "⚠️ Código modificado pero track update no llamado. Complete el elemento G4 de la checklist.",
        "no_status_blocked": "⚠️ Código modificado y probado, pero estado no establecido como bloqueado para verificación del usuario.",
    },
}


def get_message(key: str, **kwargs) -> str:
    """获取当前语言的消息，支持 format 参数

    优先从 aivectormemory settings 获取语言，
    fallback 链：settings → LANG 环境变量 → en
    """
    try:
        from aivectormemory.settings import get_language
        lang = get_language()
    except Exception:
        import os
        lang_env = os.environ.get("LANG", "en")
        if "zh_CN" in lang_env or "zh-CN" in lang_env:
            lang = "zh-CN"
        elif "zh_TW" in lang_env or "zh-TW" in lang_env:
            lang = "zh-TW"
        elif "ja" in lang_env:
            lang = "ja"
        elif "de" in lang_env:
            lang = "de"
        elif "fr" in lang_env:
            lang = "fr"
        elif "es" in lang_env:
            lang = "es"
        else:
            lang = "en"
    msgs = MESSAGES.get(lang, MESSAGES["en"])
    template = msgs.get(key, MESSAGES["en"].get(key, key))
    if kwargs:
        return template.format(**kwargs)
    return template
