"""Windows desktop shell; the viewer and ESP32 code remain unmodified."""
import atexit
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))


def user_directory():
    base = Path(os.environ.get('LOCALAPPDATA', Path.home()/'.local'/'share'))
    path = base/'DualLidarS3'
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_layout(directory):
    """Seed a writable user copy without overwriting saved calibration."""
    target = directory/'layout.json'
    if not target.exists():
        shutil.copyfile(ROOT/'layout.json',target)
    return target


def child_command(port, baud, http_port, layout, ready):
    args = ['--viewer-server','--ready-file',str(ready),'--port',port,
            '--baud',str(baud),'--host','127.0.0.1','--viser-port',str(http_port),
            '--layout',str(layout),'--stop-file',str(ready.with_suffix('.stop')),
            '--parent-pid',str(os.getpid())]
    if getattr(sys,'frozen',False): return [sys.executable,*args]
    return [sys.executable,str(ROOT/'desktop.py'),*args]


def parent_alive(pid):
    if sys.platform=='win32':
        import ctypes
        from ctypes import wintypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        kernel.OpenProcess.restype=wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
        kernel.WaitForSingleObject.restype=wintypes.DWORD
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=kernel.OpenProcess(0x00100000,False,pid)
        if not handle:return False
        try:return kernel.WaitForSingleObject(handle,0)==0x102
        finally:kernel.CloseHandle(handle)
    try:os.kill(pid,0);return True
    except OSError:return False


def run_server():
    """Run the exact existing viewer with a parent-controlled lifetime."""
    import _thread
    args = sys.argv[1:]
    args.remove('--viewer-server')
    index = args.index('--ready-file')
    ready = Path(args[index+1])
    del args[index:index+2]
    index = args.index('--stop-file')
    stop_file = Path(args[index+1])
    del args[index:index+2]
    index = args.index('--parent-pid')
    parent_pid = int(args[index+1])
    del args[index:index+2]
    sys.argv = [sys.argv[0],*args]
    # PyInstaller windowed executables can set stdout/stderr to None.
    if sys.stdout is None:
        sys.stdout = (ready.parent/'viewer.log').open('a',encoding='utf-8',buffering=1)
    if sys.stderr is None: sys.stderr = sys.stdout
    from viewer.dual_serial import DualReader
    original_start = DualReader.start
    def start_with_ready(self):
        original_start(self)
        ready.write_text('ready',encoding='ascii')
    DualReader.start = start_with_ready
    def watch_parent():
        while not stop_file.exists() and parent_alive(parent_pid):
            time.sleep(.2)
        _thread.interrupt_main()
    threading.Thread(target=watch_parent,daemon=True).start()
    from viewer.dual_viewer import main
    main()


class DesktopController:
    def __init__(self, directory=None):
        self.directory = directory or user_directory()
        self.layout = ensure_layout(self.directory)
        self.process = None
        self.log = None
        self.lock = threading.RLock()
        self.closed = threading.Event()
        self.last_port = ''
        try:
            settings=json.loads((self.directory/'desktop.json').read_text())
            self.last_port=str(settings.get('port',''))
        except (OSError,ValueError,TypeError): pass

    def list_ports(self):
        from serial.tools import list_ports
        return {'ports':[{'device':p.device,'description':p.description}
                         for p in list_ports.comports()], 'last_port':self.last_port}

    def connect(self, port):
        if not isinstance(port,str) or not re.fullmatch(r'COM[1-9][0-9]*',port.strip(),re.I):
            return {'ok':False,'error':'COM portunu COM5 gibi yazin.'}
        port=port.strip().upper()
        with self.lock:
            if self.closed.is_set(): return {'ok':False,'error':'Uygulama kapatiliyor.'}
            if self.process and self.process.poll() is None:
                return {'ok':False,'error':'Baglanti zaten baslatildi. Pencereyi kapatip tekrar acin.'}
            # Use a free loopback port rather than colliding with a browser session on 8080.
            with socket.socket() as sock:
                sock.bind(('127.0.0.1',0))
                http_port=sock.getsockname()[1]
            ready=self.directory/'server.ready'
            ready.unlink(missing_ok=True)
            self.stop_file=ready.with_suffix('.stop')
            self.stop_file.unlink(missing_ok=True)
            if self.log: self.log.close()
            self.log=(self.directory/'viewer.log').open('w',encoding='utf-8')
            flags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0
            try:
                self.process=subprocess.Popen(
                    child_command(port,460800,http_port,self.layout,ready),
                    cwd=self.directory,stdin=subprocess.DEVNULL,
                    stdout=self.log,stderr=subprocess.STDOUT,text=True,
                    creationflags=flags)
            except OSError as exc:
                self.log.close();self.log=None
                return {'ok':False,'error':str(exc)}
            process=self.process
        url=f'http://127.0.0.1:{http_port}'
        deadline=time.monotonic()+45
        while time.monotonic()<deadline and not self.closed.is_set():
            if process.poll() is not None:
                return {'ok':False,'error':'Goruntuleyici acilamadi. Seri Monitoru kapatin, COM portunu kontrol edin. '
                        f'Ayrinti: {self.directory / "viewer.log"}'}
            if ready.exists():
                try:
                    with urllib.request.urlopen(url,timeout=.5) as response:
                        if response.status==200:
                            self.last_port=port
                            (self.directory/'desktop.json').write_text(json.dumps({'port':port}),encoding='utf-8')
                            return {'ok':True,'url':url}
                except (OSError,ValueError): pass
            self.closed.wait(.15)
        self._stop_process()
        return {'ok':False,'error':'Baslatma zaman asimina ugradi. viewer.log dosyasini kontrol edin.'}

    def _stop_process(self):
        with self.lock:
            if self.process:
                if self.process.poll() is None:
                    try:
                        self.stop_file.write_text('stop',encoding='ascii')
                        self.process.wait(timeout=4)
                    except (OSError,ValueError,subprocess.TimeoutExpired):
                        self.process.terminate()
                        try: self.process.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            self.process.kill();self.process.wait(timeout=2)
                self.process=None
            if self.log: self.log.close();self.log=None

    def close(self):
        self.closed.set()
        self._stop_process()


