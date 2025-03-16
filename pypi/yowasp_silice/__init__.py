import os
import sys
import yowasp_runtime
from . import silice_make
import requests
import tarfile
import http.server
import ssl
import subprocess
import shutil
import mimetypes

try:
    from importlib import resources as importlib_resources
    importlib_resources.files
except (ImportError, AttributeError):
    import importlib_resources

def run_silice(argv):
    print(argv)
    if "--frameworks_dir" in argv:
        cmd_argv = ["yowasp-silice", *argv]
    else:
        cmd_argv = ["yowasp-silice", "--framework","share/silice/frameworks/boards/icestick/icestick.v","--frameworks_dir","share/silice/frameworks/", *argv]
    return yowasp_runtime.run_wasm(__package__, "silice.wasm", resources=["share"], argv=cmd_argv)

def run_make(argv):
    silice_make.make(argv)

import os
import requests

def download_file(url, filename):
    if os.path.exists(filename):
        print(f"File '{filename}' already exists. Skipping download.")
        return 1
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get("content-length", 0))  # Get file size if available
        chunk_size = 1024  # 1 KB chunks
        downloaded = 0  # Track progress
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)
                downloaded += len(chunk)

                # Print progress bar
                if total_size > 0:  # Only show if size is known
                    percent = (downloaded / total_size) * 100
                    bar_length = 40  # Length of the progress bar
                    filled_length = int(bar_length * downloaded / total_size)
                    bar = "█" * filled_length + "-" * (bar_length - filled_length)
                    print(f"\r[{bar}] {percent:.2f}% ", end="", flush=True)
        return 1
    else:
        print(f"Failed to download {filename} from {url} (code: {response.status_code}).")
        return 0

def get_openFPGALoader():
    print("downloading openFPGALoader-online ...")
    url = "https://github.com/sylefeb/openFPGALoader-online/releases/download/bucket-linux-x64/release.tgz"
    download_file(url,"ofl.tgz")
    with tarfile.open("ofl.tgz", "r:gz") as tar:
        tar.extractall(".")

def generate_self_signed_cert(certfile='cert.pem', keyfile='key.pem'):
    subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-out', keyfile], check=True)
    subprocess.run(['openssl', 'req', '-new', '-key', keyfile, '-out', 'cert.csr', '-subj', '/CN=localhost'], check=True)
    subprocess.run(['openssl', 'x509', '-req', '-in', 'cert.csr', '-signkey', keyfile, '-out', certfile], check=True)
    os.remove('cert.csr')

def serve(html_content):
    class CustomHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                # Respond with the HTML content
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
            else:
                # Respond with the file content
                file_path = self.path.lstrip('/')
                if os.path.isfile(file_path):
                    content_type, _ = mimetypes.guess_type(file_path)
                    content_type = content_type or 'application/octet-stream'
                    try:
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                        self.send_response(200)
                        self.send_header('Content-type', content_type)
                        self.end_headers()
                        self.wfile.write(file_content)
                    except Exception as e:
                        self.send_error(500, f"Internal Server Error: {str(e)}")
    if False:
      # make certificates
      if not os.path.exists('cert.pem'):
        generate_self_signed_cert()
      # create localhost
      httpd = http.server.HTTPServer(('localhost', 4443), CustomHTTPRequestHandler)
      # wrap the server with SSL for HTTPS
      context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
      context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
      httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    else:
      httpd = http.server.HTTPServer(('localhost', 8000), CustomHTTPRequestHandler)
    # message
    print("\n\033[1;97m------=< openFPGALoader online >=------\033[0m")
    print("Serving openFPGALoader on \033[1;97mhttps://localhost:4443\033[0m")
    print("Open this URL with a broswer supporting WebUSB (e.g. Chrome)")
    print("This will let you configure your board directly.")
    print("\033[1;97mCtrl+C to exit\033[0m")
    print("Your browser will issue a warning regarding certificates.")
    httpd.serve_forever()

def serve_openFPGALoader(board,bitstream):
    get_openFPGALoader()
    html_page ="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <title>FPGA programming page</title>
      <style type="text/css">
      pre {
        margin: 0;
        font-family: monaco, "Courier New", Courier, monospace;
        line-height: 1.3;
        background: black;
        color: gray;
      }
      .button {
        background-color: #f0f0f0;
        border: none;
        color: black;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        border-radius: 8px;
      }
      .button:hover {
        background-color: #a9a9a9;
        color: white;
      }
    </style>
    </head>
    <body style="background-color: black;">
    <button class="button" id="selectAndProgramDevice">Click to select your FPGA device</button>
    <pre id="txtfield"></pre>

    <script type="module">
    import { AnsiUp } from 'https://cdn.jsdelivr.net/npm/ansi_up@6.0.2/ansi_up.min.js';
    window.ansiUp = new AnsiUp();
    </script>

    <script>
    var ansiText = "\\n\\033[1;97mIn progress ... please wait, the console is not refreshed during uploads...\\033[0m\\n\\n";
    var Module = {
      preRun: [function() {  }],
      'print': function(text)    {
        ansiText += text + "\\r\\n";
        niceText = window.ansiUp.ansi_to_html(ansiText);
        console.log(niceText);
        document.getElementById("txtfield").innerHTML = niceText;
        console.log(':: ' + text)
      },
      'printErr': function(text) {
        ansiText += text + "\\r\\n";
        niceText = window.ansiUp.ansi_to_html(ansiText);
        console.log(niceText);
        document.getElementById("txtfield").innerHTML = niceText;
        console.log(':: ' + text)
      }
    }
    Module['onRuntimeInitialized'] = function() {
      // download file
      var xhr = new XMLHttpRequest();
      xhr.open("GET", '""" + bitstream + """');
      xhr.responseType = "arraybuffer";
      xhr.overrideMimeType("application/octet-stream");
      xhr.onload = function () {
        if (this.status === 200) {
          FS.writeFile('/bitstream.bit', new Uint8Array(xhr.response), { encoding: "binary" });
          console.log("bitstream loaded")
        }
      };
      xhr.send();
    }
    function assert() {}
    </script>

    <script src=release/openFPGALoader.js></script>
    <script>
        // Request access to a USB device
        document.getElementById('selectAndProgramDevice').addEventListener('click', async () => {
          try {
            const device = await navigator.usb.requestDevice({ filters: [] });
            console.log(`Selected device: ${device.productName}`);
            Module.callMain(['-b','"""+board+"""','/bitstream.bit'])
          } catch (err) {
            console.error(`Error: ${err}`);
          }
        });
    </script>
    </body>
    </html>
    """
    serve(html_page)

def _run_silice_argv():
    sys.exit(run_silice(sys.argv[1:]))

def _run_make_argv():
    sys.exit(run_make(sys.argv[1:]))
