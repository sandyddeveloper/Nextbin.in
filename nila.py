import sys
import os
import subprocess
import threading
import time
import ctypes
import socket
from app.core.config import settings

def enable_windows_ansi():
    """
    Enables ANSI escape sequence processing in the Windows Command Prompt (cmd.exe).
    This ensures colors render perfectly on Windows without needing external packages.
    """
    if os.name == 'nt':
        try:
            kernel32 = ctypes.windll.kernel32
            # STD_OUTPUT_HANDLE = -11
            hOut = kernel32.GetStdHandle(-11)
            if hOut != -1 and hOut != 0:
                mode = ctypes.c_ulong()
                if kernel32.GetConsoleMode(hOut, ctypes.byref(mode)):
                    # 0x0004 corresponds to ENABLE_VIRTUAL_TERMINAL_PROCESSING
                    kernel32.SetConsoleMode(hOut, mode.value | 0x0004)
        except Exception:
            pass

def get_local_ips():
    """
    Detects all active local IPv4 addresses assigned to this host's physical network adapters.
    Useful for showing other local network devices how to connect.
    """
    ips = []
    try:
        # Connect to an external public IP to determine which local network interface is routeable
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        ips.append(local_ip)
        s.close()
    except Exception:
        pass
    
    # Fallback to general lookup if connection-based detection fails
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
    except Exception:
        pass
    
    return ips

def read_stream(stream, prefix, color_code):
    """
    Reads a sub-process output stream line by line and prints it with a colored prefix.
    """
    color = f"\033[{color_code}m"
    reset = "\033[0m"
    
    for line in iter(stream.readline, b''):
        decoded_line = line.decode('utf-8', errors='ignore').rstrip()
        if decoded_line:
            print(f"{color}{prefix}{reset} {decoded_line}")
    stream.close()

