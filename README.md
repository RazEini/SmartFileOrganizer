<h1 align="center">📂 Smart File Organizer</h1>

<p align="center">
  <strong>Smart File Organizer</strong> is a desktop tool for automatically sorting files by type and category. It includes a modern graphical interface (<strong>GUI</strong>) with <strong>Light / Dark Mode</strong> support, a command-line interface (<strong>CLI</strong>), real <strong>Undo / Redo</strong> based on recorded history, hash-based duplicate detection, and real-time folder monitoring using <code>watchdog</code>.
</p>

<br>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue" />
  <img src="https://img.shields.io/badge/Tkinter-GUI-lightgrey" />
  <img src="https://img.shields.io/badge/ttkbootstrap-Modern_UI-purple" />
  <img src="https://img.shields.io/badge/CLI-Supported-green" />
  <img src="https://img.shields.io/badge/Architecture-19_modules-orange" />
  <img src="https://img.shields.io/badge/Thread--Safe-Yes-brightgreen" />
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
      <td>🧩 Modular Architecture</td>
      <td>Rebuilt from one large file into <strong>19 focused modules</strong> (mixins), each owning a single concern — theme, sorting, preview, watchdog, settings, etc.</td>
    </tr>
    <tr>
      <td>🧵 Real Thread Safety</td>
      <td>Introduced a central, thread-safe update queue (<code>ui_queue_mixin.py</code>) so the sort worker, undo/redo workers, and the watchdog thread never touch Tkinter widgets directly — eliminating a real <code>RuntimeError: main thread is not in main loop</code> crash and silent progress-bar freezes.</td>
    </tr>
    <tr>
      <td>🎯 Correct Duplicate Routing</td>
      <td>Fixed a bug where a duplicate file could be moved to the <em>wrong</em> destination (a leftover path from a previous loop iteration) instead of its intended <code>Duplicates/&lt;category&gt;/</code> folder.</td>
    </tr>
    <tr>
      <td>♻️ True Idempotency</td>
      <td>Re-running Sort on an already-sorted folder now moves <strong>zero</strong> files. Previously it would re-shuffle <code>Others/</code> files with endless <code>(1)</code>, <code>(2)</code>... suffixes and nest <code>Duplicates/</code> folders inside themselves on every run.</td>
    </tr>
    <tr>
      <td>🖼️ Flicker-Free Live Preview</td>
      <td>The preview grid now reuses existing widgets (widget pooling) instead of destroying and rebuilding hundreds of them on every refresh.</td>
    </tr>
    <tr>
      <td>🌗 Light / Dark Mode</td>
      <td>Instant switching between modes, with automatic saving to <code>organizer_settings.json</code> and no more crash on repeated toggling.</td>
    </tr>
    <tr>
      <td>💾 Settings Persistence</td>
      <td>Automatic loading and saving of the last used folder, filters, and user preferences — tolerant of a corrupted settings file.</td>
    </tr>
    <tr>
      <td>🔄 Undo / Redo</td>
      <td>Full restoration of sorting actions based on a recorded history in <code>.sort_history.json</code>.</td>
    </tr>
    <tr>
      <td>🧠 Duplicate Handling</td>
      <td>Detects byte-identical files by <strong>SHA-256 content hash</strong> (not filename) and routes them into <code>Duplicates/&lt;category&gt;/</code>.</td>
    </tr>
    <tr>
      <td>👀 Real-Time Monitoring</td>
      <td>Automatically tracks folder changes using <strong>watchdog</strong>, paused during an active sort to avoid feedback loops.</td>
    </tr>
    <tr>
      <td>🧪 Dry-Run</td>
      <td>Preview upcoming actions before actually executing them, for testing and safety.</td>
    </tr>
    <tr>
      <td>💻 CLI Mode</td>
      <td>Run from the command line with <code>--no-gui</code>, no window required — for automation or scripting.</td>
    </tr>
    <tr>
      <td>📝 Logging</td>
      <td>Full logging of all sorting actions to <code>sorted_files_log.txt</code>, for auditing and recovery.</td>
    </tr>
  </tbody>
</table>

<hr>

<h2 align="center">📁 Project Structure</h2>

