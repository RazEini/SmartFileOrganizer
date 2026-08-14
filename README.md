<h1 align="center">📂 Smart File Organizer</h1>

<p align="center">
  <strong>Smart File Organizer</strong> is a smart desktop tool for automatically sorting files by type and category. It includes a modern graphical interface (<strong>GUI</strong>) with <strong>Light / Dark Mode</strong> support, a command-line interface (<strong>CLI</strong>), <strong>Undo / Redo</strong> functionality, duplicate file handling, and real-time folder monitoring using <code>watchdog</code>.
</p>

<br>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue" />
  <img src="https://img.shields.io/badge/Tkinter-GUI-lightgrey" />
  <img src="https://img.shields.io/badge/ttkbootstrap-Modern_UI-purple" />
  <img src="https://img.shields.io/badge/CLI-Supported-green" />
  <img src="https://img.shields.io/badge/License-MIT-blue" />
</p>

<br/>
<hr>

<h2 align="center">🔍 What's New in the Latest Version</h2>

<table align="center">
  <thead>
    <tr>
      <th>Feature</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🎨 Modern Design</td>
      <td>Built with <strong>ttkbootstrap</strong> using ready-made themes for a clean, consistent look with no manual CSS required</td>
    </tr>
    <tr>
      <td>🌗 Light / Dark Mode</td>
      <td>Instant switching between modes, with automatic saving to <code>organizer_settings.json</code></td>
    </tr>
    <tr>
      <td>🌓 Theme Toggle Button</td>
      <td>Quick control over the display mode via a ☀️ / 🌙 button at the top of the interface</td>
    </tr>
    <tr>
      <td>💾 Settings Persistence</td>
      <td>Automatic loading and saving of the last used folder, filters, and user preferences</td>
    </tr>
    <tr>
      <td>🔄 Undo / Redo</td>
      <td>Full restoration of sorting actions based on a recorded history</td>
    </tr>
    <tr>
      <td>🧠 Duplicate Handling</td>
      <td>Detects identical files and adds indices <code>(1)</code>, <code>(2)</code> without overwriting</td>
    </tr>
    <tr>
      <td>👀 Real-Time Monitoring</td>
      <td>Automatically tracks folder changes using <strong>watchdog</strong></td>
    </tr>
    <tr>
      <td>🧪 Dry-Run</td>
      <td>Preview upcoming actions before actually executing them, for testing and safety</td>
    </tr>
    <tr>
      <td>💻 Advanced CLI</td>
      <td>Run from the command line with advanced flags, no GUI required</td>
    </tr>
    <tr>
      <td>📝 Logging</td>
      <td>Full logging of all sorting actions for auditing and recovery purposes</td>
    </tr>
  </tbody>
</table>

<hr>

<h2 align="center">📁 Project Structure</h2>

<table align="center">
  <thead>
    <tr>
      <th>File / Folder</th>
      <th>Extended Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>main.py</code></td>
      <td>The program's entry point. Manages the program flow, loads settings, and allows launching via GUI or CLI.</td>
    </tr>
    <tr>
      <td><code>ui.py</code></td>
      <td>Modern graphical interface with Light / Dark Mode. Handles windows, buttons, menus, and dialogs, and integrates with the sorting operations in <code>file_sorter.py</code>.</td>
    </tr>
    <tr>
      <td><code>file_sorter.py</code></td>
      <td>Core sorting logic: file type detection, duplicate handling, moving files into categories, Undo / Redo, and Dry-Run support.</td>
    </tr>
    <tr>
      <td><code>logger.py</code></td>
      <td>Logging module. Stores a history of user actions, errors, and alerts for tracking and recovery purposes.</td>
    </tr>
    <tr>
      <td><code>organizer_settings.json</code></td>
      <td>User settings file: color mode (Light/Dark), last used folder, filters, and additional preferences. Loaded and saved automatically.</td>
    </tr>
    <tr>
      <td><code>.sort_history.json</code></td>
      <td>Sorting action history file. Enables Undo / Redo and full restoration of changes made to files.</td>
    </tr>
  </tbody>
</table>

<hr>

<h2 align="center">🧠 Key Features</h2>