START_HTML = '''<!doctype html><html lang="tr"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dual LiDAR S3</title><style>
*{box-sizing:border-box}body{margin:0;background:#101820;color:#eaf1f5;font:16px system-ui;
min-height:100vh;display:grid;place-items:center}.panel{width:min(560px,92vw);padding:36px;
border:1px solid #354552;border-radius:16px;background:#192630}h1{margin-top:0;font-size:30px}
p{line-height:1.6;color:#b5c8d5}label{display:block;margin:18px 0 8px}
select,input,button{font:inherit;border-radius:8px;padding:12px;border:1px solid #506575}
select,input{background:#0e1922;color:white;width:100%}button{cursor:pointer;background:#2ec5d3;color:#071820;font-weight:700}
.row{display:flex;gap:12px;margin-top:20px}.row button:first-child{flex:1}.secondary{background:#263d4c;color:white}
#message{white-space:pre-wrap;min-height:48px;color:#ffd590}small{color:#94acbc}</style>
<main class="panel"><h1>Dual LiDAR S3</h1><p>2 × VL53L5CX + BNO085<br>Mevcut tarama arayuzunu masaustu penceresinde ac.</p>
<label for="ports">Bagli cihazlar</label><select id="ports" onchange="document.getElementById('port').value=this.value"></select>
<label for="port">ESP32 COM portu</label><input id="port" placeholder="COM5" autocomplete="off">
<p><small>Arduino Seri Monitoru kapali olmali. Haberlesme: 460800 baud.</small></p>
<div class="row"><button id="connect" onclick="connect()" disabled>Uygulamayi Ac</button>
<button class="secondary" onclick="refresh()">Yenile</button></div><p id="message"></p></main>
<script>
async function refresh(){try{const r=await pywebview.api.list_ports();const s=document.getElementById('ports');s.replaceChildren();
for(const p of r.ports){const o=document.createElement('option');o.value=p.device;o.textContent=p.device+' — '+p.description;s.append(o)}
const selected=r.ports.find(p=>p.device===r.last_port)||r.ports[0];
if(selected){s.value=selected.device;document.getElementById('port').value=selected.device}
else{document.getElementById('port').value=r.last_port;document.getElementById('message').textContent='Cihaz bulunamadi. ESP32 baglantisini kontrol edin.'}
}catch(e){document.getElementById('message').textContent=String(e)}}
async function connect(){const b=document.getElementById('connect');b.disabled=true;document.getElementById('message').textContent='Baslatiliyor...';
try{const r=await pywebview.api.connect(document.getElementById('port').value);if(r.ok){window.location.assign(r.url);return}
document.getElementById('message').textContent=r.error}catch(e){document.getElementById('message').textContent=String(e)}b.disabled=false}
window.addEventListener('pywebviewready',()=>{document.getElementById('connect').disabled=false;refresh()});
</script></html>'''


def main():
    if '--viewer-server' in sys.argv:
        run_server()
        return
    import webview
    controller=DesktopController()
    atexit.register(controller.close)
    webview.settings['ALLOW_DOWNLOADS']=True
    window=webview.create_window('Dual LiDAR S3',html=START_HTML,js_api=controller,
                                width=1440,height=940,min_size=(900,650))
    window.events.closed += controller.close
    try:
        webview.start(gui='edgechromium' if sys.platform=='win32' else None,
                      private_mode=False,storage_path=str(controller.directory/'webview'))
    finally: controller.close()

if __name__=='__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    is_server = '--viewer-server' in sys.argv
    try: main()
    except Exception as exc:
        if is_server or sys.platform!='win32': raise
        import ctypes
        ctypes.windll.user32.MessageBoxW(None,
            'Uygulama acilamadi: '+str(exc)+'\n\nMicrosoft Edge WebView2 Runtime kurulu olmali.',
            'Dual LiDAR S3',0x10)