<table align="center">
  <thead>
    <tr>
      <th>File</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>main.py</code></td><td>Entry point. Launches the GUI, or runs headless via <code>--no-gui</code> for CLI use.</td></tr>
    <tr><td><code>app.py</code></td><td><code>SmartOrganizerApp</code> — composes every mixin below into the final application class.</td></tr>
    <tr><td><code>file_sorter.py</code></td><td>Core sorting logic: category detection, SHA-256 duplicate hashing, moving files, and the Undo/Redo history engine.</td></tr>
    <tr><td><code>theme_mixin.py</code></td><td>Dark/Light theme switching and all <code>ttk</code> style definitions.</td></tr>
    <tr><td><code>ui_mixin.py</code></td><td>Builds the entire window layout (header, folder picker, options, actions, stats, log, preview).</td></tr>
    <tr><td><code>folder_mixin.py</code></td><td>Browsing for and opening the target folder in the OS file explorer.</td></tr>
    <tr><td><code>sort_mixin.py</code></td><td>Runs the sort operation on a background thread.</td></tr>
    <tr><td><code>preview_mixin.py</code></td><td>The live thumbnail grid, using widget pooling to stay flicker-free.</td></tr>
    <tr><td><code>watchdog_mixin.py</code></td><td>Starts/stops live filesystem monitoring of the selected folder.</td></tr>
    <tr><td><code>undo_redo_mixin.py</code></td><td>Undo and Redo of the last sort operation.</td></tr>
    <tr><td><code>settings_mixin.py</code></td><td>JSON settings persistence (auto-save) and the Settings window.</td></tr>
    <tr><td><code>stats_progress_mixin.py</code></td><td>Updates the stat cards and the progress bar.</td></tr>
    <tr><td><code>log_mixin.py</code></td><td>Thread-safe activity-log queue and its display.</td></tr>
    <tr><td><code>ui_queue_mixin.py</code></td><td>★ The central thread-safe channel every background thread uses to request a UI update.</td></tr>
    <tr><td><code>colors.py</code></td><td>Dark/Light color palettes.</td></tr>
    <tr><td><code>icons.py</code></td><td>Generates file/folder thumbnail icons for the preview grid.</td></tr>
    <tr><td><code>tooltip.py</code></td><td>Hover tooltip widget.</td></tr>
    <tr><td><code>watchdog_handler.py</code></td><td><code>FileSystemEventHandler</code> used by the watchdog observer.</td></tr>
    <tr><td><code>logging_setup.py</code></td><td>Logger configuration and file paths (<code>LOG_FILE</code>, <code>SETTINGS_FILE</code>).</td></tr>
    <tr><td><code>organizer_settings.json</code></td><td><em>(generated)</em> User settings: theme, last folder, filters — loaded/saved automatically.</td></tr>
    <tr><td><code>.sort_history.json</code></td><td><em>(generated, inside the sorted folder)</em> Sort action history that powers Undo/Redo.</td></tr>
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
    <tr><td>📂 File Sorting</td><td>Automatic classification by type</td><td>✅</td><td>Images, documents, code, video, audio, and more</td></tr>
    <tr><td>🧪 Safety</td><td>Dry-Run</td><td>✅</td><td>Preview before actually moving files</td></tr>
    <tr><td>🧠 Duplicates</td><td>Content-hash detection</td><td>✅</td><td>SHA-256, routed into <code>Duplicates/&lt;category&gt;/</code></td></tr>
    <tr><td>🔄 Recovery</td><td>Undo / Redo</td><td>✅</td><td>Full restoration from history</td></tr>
    <tr><td>♻️ Repeatability</td><td>Idempotent re-sorting</td><td>✅</td><td>Re-running Sort moves 0 files on an already-sorted folder</td></tr>
    <tr><td>👀 Monitoring</td><td>Real-time folder tracking</td><td>✅</td><td>Powered by watchdog, thread-safe</td></tr>
    <tr><td>💻 CLI</td><td>Command-line execution</td><td>✅</td><td>Includes advanced flags</td></tr>
    <tr><td>🎨 Interface</td><td>Light / Dark Mode</td><td>✅</td><td>Automatically saved, crash-free toggling</td></tr>
    <tr><td>🧵 Concurrency</td><td>Thread-safe UI updates</td><td>✅</td><td>Central queue — no direct cross-thread Tk calls</td></tr>
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
    </tr>
  </thead>
  <tbody>
    <tr><td>Images</td><td>🖼️</td><td><code>.jpg .jpeg .png .gif .bmp .tiff .webp .heic</code></td></tr>
    <tr><td>Documents</td><td>📄</td><td><code>.pdf .docx .doc .txt .odt .rtf</code></td></tr>
    <tr><td>Code</td><td>💻</td><td><code>.py .java .cpp .c .h .js .html .css .ts .go .rb</code></td></tr>
    <tr><td>Videos</td><td>🎥</td><td><code>.mp4 .mkv .avi .mov .wmv .flv</code></td></tr>
    <tr><td>Audio</td><td>🎵</td><td><code>.mp3 .wav .aac .ogg .flac</code></td></tr>
    <tr><td>Archives</td><td>📦</td><td><code>.zip .rar .tar .gz .7z</code></td></tr>
    <tr><td>Spreadsheets</td><td>📊</td><td><code>.xls .xlsx .csv</code></td></tr>
    <tr><td>Presentations</td><td>📈</td><td><code>.ppt .pptx</code></td></tr>
    <tr><td>Others</td><td>❓</td><td>Any unrecognized extension</td></tr>
    <tr><td>Duplicates/&lt;category&gt;</td><td>🧬</td><td>Any file whose SHA-256 hash matches one already sorted</td></tr>
  </tbody>
