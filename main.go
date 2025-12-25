package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"runtime"
	"strings"
	"syscall"
    "time"
)

func main() {
	// 1. Setup minimal ANSI stuff
	hideCursor := "\033[?25l"
	showCursor := "\033[?25h"
	cursorHome := "\033[H"
	// clearScreen := "\033[2J" // Not using this to avoid flicker

	fmt.Print(hideCursor)

	// handle cleanup on interrupt
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-c
		fmt.Print(showCursor)
		os.Exit(0)
	}()

	// 2. Identify Python path
	var pythonPath string
	cwd, _ := os.Getwd()
	if runtime.GOOS == "windows" {
		pythonPath = filepath.Join(cwd, "venv", "Scripts", "python.exe")
	} else {
		pythonPath = filepath.Join(cwd, "venv", "bin", "python")
	}

	if _, err := os.Stat(pythonPath); os.IsNotExist(err) {
		fmt.Printf("Error: Python environment not found at %s. Please ensure 'venv' is created.\n", pythonPath)
		return
	}

    // 3. Determine Mode
    var cameraIdx string
    
    if len(os.Args) > 1 {
        // Argument provided, use it directly (bypass GUI launcher)
        cameraIdx = os.Args[1]
    } else {
        // No argument, use legacy Python Launcher
        cmdLauncher := exec.Command(pythonPath, "launcher.py")
        launchOut, err := cmdLauncher.Output()
        if err != nil {
            fmt.Printf("Error running launcher or no camera selected: %v\n", err)
            return
        }
        
        // Parse index
        cameraIdx = strings.TrimSpace(string(launchOut))
        if cameraIdx == "" {
            fmt.Println("No camera selected.")
            return
        }
    }
    
    fmt.Printf("Launching with Camera %s...\n", cameraIdx)

	// 4. Start Vision Process
	cmd := exec.Command(pythonPath, "vision.py", cameraIdx)
	// cmd.Dir = cwd // Optional, defaults to current
	
	// Get stdout pipe
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		fmt.Printf("Error creating stdout pipe: %v\n", err)
		return
	}
	
	// Get stderr pipe for debugging
	stderr, err := cmd.StderrPipe()
	if err != nil {
		fmt.Printf("Error creating stderr pipe: %v\n", err)
		return
	}
	go func() {
		io.Copy(os.Stderr, stderr)
	}()

	if err := cmd.Start(); err != nil {
		fmt.Printf("Error starting python process: %v\n", err)
		// Fallback check
		fmt.Println("Make sure you are running this from the ascii_face directory where venv is located.")
		return
	}
	defer cmd.Process.Kill()

	// 4. Read Loop
	scanner := bufio.NewScanner(stdout)
	// Increase buffer size just in case lines are huge (ansi codes add up)
	buf := make([]byte, 0, 1024*1024)
	scanner.Buffer(buf, 1024*1024)

	var frameBuilder strings.Builder
    
    // Countdown state
    captured := false
    countdown := 15
    ticker := time.NewTicker(1 * time.Second)
    defer ticker.Stop()
    
    // Ticker loop needs to be separate or integrated?
    // Integrating ticker into scanning is tricky because scanning blocks.
    // Better to run scanning in a goroutine or use select?
    // Scanning in goroutine is cleaner.
    
    lineChan := make(chan string)
    go func() {
        for scanner.Scan() {
            lineChan <- scanner.Text()
        }
        close(lineChan)
    }()

	fmt.Println("Starting Face Detection... (Press Ctrl+C to quit)")

    loop:
	for {
        select {
        case line, ok := <-lineChan:
            if !ok {
                break loop
            }
            
            if strings.HasPrefix(line, "---CAPTURED") {
                // e.g. "---CAPTURED 1---"
                fmt.Println("\n\n*** IMAGE CAPTURED! ***")
            } else if line == "---DONE---" {
                if !captured {
                    captured = true
                    countdown = 5 // User requested 5 seconds after 2nd picture
                    fmt.Printf("\n\nAll images captured. Auto-closing in %d seconds...\n", countdown)
                }
            } else if line == "---FRAME---" {
                // Flush frame
                finalOutput := cursorHome + frameBuilder.String()
                
                // Overlay info if closing
                if captured {
                    finalOutput += fmt.Sprintf("\n\nClosing in %d seconds...", countdown)
                }

                os.Stdout.Write([]byte(finalOutput))
                frameBuilder.Reset()
            } else {
                frameBuilder.WriteString(line)
                frameBuilder.WriteString("\n")
            }
            
        case <-ticker.C:
            if captured {
                countdown--
                if countdown <= 0 {
                    fmt.Println("\n\nTimer expired. Shutting down...")
                    break loop
                }
            }
        
        case <-c:
            // Interrupt
            break loop
        }
	}

	if err := scanner.Err(); err != nil {
		fmt.Printf("Scanner error: %v\n", err)
	}
	
	cmd.Process.Kill()
}
