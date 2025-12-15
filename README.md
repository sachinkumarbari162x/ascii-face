# ASCII Face

This project contains two implementations of the ASCII Face generator:

## 1. Desktop Application (Python/Go)
A high-performance command-line tool that captures your face and converts it to ASCII art in your terminal.

**Requirements:**
- Python 3.x
- Go (for the launcher, optional)
- OpenCV (`pip install opencv-python`)

**Running:**
```bash
# Run with Python
python vision.py

# Or run with Go Wrapper
go run main.go
```

## 2. Web Application (HTML/JS)
A global production-ready web version designed for deployment on Vercel.

**Features:**
- Real-time ASCII conversion using Canvas API.
- "Matrix" Color Mode & True Color Mode.
- Snapshot functionality.
- Mobile responsive.

**Deployment:**
This `web/` directory is ready for static deployment.
1. Push this repository to GitHub.
2. Import the project into Vercel.
3. Set the **Root Directory** to `web` in Vercel Project Settings.
4. Deploy!

## License
MIT
