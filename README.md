<h1 align="center">📂 Smart File Organizer – מארגן הקבצים החכם</h1>

<p align="center">כלי שולחני חכם לסידור קבצים לפי סוגים לתיקיות מתאימות, עם ממשק גרפי מודרני (Light / Dark Mode) וגם אפשרות להרצה דרך שורת הפקודה (CLI).  
נבנה ב־<strong>Python 3.9+</strong> עם <code>Tkinter</code> ו־<code>ttkbootstrap</code> לעיצוב מודרני,  
עם תמיכה באפשרויות מתקדמות כמו <code>watchdog</code> (מעקב שינויים בזמן אמת) ו־<code>Pillow</code> (תמיכה באייקונים ותמונות).</p>
<br>
<hr/>

<h2>✨ חידושים בגרסה האחרונה</h2>
<ul>
  <li>🎨 עיצוב מודרני עם <code>ttkbootstrap</code></li>
  <li>🌗 תמיכה במצבים Light ו־Dark + שמירה אוטומטית ב־<code>settings.json</code></li>
  <li>🌓 כפתור מתחלף (☀️ / 🌙) בראש הממשק</li>
  <li>⚙️ אפשרות לשנות מצב גם דרך הגדרות GUI</li>
  <li>💾 שמירה וטעינה אוטומטית של כל ההגדרות האחרונות</li>
  <li>🔄 Undo / Redo חכם עם שחזור היסטוריית פעולות מלאה</li>
  <li>🧠 טיפול משופר בכפילויות (duplicates)</li>
  <li>👀 ניטור בזמן אמת לתיקייה (watchdog)</li>
</ul>

<hr/>

<h2>📁 מבנה הפרויקט</h2>
<ul>
  <li><code>main.py</code> – נקודת הכניסה הראשית (GUI או CLI)</li>
  <li><code>ui.py</code> – ממשק משתמש מודרני עם תמיכה במצבי תאורה</li>
  <li><code>file_sorter.py</code> – הלוגיקה לסידור, טיפול בכפילויות, Undo/Redo ועוד</li>
  <li><code>logger.py</code> – רישום לוגים לקובץ <code>sorted_files_log.txt</code></li>
  <li><code>organizer_settings.json</code> – שמירת הגדרות ממשק</li>
  <li><code>.sort_history.json</code> – ניהול היסטוריית פעולות לסידור</li>
</ul>

<hr/>

<h2>⚙️ תכונות עיקריות</h2>
<ul>
  <li>סידור קבצים לפי סוג (תמונות, מסמכים, קוד, וידאו, שמע, ארכיונים ועוד)</li>
  <li>שמירה על מבנה תיקיות מקורי</li>
  <li>Dry-run להצגת תוצאות בלי לבצע שינויים בפועל</li>
  <li>טיפול חכם בכפילויות – הוספת (1), (2) לפי הצורך</li>
  <li>Undo / Redo עם שחזור אוטומטי מהיסטוריה</li>
  <li>סינון לפי סיומות קבצים (למשל: <code>.png,.jpg,.pdf</code>)</li>
  <li>מעקב שינויים בתיקייה בזמן אמת (watchdog)</li>
  <li>שמירה של כל הפעולות בלוג (<code>sorted_files_log.txt</code>)</li>
  <li>שמירה אוטומטית של כל ההגדרות האחרונות בממשק</li>
  <li>אפשרות מעבר בין Light / Dark בלחיצה אחת או מתוך ההגדרות</li>
</ul>

<hr/>

<h2>🗂️ קטגוריות קבצים וסיומות</h2>

<table align="center">
  <thead>
    <tr>
      <th>קטגוריה</th>
      <th>אייקון</th>
      <th>סיומות</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Images</td><td>🖼️</td><td>.jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp, .heic</td></tr>
    <tr><td>Documents</td><td>📄</td><td>.pdf, .docx, .doc, .txt, .odt, .rtf</td></tr>
    <tr><td>Code</td><td>💻</td><td>.py, .java, .cpp, .c, .h, .js, .html, .css, .ts, .go, .rb</td></tr>
    <tr><td>Videos</td><td>🎥</td><td>.mp4, .mkv, .avi, .mov, .wmv, .flv</td></tr>
    <tr><td>Audio</td><td>🎵</td><td>.mp3, .wav, .aac, .ogg, .flac</td></tr>
    <tr><td>Archives</td><td>📦</td><td>.zip, .rar, .tar, .gz, .7z</td></tr>
    <tr><td>Spreadsheets</td><td>📊</td><td>.xls, .xlsx, .csv</td></tr>
    <tr><td>Presentations</td><td>📈</td><td>.ppt, .pptx</td></tr>
    <tr><td>Others</td><td>❓</td><td>כל קובץ שלא משתייך לקטגוריות אחרות</td></tr>
  </tbody>
</table>

<hr/>

<h2>💻 דרישות</h2>
<ul>
  <li>Python 3.9 ומעלה</li>
  <li>Tkinter (מובנה כבר בפייתון)</li>
  <li><code>pip install ttkbootstrap Pillow watchdog</code></li>
</ul>

<hr/>

<h2>🚀 הפעלה</h2>

<h3>🖥️ GUI (מומלץ)</h3>
<pre><code>python main.py</code></pre>
<ul>
  <li>בחר תיקייה, סמן אפשרויות ולחץ על <strong>Sort Files</strong></li>
  <li>החלף בין Light ו־Dark בלחיצה על ☀️ / 🌙</li>
  <li>כל ההגדרות נשמרות אוטומטית להפעלה הבאה</li>
</ul>

<h3>💻 CLI</h3>
<pre><code>python main.py &lt;folder&gt; --no-gui [--dry-run] [--include-hidden] [--duplicates]</code></pre>
<ul>
  <li><code>&lt;folder&gt;</code> – נתיב לתיקייה</li>
  <li><code>--dry-run</code> – סימולציה בלבד</li>
  <li><code>--include-hidden</code> – לכלול קבצים מוסתרים</li>
  <li><code>--duplicates</code> – לזהות ולהעביר כפולים</li>
</ul>

<hr/>

<h2>⚠️ הערות</h2>
<ul>
  <li>מומלץ להתחיל עם <strong>Dry-run</strong> לפני הרצה אמיתית</li>
  <li>האפליקציה לא מזיזה קבצים שכבר בתיקיות היעד</li>
  <li>ניתן לערוך את <code>FILE_CATEGORIES</code> ב־<code>file_sorter.py</code> להוספה או שינוי סוגי קבצים</li>
</ul>

<hr/>

<h4 align="center">👨‍💻 Raz Eini (2025)</h4>
