from flask import Flask, request, redirect, render_template_string, send_from_directory
import os, shutil
import zipfile
from flask import jsonify
from flask import session


app = Flask(__name__)
app.secret_key = "secret123"


BASE_DIR = os.getcwd()
TRASH = os.path.join(BASE_DIR, ".trash")
os.makedirs(TRASH, exist_ok=True)

def safe_path(path):
    full = os.path.abspath(path)
    if not full.startswith(BASE_DIR):
        return BASE_DIR
    return full

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>cPanel File Manager</title>

<script src="https://cdn.tailwindcss.com"></script>

<style>
body { font-family: Arial; }
.toolbar button { margin-right:6px; }
</style>
</head>

<body class="bg-gray-200">

<div class="flex h-screen">

  <!-- Sidebar -->
  <div class="w-64 bg-gray-100 border-r overflow-auto">
    <div class="p-3 font-bold border-b bg-gray-200">📂 File Tree</div>
    <ul class="p-2 text-sm">
      <li><a href="/?path={{ base }}">🏠 Home</a></li>
      <li><a href="/?path={{ base }}">📁 Root</a></li>
    </ul>
  </div>

  <!-- Main -->
  <div class="flex-1 flex flex-col">

   <!-- Top Toolbar -->
<div class="bg-white border-b p-2 flex justify-between items-center">

  <!-- LEFT SIDE -->
  <div class="flex items-center gap-3 flex-wrap">

    <!-- NAVIGATION -->
    <div class="flex gap-1">
      <a href="/back" class="bg-gray-600 text-white px-3 py-1 rounded">⬅ Back</a>
      <a href="/forward" class="bg-gray-600 text-white px-3 py-1 rounded">➡ Forward</a>
      <a href="/?path={{ path }}" class="bg-blue-500 text-white px-3 py-1 rounded">🔄 Reload</a>
      <a href="/trash" class="bg-red-500 text-white px-3 py-1 rounded">🗑 Trash</a>
    </div>

    <!-- BULK ACTIONS -->
    <div class="flex gap-1 bg-gray-100 p-1 rounded">
      <button onclick="bulkDelete()" class="bg-red-500 text-white px-2 py-1 rounded">Delete</button>
      <button onclick="bulkDownload()" class="bg-green-500 text-white px-2 py-1 rounded">Download</button>
      <button onclick="bulkCompress()" class="bg-blue-500 text-white px-2 py-1 rounded">Compress</button>
    </div>

    <!-- FILE ACTIONS -->
    <div class="flex items-center gap-1">

      <!-- Upload -->
      <form action="/upload" method="post" enctype="multipart/form-data" class="flex items-center gap-1">
        <input type="file" name="file" class="text-sm">
        <input type="hidden" name="path" value="{{ path }}">
        <button class="bg-blue-500 text-white px-2 py-1 rounded">Upload</button>
      </form>

      <!-- New File -->
      <form action="/new_file" method="post" class="flex items-center gap-1">
        <input name="name" placeholder="File" class="border px-1 text-sm">
        <input type="hidden" name="path" value="{{ path }}">
        <button class="bg-green-500 text-white px-2 py-1 rounded">+ File</button>
      </form>

      <!-- New Folder -->
      <form action="/new_folder" method="post" class="flex items-center gap-1">
        <input name="name" placeholder="Folder" class="border px-1 text-sm">
        <input type="hidden" name="path" value="{{ path }}">
        <button class="bg-yellow-500 text-white px-2 py-1 rounded">+ Folder</button>
      </form>

    </div>

  </div>

  <!-- RIGHT SIDE (SEARCH) -->
  <div>
    <form method="get" class="flex items-center gap-2">
      <input type="hidden" name="path" value="{{ path }}">
      <input name="search" placeholder="🔍 Search..." class="border px-2 py-1 rounded">
      <button class="bg-gray-700 text-white px-2 py-1 rounded">Go</button>
    </form>
  </div>

</div>

    <!-- Breadcrumb -->
    <div class="bg-gray-300 px-3 py-1 text-sm">
      📍 {{ path }}
    </div>

    <!-- File Table -->
    <div class="flex-1 overflow-auto">

      <table class="w-full text-sm">
        <thead class="bg-gray-300">
            <tr>
              <th><input type="checkbox" onclick="toggleAll(this)"></th>
              <th>Name</th>
              <th>Size</th>
              <th>Type</th>
              <th>Perm</th>

              <th>Actions</th>
            </tr>
        </thead>

        <tbody class="bg-white">

        {% for f in files %}
        <tr class="border-b hover:bg-gray-100">
        <td>
              <input type="checkbox" class="file-check" value="{{ f.path }}">
          </td>
 

          <td class="p-2">
            {% if f.is_dir %}
              📁 <a href="/?path={{ f.path }}">{{ f.name }}</a>
            {% else %}
              📄 {{ f.name }}
            {% endif %}
          </td>

          <td class="text-center">{{ f.size }}</td>
          <td class="text-center">{{ f.type }}</td>

          <td class="text-center">
            0755
          </td>

          
          

          <td class="text-center">

            {% if not f.is_dir %}
              <a href="/edit?path={{ f.path }}" class="text-blue-600">Edit</a>
              <a href="/download?path={{ f.path }}" class="text-green-600 ml-2">Download</a>
            {% endif %}

            <a href="/delete?path={{ f.path }}" class="text-red-600 ml-2">Delete</a>

          </td>

        </tr>
        {% endfor %}

        </tbody>
      </table>

    </div>

  </div>
