package embedding

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

type Engine struct {
	PythonPath string
}

func NewEngine(pythonPath string) *Engine {
	if pythonPath == "" {
		pythonPath = DetectPython()
	}
	return &Engine{PythonPath: pythonPath}
}

func (e *Engine) Encode(text string) ([]float32, error) {
	if e.PythonPath == "" {
		return nil, fmt.Errorf("python not found")
	}

	// Write input to temp file
	tmpDir := os.TempDir()
	inputFile := filepath.Join(tmpDir, "avm_embed_input.json")
	outputFile := filepath.Join(tmpDir, "avm_embed_output.json")

	inputData, _ := json.Marshal(map[string]string{"text": text})
	if err := os.WriteFile(inputFile, inputData, 0644); err != nil {
		return nil, fmt.Errorf("write input: %w", err)
	}
	defer os.Remove(inputFile)
	defer os.Remove(outputFile)

	script := fmt.Sprintf(`
import json, sys
try:
    from aivectormemory.embedding.engine import EmbeddingEngine
    with open(%q) as f:
        data = json.load(f)
    engine = EmbeddingEngine()
    embedding = engine.encode(data["text"])
    with open(%q, "w") as f:
        json.dump({"embedding": embedding}, f)
except Exception as e:
    with open(%q, "w") as f:
        json.dump({"error": str(e)}, f)
`, inputFile, outputFile, outputFile)

	scriptFile := filepath.Join(tmpDir, "avm_embed_script.py")
	if err := os.WriteFile(scriptFile, []byte(script), 0644); err != nil {
		return nil, fmt.Errorf("write script: %w", err)
	}
	defer os.Remove(scriptFile)

	cmd := exec.Command(e.PythonPath, scriptFile)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, fmt.Errorf("python exec: %w, output: %s", err, string(output))
	}

	resultData, err := os.ReadFile(outputFile)
	if err != nil {
		return nil, fmt.Errorf("read output: %w", err)
	}

	var result struct {
		Embedding []float32 `json:"embedding"`
		Error     string    `json:"error"`
	}
	if err := json.Unmarshal(resultData, &result); err != nil {
		return nil, fmt.Errorf("parse output: %w", err)
	}
	if result.Error != "" {
		return nil, fmt.Errorf("embedding error: %s", result.Error)
	}

	return result.Embedding, nil
}

func (e *Engine) EncodeBatch(texts []string) ([][]float32, error) {
	results := make([][]float32, len(texts))
	for i, text := range texts {
		emb, err := e.Encode(text)
		if err != nil {
			return nil, fmt.Errorf("encode text %d: %w", i, err)
		}
		results[i] = emb
	}
	return results, nil
}

// DetectPython finds a Python interpreter with aivectormemory installed.
// Priority: aivectormemory venv → system python → common paths.
func DetectPython() string {
	candidates := pythonCandidates(true)
	for _, py := range candidates {
		path := resolvePython(py)
		if path == "" {
			continue
		}
		out, err := exec.Command(path, "-c", "import aivectormemory; print('ok')").Output()
		if err == nil && strings.TrimSpace(string(out)) == "ok" {
			return path
		}
	}
	return ""
}

// FindSystemPython finds any Python ≥ 3.9 for package installation.
// Priority: system python → common paths → aivectormemory venv (reversed from DetectPython).
func FindSystemPython() string {
	candidates := pythonCandidates(false)
	for _, py := range candidates {
		path := resolvePython(py)
		if path == "" {
			continue
		}
		out, err := exec.Command(path, "-c", "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}')").Output()
		if err != nil {
			continue
		}
		ver := strings.TrimSpace(string(out))
		parts := strings.Split(ver, ".")
		if len(parts) >= 2 {
			major, minor := parts[0], parts[1]
			if major == "3" && minor >= "9" || major > "3" {
				return path
			}
		}
	}
	return ""
}

// pythonCandidates returns candidate paths. When venvFirst=true, aivectormemory
// venv is checked before system paths (for runtime). When false, system paths
// come first (for installation).
func pythonCandidates(venvFirst bool) []string {
	home, _ := os.UserHomeDir()

	// aivectormemory standard venv
	var venvPaths []string
	avmDir := filepath.Join(home, ".aivectormemory", ".venv")
	if runtime.GOOS == "windows" {
		venvPaths = []string{
			filepath.Join(avmDir, "Scripts", "python.exe"),
		}
	} else {
		venvPaths = []string{
			filepath.Join(avmDir, "bin", "python3"),
			filepath.Join(avmDir, "bin", "python"),
		}
	}

	// System-level paths (via PATH lookup)
	var systemPaths []string
	if runtime.GOOS == "windows" {
		systemPaths = []string{"python", "python3", "py"}
	} else {
		systemPaths = []string{"python3", "python"}
	}

	// Well-known installation paths
	var commonPaths []string
	switch runtime.GOOS {
	case "darwin":
		commonPaths = []string{
			"/opt/homebrew/bin/python3",
			"/usr/local/bin/python3",
			"/usr/bin/python3",
		}
	case "linux":
		commonPaths = []string{
			"/usr/bin/python3",
			"/usr/local/bin/python3",
		}
	case "windows":
		localAppData := os.Getenv("LOCALAPPDATA")
		if localAppData != "" {
			commonPaths = append(commonPaths,
				filepath.Join(localAppData, "Programs", "Python", "Python312", "python.exe"),
				filepath.Join(localAppData, "Programs", "Python", "Python311", "python.exe"),
				filepath.Join(localAppData, "Programs", "Python", "Python310", "python.exe"),
			)
		}
		commonPaths = append(commonPaths,
			`C:\Python312\python.exe`,
			`C:\Python311\python.exe`,
			`C:\Python310\python.exe`,
		)
	}

	if venvFirst {
		return append(append(venvPaths, systemPaths...), commonPaths...)
	}
	return append(append(systemPaths, commonPaths...), venvPaths...)
}

// resolvePython resolves a candidate to an absolute path, returns "" if not found.
func resolvePython(candidate string) string {
	if filepath.IsAbs(candidate) {
		if _, err := os.Stat(candidate); err == nil {
			return candidate
		}
		return ""
	}
	found, err := exec.LookPath(candidate)
	if err != nil {
		return ""
	}
	return found
}
