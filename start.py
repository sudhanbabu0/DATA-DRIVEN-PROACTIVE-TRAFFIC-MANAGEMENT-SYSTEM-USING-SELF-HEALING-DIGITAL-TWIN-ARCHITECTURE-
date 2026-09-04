#!/usr/bin/env python3
"""
VTIP — Virtual Traffic Intelligence Platform
Run: python3 start.py
Then open: http://localhost:5050
"""
import subprocess, sys, os, webbrowser, time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("""
╔══════════════════════════════════════════════════════╗
║   VTIP — Virtual Traffic Intelligence Platform       ║
║   Starting backend on http://localhost:5050          ║
╚══════════════════════════════════════════════════════╝
""")

# Start Flask
proc = subprocess.Popen([sys.executable, 'app.py'])
time.sleep(1.5)

# Open browser
try:
    webbrowser.open('http://localhost:5050')
    print("✅ Browser opened. Press Ctrl+C to stop.\n")
except:
    print("✅ Open http://localhost:5050 in your browser.\n")

try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    print("\n🛑 VTIP stopped.")