</div>


<script>
    function getSelected() {
      let selected = [];
      document.querySelectorAll(".file-check:checked").forEach(cb => {
        selected.push(cb.value);
      });
      return selected;
    }

    function toggleAll(master) {
      document.querySelectorAll(".file-check").forEach(cb => {
        cb.checked = master.checked;
      });
    }

    function bulkDelete() {
      let files = getSelected();
      if(files.length === 0) return alert("No files selected");

      fetch("/bulk_delete", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({files: files})
      }).then(() => location.reload());
    }

    function bulkCompress() {
      let files = getSelected();
      fetch("/bulk_compress", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({files: files})
      }).then(() => location.reload());
    }
    function bulkDownload() {
      let files = getSelected();

      fetch("/bulk_download", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({files})
      }).then(() => alert("ZIP created"));
    }
</script>

</body>
</html>
"""

@app.route("/")
def home():
    path = safe_path(request.args.get("path", BASE_DIR))
    search = request.args.get("search", "").lower()

    # HISTORY SYSTEM
    session.setdefault("history", [])
    session.setdefault("index", -1)

    if session["index"] == -1 or session["history"][session["index"]] != path:
        session["history"] = session["history"][:session["index"]+1]
        session["history"].append(path)
        session["index"] = len(session["history"]) - 1

    parent = os.path.dirname(path)

    files = []
    for f in os.listdir(path):
        if search and search not in f.lower():
            continue

        full = os.path.join(path, f)
        size = os.path.getsize(full) if os.path.isfile(full) else "-"

        files.append({
            "name": f,
            "path": full,
            "is_dir": os.path.isdir(full),
            "size": str(size) + " B" if size != "-" else "-",
            "type": "Folder" if os.path.isdir(full) else "File",
            "perm": oct(os.stat(full).st_mode)[-3:]
        })

    return render_template_string(
        HTML,
        files=files,
        path=path,
        base=BASE_DIR,
        parent=parent
    )

# -------- FILE ACTIONS --------
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    path = safe_path(request.form["path"])
    file.save(os.path.join(path, file.filename))
    return redirect(f"/?path={path}")

@app.route("/new_file", methods=["POST"])
def new_file():
    path = safe_path(request.form["path"])
    open(os.path.join(path, request.form["name"]), "w").close()
    return redirect(f"/?path={path}")

@app.route("/new_folder", methods=["POST"])
def new_folder():
    path = safe_path(request.form["path"])
    os.makedirs(os.path.join(path, request.form["name"]), exist_ok=True)
    return redirect(f"/?path={path}")

@app.route("/delete")
def delete():
    path = safe_path(request.args.get("path"))
    shutil.move(path, os.path.join(TRASH, os.path.basename(path)))
    return redirect(request.referrer)

@app.route("/trash")
def view_trash():
    files = os.listdir(TRASH)
    return "<br>".join(files) + "<br><a href='/'>Back</a>"
@app.route("/bulk_download", methods=["POST"])
def bulk_download():
    files = request.json["files"]
    zip_path = os.path.join(BASE_DIR, "download.zip")

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for f in files:
            f = safe_path(f)
            zipf.write(f, os.path.basename(f))

    return jsonify({"status": "ready"})

@app.route("/download")
def download():
    path = safe_path(request.args.get("path"))
    return send_from_directory(os.path.dirname(path), os.path.basename(path), as_attachment=True)

@app.route("/edit")
def edit():
    import json

    path = safe_path(request.args.get("path"))
    content = open(path, errors="ignore").read()

    # SAFE content for JS
    content_json = json.dumps(content)

    return f"""
<!DOCTYPE html>
<html>
<head>
<title>Editor</title>

<script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/loader.js"></script>

<style>
body {{ margin:0; }}
#editor {{ height:90vh; width:100%; }}

.topbar {{
    background:#1e1e1e;
    padding:10px;
    display:flex;
    justify-content:space-between;
}}

button {{
    background:#007acc;
    color:white;
    border:none;
    padding:8px 12px;
    cursor:pointer;
}}