<table align="center">
  <thead>
    <tr>
      <th>Area</th>
      <th>Feature</th>
      <th>Status</th>
      <th>Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>📂 File Sorting</td>
      <td>Automatic classification by type</td>
      <td>✅</td>
      <td>Images, documents, code, video, audio, and more</td>
    </tr>
    <tr>
      <td>🧪 Safety</td>
      <td>Dry-Run</td>
      <td>✅</td>
      <td>Preview before actually moving files</td>
    </tr>
    <tr>
      <td>🧠 Duplicates</td>
      <td>Smart handling of identical names</td>
      <td>✅</td>
      <td>Adds (1), (2) as needed</td>
    </tr>
    <tr>
      <td>🔄 Recovery</td>
      <td>Undo / Redo</td>
      <td>✅</td>
      <td>Full restoration from history</td>
    </tr>
    <tr>
      <td>👀 Monitoring</td>
      <td>Real-time folder tracking</td>
      <td>✅</td>
      <td>Powered by watchdog</td>
    </tr>
    <tr>
      <td>💻 CLI</td>
      <td>Command-line execution</td>
      <td>✅</td>
      <td>Includes advanced flags</td>
    </tr>
    <tr>
      <td>🎨 Interface</td>
      <td>Light / Dark Mode</td>
      <td>✅</td>
      <td>Automatically saved</td>
    </tr>
  </tbody>
</table>

<hr>

<h2 align="center">🗂️ File Categories</h2>

<table align="center">
  <thead>
    <tr>
      <th>Category</th>
      <th>Icon</th>
      <th>Supported Extensions</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Images</td>
      <td>🖼️</td>
      <td>.jpg, .jpeg, .png, .gif, .bmp, .webp, .heic</td>
      <td>Image and graphic files, including common and advanced formats</td>
    </tr>
    <tr>
      <td>Documents</td>
      <td>📄</td>
      <td>.pdf, .docx, .doc, .txt, .odt, .rtf</td>
      <td>Documents, text files, and Office files</td>
    </tr>
    <tr>
      <td>Code</td>
      <td>💻</td>
      <td>.py, .js, .ts, .java, .cpp, .c, .html, .css</td>
      <td>Source code and development files</td>
    </tr>
    <tr>
      <td>Videos</td>
      <td>🎥</td>
      <td>.mp4, .mkv, .avi, .mov, .flv</td>
      <td>Video files in common formats</td>
    </tr>
    <tr>
      <td>Audio</td>
      <td>🎵</td>
      <td>.mp3, .wav, .aac, .ogg, .flac</td>
      <td>Audio and music files</td>
    </tr>
    <tr>
      <td>Archives</td>
      <td>📦</td>
      <td>.zip, .rar, .7z, .tar, .gz</td>
      <td>Archive and compressed files</td>
    </tr>
    <tr>
      <td>Spreadsheets</td>
      <td>📊</td>
      <td>.xls, .xlsx, .csv</td>
      <td>Data spreadsheets and tables</td>
    </tr>
    <tr>
      <td>Presentations</td>
      <td>📈</td>
      <td>.ppt, .pptx</td>
      <td>Presentations and slide files</td>
    </tr>
    <tr>
      <td>Others</td>
      <td>❓</td>
      <td>Any unrecognized extension</td>
      <td>Files that were not assigned to another category</td>
    </tr>
  </tbody>
</table>

<hr>

<div align="center">

## ⚙️ Installation & Setup

Set up the environment and launch the project in a few simple steps:

| Step | Action | Command |
| :---: | :--- | :--- |
| 1️⃣ | **Install dependencies** | `pip install ttkbootstrap Pillow watchdog` |
| 2️⃣ | **Run the interface** | `python main.py` |

---

### 🖥️ Using the Command-Line Interface (CLI)

You can run the tool directly from the terminal for automation or headless (no-GUI) operation:

</div>

```bash
python main.py <folder> --no-gui [--dry-run] [--include-hidden] [--duplicates]
```

<hr>

<h2>⚠️ Important Notes</h2>

<ul>
  <li>It's recommended to start with a <strong>Dry-Run</strong></li>
  <li>Files already in their target folders are not moved</li>
  <li>Categories can be extended in the <code>file_sorter.py</code> file</li>
</ul>

<hr>

<h2>📄 License</h2>

<p>
  This project is distributed under the <strong>MIT</strong> license – free to use, modify, and distribute with credit.
</p>

<hr>

<p align="center"><strong>👨‍💻 Raz Eini (2025)</strong></p>
