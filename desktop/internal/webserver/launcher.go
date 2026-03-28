package webserver

import (
	"fmt"
	"net"
	"os/exec"
	"runtime"
	"sync"
	"time"
)

type Launcher struct {
	PythonPath string
	Port       int
	mu         sync.Mutex
	cmd        *exec.Cmd
	waitDone   chan struct{}
}

func NewLauncher(pythonPath string, port int) *Launcher {
	return &Launcher{PythonPath: pythonPath, Port: port}
}

func (l *Launcher) Start() error {
	if l.IsRunning() {
		return fmt.Errorf("web dashboard already running on port %d", l.Port)
	}

	cmd := exec.Command(l.PythonPath, "-m", "aivectormemory", "web", "--port", fmt.Sprintf("%d", l.Port))
	setProcAttr(cmd)
	cmd.Stdout = nil
	cmd.Stderr = nil

	if err := cmd.Start(); err != nil {
		return fmt.Errorf("start web dashboard: %w", err)
	}

	l.mu.Lock()
	l.cmd = cmd
	l.waitDone = make(chan struct{})
	l.mu.Unlock()

	// Wait for process exit via channel instead of bare goroutine
	go func() {
		cmd.Wait()
		l.mu.Lock()
		l.cmd = nil
		l.mu.Unlock()
		close(l.waitDone)
	}()

	// Wait for port to be ready
	go l.waitAndOpenBrowser()

	return nil
}

func (l *Launcher) Stop() error {
	l.mu.Lock()
	cmd := l.cmd
	l.mu.Unlock()

	if cmd != nil && cmd.Process != nil {
		killProcess(cmd)
		l.mu.Lock()
		l.cmd = nil
		l.mu.Unlock()
	}
	return nil
}

func (l *Launcher) IsRunning() bool {
	conn, err := net.DialTimeout("tcp", fmt.Sprintf("127.0.0.1:%d", l.Port), time.Second)
	if err != nil {
		return false
	}
	conn.Close()
	return true
}

func (l *Launcher) waitAndOpenBrowser() {
	for i := 0; i < 30; i++ {
		time.Sleep(2 * time.Second)
		if l.IsRunning() {
			openBrowser(fmt.Sprintf("http://127.0.0.1:%d", l.Port))
			return
		}
	}
}

func openBrowser(url string) {
	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "darwin":
		cmd = exec.Command("open", url)
	case "windows":
		cmd = exec.Command("cmd", "/c", "start", url)
	case "linux":
		cmd = exec.Command("xdg-open", url)
	}
	if cmd != nil {
		cmd.Start()
	}
}

// Detach ensures the web dashboard process survives app shutdown
func (l *Launcher) Detach() {
	l.mu.Lock()
	defer l.mu.Unlock()
	// Process is already detached via Setpgid
	l.cmd = nil
}

// GetPID returns the PID of the running web dashboard, if any
func (l *Launcher) GetPID() int {
	l.mu.Lock()
	defer l.mu.Unlock()
	if l.cmd != nil && l.cmd.Process != nil {
		return l.cmd.Process.Pid
	}
	return 0
}

func PortToString(port int) string {
	return fmt.Sprintf("%d", port)
}

// CheckPort checks if a specific port is available
func CheckPort(port int) bool {
	conn, err := net.DialTimeout("tcp", fmt.Sprintf("127.0.0.1:%d", port), time.Second)
	if err != nil {
		return true // Port is available
	}
	conn.Close()
	return false // Port is in use
}

// FindAvailablePort finds an available port starting from the given port
func FindAvailablePort(startPort int) int {
	for p := startPort; p < startPort+100; p++ {
		if CheckPort(p) {
			return p
		}
	}
	return startPort
}