#contextMenu {{
    position:absolute;
    background:white;
    box-shadow:0 0 10px rgba(0,0,0,0.3);
    padding:5px;
    display:none;
    z-index:1000;
}}

#contextMenu div {{
    padding:5px 10px;
    cursor:pointer;
}}

#contextMenu div:hover {{
    background:#eee;
}}
</style>
</head>

<body>

<!-- TOP BAR -->
<div class="topbar">
    <form method="post" action="/save">
        <input type="hidden" name="path" value="{path}">
        <input type="hidden" id="content" name="content">
        <button type="submit">💾 Save</button>
    </form>

    <a href="/" style="color:white;">⬅ Back</a>
</div>

<!-- EDITOR -->
<div id="editor"></div>

<!-- RIGHT CLICK MENU -->
<div id="contextMenu">
    <div onclick="saveFile()">💾 Save</div>
    <div onclick="copyText()">📋 Copy</div>
    <div onclick="pasteText()">📥 Paste</div>
</div>

<script>
require.config({{ paths: {{ vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' }} }});

let editor;

require(["vs/editor/editor.main"], function () {{

    editor = monaco.editor.create(document.getElementById('editor'), {{
        value: {content_json},
        language: "python",
        theme: "vs-dark",
        automaticLayout: true,
        fontSize: 14
    }});

    document.querySelector("form").onsubmit = function() {{
        document.getElementById("content").value = editor.getValue();
    }};
}});

// RIGHT CLICK MENU
document.addEventListener("contextmenu", function(e){{
    e.preventDefault();

    let menu = document.getElementById("contextMenu");
    menu.style.top = e.pageY + "px";
    menu.style.left = e.pageX + "px";
    menu.style.display = "block";
}});

document.addEventListener("click", function(){{
    document.getElementById("contextMenu").style.display = "none";
}});

// MENU FUNCTIONS
function saveFile(){{
    document.querySelector("form").submit();
}}

function copyText(){{
    navigator.clipboard.writeText(editor.getValue());
    alert("Copied!");
}}

function pasteText(){{
    navigator.clipboard.readText().then(text => {{
        editor.setValue(editor.getValue() + text);
    }});
}}
</script>

</body>
</html>
"""
@app.route("/compress")
def compress():
    path = safe_path(request.args.get("path"))
    zip_path = path + ".zip"

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    full = os.path.join(root, file)
                    zipf.write(full, os.path.relpath(full, path))
        else:
            zipf.write(path, os.path.basename(path))

    return redirect(request.referrer)
# @app.route("/rename", methods=["POST"])
# def rename():
#     old = safe_path(request.form["old"])
#     new = os.path.join(os.path.dirname(old), request.form["new"])

#     os.rename(old, new)
#     return redirect(request.referrer)

@app.route("/rename", methods=["POST"])
def rename():
    old = safe_path(request.form["old"])
    new = os.path.join(os.path.dirname(old), request.form["new"])

    os.rename(old, new)
    return redirect(request.referrer)

@app.route("/restore")
def restore():
    file = request.args.get("file")
    shutil.move(os.path.join(TRASH, file), BASE_DIR)
    return redirect("/")

@app.route("/move")
def move():
    src = safe_path(request.args.get("src"))
    dst = safe_path(request.args.get("dst"))

    shutil.move(src, dst)
    return redirect(request.referrer)

@app.route("/copy")
def copy():
    src = safe_path(request.args.get("src"))
    dst = safe_path(request.args.get("dst"))

    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(dst, os.path.basename(src)))
    else:
        shutil.copy2(src, dst)

    return redirect(request.referrer)

@app.route("/extract")
def extract():
    path = safe_path(request.args.get("path"))

    import zipfile
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(path))

    return redirect(request.referrer)


@app.route("/save", methods=["POST"])
def save():
    path = safe_path(request.form["path"])
    open(path, "w").write(request.form["content"])
    return redirect("/")

@app.route("/back")
def back():
    idx = session.get("index", 0)
    history = session.get("history", [])

    if idx > 0:
        idx -= 1
        session["index"] = idx

    return redirect(f"/?path={history[idx]}")

@app.route("/forward")
def forward():
    idx = session.get("index", 0)
    history = session.get("history", [])

    if idx < len(history) - 1:
        idx += 1
        session["index"] = idx

    return redirect(f"/?path={history[idx]}")

@app.route("/bulk_delete", methods=["POST"])
def bulk_delete():
    data = request.json["files"]

    for path in data:
        path = safe_path(path)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    return jsonify({"status": "ok"})

@app.route("/bulk_compress", methods=["POST"])
def bulk_compress():
    import zipfile
    data = request.json["files"]

    zip_path = os.path.join(BASE_DIR, "compressed.zip")

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in data:
            file = safe_path(file)
            zipf.write(file, os.path.basename(file))

    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)