</table>

<hr>

<div align="center">

## ⚙️ Installation & Setup

| Step | Action | Command |
| :---: | :--- | :--- |
| 1️⃣ | **Install dependencies** | `pip install ttkbootstrap Pillow watchdog` |
| 2️⃣ | **Run the interface** | `python main.py` |

---

### 🖥️ Using the Command-Line Interface (CLI)

Run the tool directly from the terminal for automation or headless (no-GUI) operation:

</div>

```bash
python main.py <folder> --no-gui [--dry-run] [--include-hidden] [--duplicates]
```

<hr>

<h2 align="center">🧵 Why Thread Safety Matters Here</h2>

<p align="center">Sorting has to run off the main thread so the window doesn't freeze — but Tkinter widgets, variables, and <code>root.after(...)</code> may only be touched from the <strong>main thread</strong>. Three background threads used to break that rule.</p>

<table align="center">
  <thead>
    <tr>
      <th>Background thread</th>
      <th>What it used to do wrong</th>
      <th>Fix</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Sort worker</td><td>Called <code>root.after(...)</code> and read Tkinter <code>Variable.get()</code> directly</td><td>Values captured on the main thread first; updates now go through <code>ui_queue</code></td></tr>
    <tr><td>Undo / Redo workers</td><td>Called <code>root.after(...)</code> directly to refresh stats/preview</td><td>Routed through <code>ui_queue</code></td></tr>
    <tr><td>Watchdog observer</td><td>Called <code>root.after(...)</code> / <code>after_cancel(...)</code> on every filesystem event</td><td>Routed through <code>ui_queue</code>; bursts of events are naturally coalesced into one refresh per poll</td></tr>
  </tbody>
</table>

<p align="center">All three now only push plain data into a <code>queue.Queue</code>. A single poller, scheduled exclusively via <code>root.after()</code> on the main thread, drains it and applies every update safely.</p>

<hr>

<h2>⚠️ Important Notes</h2>

<ul>
  <li>It's recommended to start with a <strong>Dry-Run</strong></li>
  <li>Files already sorted into their category folder (including <code>Others</code> and <code>Duplicates</code>) are skipped on the next run — re-sorting is safe and idempotent</li>
  <li>Categories can be extended in <code>file_sorter.py</code> → <code>FILE_CATEGORIES</code></li>
</ul>

<hr>

<h2>📄 License</h2>

<p>
  This project is distributed under the <strong>MIT</strong> license – free to use, modify, and distribute with credit.
</p>

<hr>

<p align="center"><strong>👨‍💻 Raz Eini (2025)</strong></p>
