<h1 align= "right">📂 Smart File Organizer – מארגן הקבצים החכם</h1>

<p>כלי לדסקטופ שמסדר קבצים לפי סוגים לתיקיות מתאימות, עם ממשק GUI וגם אפשרות להרצה דרך CLI.  
נבנה בפייתון 3.9+ עם Tkinter בלבד, ללא צורך בהתקנות נוספות.</p>

<hr/>

<h2>📁 קבצים בפרויקט</h2>
<ul>
  <li><code>main.py</code> – נקודת כניסה; מריץ GUI או CLI בהתאם לארגומנטים.</li>
  <li><code>file_sorter.py</code> – לוגיקה לסידור קבצים, כולל:
    <ul>
      <li>סידור לפי קטגוריות (תמונות, מסמכים, קוד, וידאו וכו')</li>
      <li>שמירה על מבנה התיקיות המקורי</li>
      <li>מצב Dry-run להצגה מה יוזז בלי לבצע שינויים</li>
      <li>טיפול בעותקים כפולים</li>
      <li>Undo / Redo עם שמירת היסטוריה (<code>.sort_history.json</code>)</li>
    </ul>
  </li>
  <li><code>ui.py</code> – ממשק Tkinter:
    <ul>
      <li>בחירת תיקייה</li>
      <li>אפשרויות: preserve structure, dry-run, include hidden, detect duplicates</li>
      <li>סינון לפי סיומות (<code>.png,.jpg,.pdf</code> וכו')</li>
      <li>כפתורים ל־Undo, Redo, Clear Log, Save Settings</li>
      <li>תצוגת סטטוס ולוג עם פרוגרס בר</li>
    </ul>
  </li>
  <li><code>logger.py</code> – Logger שמייצר קובץ <code>sorted_files_log.txt</code> ומדפיס למסך</li>
</ul>

<hr/>

<h2>⚙️ תכונות עיקריות</h2>
<ul>
  <li>סידור קבצים לפי סוג (Images, Documents, Code, Videos, Audio, Archives, Spreadsheets, Presentations, Others)</li>
  <li>שמירה על מבנה תיקיות מקורי</li>
  <li>Dry-run להצגת פעולות ללא שינוי בפועל</li>
  <li>טיפול בקבצים כפולים (מוסיף "(1)" אם שם קובץ קיים)</li>
  <li>Undo / Redo לפעולות סידור</li>
  <li>אפשרות סינון לפי סיומות קבצים בלבד</li>
  <li>שמירת לוג של כל הקבצים שהוזזו ב־<code>sorted_files_log.txt</code></li>
  <li>שמירת הגדרות GUI (<code>organizer_settings.json</code>)</li>
</ul>

<hr/>

<h2>🗂️ קטגוריות קבצים וסיומות</h2>
<table>
  <thead>
    <tr>
      <th>קטגוריה</th>
      <th>אייקון</th>
      <th>סיומות</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Images</td>
      <td>🖼️</td>
      <td>.jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp, .heic</td>
    </tr>
    <tr>
      <td>Documents</td>
      <td>📄</td>
      <td>.pdf, .docx, .doc, .txt, .odt, .rtf</td>
    </tr>
    <tr>
      <td>Code</td>
      <td>💻</td>
      <td>.py, .java, .cpp, .c, .h, .js, .html, .css, .ts, .go, .rb</td>
    </tr>
    <tr>
      <td>Videos</td>
      <td>🎥</td>
      <td>.mp4, .mkv, .avi, .mov, .wmv, .flv</td>
    </tr>
    <tr>
      <td>Audio</td>
      <td>🎵</td>
      <td>.mp3, .wav, .aac, .ogg, .flac</td>
    </tr>
    <tr>
      <td>Archives</td>
      <td>📦</td>
      <td>.zip, .rar, .tar, .gz, .7z</td>
    </tr>
    <tr>
      <td>Spreadsheets</td>
      <td>📊</td>
      <td>.xls, .xlsx, .csv</td>
    </tr>
    <tr>
      <td>Presentations</td>
      <td>📈</td>
      <td>.ppt, .pptx</td>
    </tr>
    <tr>
      <td>Others</td>
      <td>❓</td>
      <td>כל קובץ שלא משתייך לקטגוריות האחרות</td>
    </tr>
  </tbody>
</table>

<hr/>

<h2>💻 דרישות</h2>
<ul>
  <li>Python 3.9 ומעלה</li>
  <li>Tkinter (מודול מובנה)</li>
  <li>מודולים מובנים בלבד – אין צורך בהתקנות נוספות</li>
</ul>

<hr/>

<h2>🚀 הפעלה</h2>

<h3>GUI (מומלץ)</h3>
<pre><code>python main.py</code></pre>
<ul>
  <li>בחר תיקייה, סמן אפשרויות ולחץ על <strong>Sort Files</strong></li>
  <li>ניתן להשתמש ב־Undo/Redo ושמור הגדרות</li>
</ul>

<h3>CLI</h3>
<pre><code>python main.py &lt;folder&gt; --no-gui [--dry-run] [--include-hidden] [--duplicates]</code></pre>
<ul>
  <li><code>&lt;folder&gt;</code> – תיקייה למיין</li>
  <li><code>--dry-run</code> – רק סימולציה, ללא שינוי</li>
  <li><code>--include-hidden</code> – לכלול קבצים מוסתרים</li>
  <li><code>--duplicates</code> – לחשב ולהעביר כפולים</li>
</ul>

<hr/>

<h2>⚠️ הערות</h2>
<ul>
  <li>תמיד כדאי להתחיל עם <strong>Dry-run</strong> כדי לראות מה יקרה לפני שינויים אמיתיים</li>
  <li>הממשלה לא מזיזה קבצים שכבר בתיקיות היעד</li>
  <li>ניתן לערוך את <code>FILE_CATEGORIES</code> ב־<code>file_sorter.py</code> כדי להוסיף או להסיר סוגי קבצים</li>
</ul>

<hr/>

<h4 align="center">👨‍💻 Raz Eini (2025)</h4>