def watch_cloudflare_tunnel():
    """
    Watches logs/cloudflared.log for a trycloudflare URL and prints it.
    """
    import re
    log_path = os.path.join("logs", "cloudflared.log")
    seen_url = None
    while True:
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
                    if match:
                        url = match.group(0)
                        if url != seen_url:
                            seen_url = url
                            # Save to file
                            os.makedirs("logs", exist_ok=True)
                            with open(os.path.join("logs", "cloudflare_url.txt"), "w") as out:
                                out.write(url)
                            print(f"\n\033[96m🌐 [Cloudflare] Public Tunnel URL active:\033[0m \033[92m\033[1m{url}\033[0m\n")
            except Exception:
                pass
        time.sleep(2)

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
    enable_windows_ansi()
    
    # ANSI Color Definitions
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE_BOLD = "\033[1;37m"
    RESET = "\033[0m"
    
    # ASCII Art Banner
    banner = f"""
{CYAN}    _   _   ___   _         _     
   | \\ | | |_ _| | |       / \\    
   |  \\| |  | |  | |      / _ \\   
   | |\\  |  | |  | |___  / ___ \\  
   |_| \\_| |___| |_____|/_/   \\_\\ {RESET}
   
   {MAGENTA}★ Nextbin.in Automation Suite ★{RESET}
   {YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}
   {WHITE_BOLD}🤖 System Name : NILA (Nextbin Intelligent Local Agent){RESET}
   {GREEN}👤 Developer   : Santhosh Raj{RESET}
   {YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}
    """
    print(banner)
    
    # Get active local physical IP addresses
    local_ips = get_local_ips()
    host_addr = settings.HOST
    port_num = settings.PORT
    
    print(f"{CYAN}🌐 PHYSICAL NETWORK ACCESS ADDRESSES:{RESET}")
    if host_addr == "0.0.0.0":
        print(f"   Listening on ALL interfaces (0.0.0.0). Access from other devices on Wi-Fi:")
        for ip in local_ips:
            print(f"   👉 {GREEN}http://{ip}:{port_num}{RESET}")
    else:
        print(f"   Listening on bound physical address: {GREEN}http://{host_addr}:{port_num}{RESET}")
    print(f"   👉 Local Host: {GREEN}http://localhost:{port_num}{RESET}")
    
    # Custom Internet Domain Exposing Guide (Cloudflare / Ngrok)
    print(f"\n{MAGENTA}🚀 PUBLIC CUSTOM DOMAIN SETUP (Termux & Local Server):{RESET}")
    print(f"   To expose Nila to the internet using a custom domain (free of charge):")
    print(f"   1. Install Cloudflare Tunnels:")
    print(f"      {WHITE_BOLD}Termux:{RESET}  pkg install cloudflared")
    print(f"      {WHITE_BOLD}Windows:{RESET} scoop install cloudflared (or download binary)")
    print(f"   2. Create a tunnel:")
    print(f"      cloudflared tunnel create nila-tunnel")
    print(f"   3. Link tunnel to your custom domain:")
    print(f"      cloudflared tunnel route dns nila-tunnel yourdomain.com")
    print(f"   4. Run the tunnel mapping:")
    print(f"      cloudflared tunnel run --url http://localhost:{port_num} nila-tunnel")
    print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    print(f"{YELLOW}[Nila]{RESET} Starting services...")
    
    # Check if a local virtual environment exists and use its Python context
    # This prevents ModuleNotFoundErrors if the user ran python nila.py without activating the venv
    venv_python = os.path.join("venv", "Scripts" if os.name == 'nt' else "bin", "python.exe" if os.name == 'nt' else "python")
    if os.path.exists(venv_python):
        python_exe = os.path.abspath(venv_python)
        print(f"{YELLOW}[Nila]{RESET} Detected local virtual environment. Using: {CYAN}{python_exe}{RESET}")
    else:
        python_exe = sys.executable
        print(f"{YELLOW}[Nila]{RESET} Using Python runtime: {CYAN}{python_exe}{RESET}")
    
    # Try to locate the local uvicorn script for speed
    bindir = os.path.dirname(python_exe)
    uvicorn_exe = os.path.join(bindir, "uvicorn.exe" if os.name == 'nt' else "uvicorn")
    
    if os.path.exists(uvicorn_exe):
        api_cmd = [uvicorn_exe, "app.main:app", "--host", host_addr, "--port", str(port_num)]
    else:
        api_cmd = [python_exe, "-m", "uvicorn", "app.main:app", "--host", host_addr, "--port", str(port_num)]
        
    worker_cmd = [python_exe, "-m", "huey.bin.huey_consumer", "app.workers.tasks.huey", "-w", "2", "-k", "thread"]
    
    api_process = subprocess.Popen(
        api_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0
    )
    
    worker_process = subprocess.Popen(
        worker_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0
    )
    
    # Start separate thread supervisors to read stdout/stderr from both processes in real time
    # 95 = Magenta prefix for API, 92 = Green prefix for Worker
    api_thread = threading.Thread(target=read_stream, args=(api_process.stdout, "[Nila API]", "95"))
    worker_thread = threading.Thread(target=read_stream, args=(worker_process.stdout, "[Nila Worker]", "92"))
    
    api_thread.daemon = True
    worker_thread.daemon = True
    
    api_thread.start()
    worker_thread.start()
    
    cf_watcher_thread = threading.Thread(target=watch_cloudflare_tunnel)
    cf_watcher_thread.daemon = True
    cf_watcher_thread.start()
    
    print(f"\n{GREEN}✔ NILA services are now online and monitoring.{RESET}")
    print(f"{RED}Press Ctrl+C to terminate all services.{RESET}\n")
    
    try:
        while True:
            # Monitor if any process crashes/terminates
            if api_process.poll() is not None:
                print(f"\n{RED}[Nila] API Server stopped unexpectedly (Exit code: {api_process.returncode}){RESET}")
                break
            if worker_process.poll() is not None:
                print(f"\n{RED}[Nila] Huey Worker stopped unexpectedly (Exit code: {worker_process.returncode}){RESET}")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[Nila] Interrupt received. Shutting down NILA services...{RESET}")
    finally:
        # Gracefully terminate child processes
        api_process.terminate()
        worker_process.terminate()
        
        # Give them a few seconds to clean up, otherwise force kill
        try:
            api_process.wait(timeout=3)
            worker_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            print(f"{RED}[Nila] Processes timed out during termination. Forcing kill...{RESET}")
            api_process.kill()
            worker_process.kill()
            
        print(f"{GREEN}[Nila] All services stopped successfully.{RESET}")

if __name__ == "__main__":
    main()
