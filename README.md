<div dir="rtl">

<h1 align="center">📂 Smart File Organizer — מארגן קבצים חכם</h1>

<p align="center">
  <strong>Smart File Organizer</strong> הוא כלי שולחני חכם לסידור קבצים אוטומטי לפי סוגים וקטגוריות.<br>
  כולל <strong>GUI מודרני (Light / Dark)</strong>, אפשרות <strong>CLI</strong>, Undo / Redo, טיפול בכפילויות<br>
  ומעקב בזמן אמת אחרי תיקיות באמצעות <code>watchdog</code>.
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

<h2 align="center">👀 חידושים בגרסה האחרונה</h2>

<table align="center">
  <thead>
    <tr>
      <th>פיצ'ר</th>
      <th>תיאור</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🎨 עיצוב מודרני</td>
      <td>שימוש ב־<strong>ttkbootstrap</strong> עם Themes מוכנים, מראה נקי ואחיד ללא צורך ב־CSS ידני</td>
    </tr>
    <tr>
      <td>🌗 Light / Dark Mode</td>
      <td>מעבר מיידי בין מצבים כולל שמירה אוטומטית ב־<code>organizer_settings.json</code></td>
    </tr>
    <tr>
      <td>🌓 כפתור מצב תצוגה</td>
      <td>שליטה מהירה במצב התאורה דרך כפתור ☀️ / 🌙 בראש הממשק</td>
    </tr>
    <tr>
      <td>💾 שמירת הגדרות</td>
      <td>טעינה ושמירה אוטומטית של תיקייה אחרונה, סינונים והעדפות משתמש</td>
    </tr>
    <tr>
      <td>🔄 Undo / Redo</td>
      <td>שחזור מלא של פעולות סידור על בסיס היסטוריה מתועדת</td>
    </tr>
    <tr>
      <td>🧠 טיפול בכפילויות</td>
      <td>זיהוי קבצים זהים והוספת אינדקסים <code>(1)</code>, <code>(2)</code> ללא דריסה</td>
    </tr>
    <tr>
      <td>👀 ניטור בזמן אמת</td>
      <td>מעקב אוטומטי אחר שינויים בתיקייה באמצעות <strong>watchdog</strong></td>
    </tr>
    <tr>
      <td>🧪 Dry-Run</td>
      <td>הצגת פעולות עתידיות לפני ביצוע בפועל לצורך בדיקה ובטיחות</td>
    </tr>
    <tr>
      <td>💻 CLI מתקדם</td>
      <td>הרצה משורת הפקודה עם flags מתקדמים וללא שימוש בממשק גרפי</td>
    </tr>
    <tr>
      <td>📝 לוגים</td>
      <td>רישום מלא של כל פעולות הסידור לצורכי בקרה ושחזור</td>
    </tr>
  </tbody>
</table>


<hr>

<h2 align="center">📁 מבנה הפרויקט</h2>

<table align="center">
  <thead>
    <tr>
      <th>קובץ / תיקייה</th>
      <th>תיאור</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>main.py</code></td>
      <td>נקודת הכניסה – GUI או CLI</td>
    </tr>
    <tr>
      <td><code>ui.py</code></td>
      <td>ממשק גרפי מודרני עם Light / Dark</td>
    </tr>
    <tr>
      <td><code>file_sorter.py</code></td>
      <td>לוגיקת הסידור, כפילויות, Undo / Redo</td>
    </tr>
    <tr>
      <td><code>logger.py</code></td>
      <td>רישום פעולות ללוג</td>
    </tr>
    <tr>
      <td><code>organizer_settings.json</code></td>
      <td>שמירת הגדרות ממשק</td>
    </tr>
    <tr>
      <td><code>.sort_history.json</code></td>
      <td>היסטוריית פעולות לסידור ושחזור</td>
    </tr>
  </tbody>
</table>

<hr>

<h2 align="center">🧠 פיצ'רים מרכזיים</h2>

<table align="center">
  <thead>
    <tr>
      <th>תחום</th>
      <th>תכונה</th>
      <th>סטטוס</th>
      <th>הערות</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>📂 סידור קבצים</td>
      <td>חלוקה אוטומטית לפי סוג</td>
      <td>✅</td>
      <td>תמונות, מסמכים, קוד, וידאו, שמע ועוד</td>
    </tr>
    <tr>
      <td>🧪 בטיחות</td>
      <td>Dry-Run</td>
      <td>✅</td>
      <td>בדיקה לפני הזזה בפועל</td>
    </tr>
    <tr>
      <td>🧠 כפילויות</td>
      <td>טיפול חכם בשמות זהים</td>
      <td>✅</td>
      <td>הוספת (1), (2) לפי צורך</td>
    </tr>
    <tr>
      <td>🔄 שחזור</td>
      <td>Undo / Redo</td>
      <td>✅</td>
      <td>שחזור מלא מהיסטוריה</td>
    </tr>
    <tr>
      <td>👀 ניטור</td>
      <td>מעקב תיקיות בזמן אמת</td>
      <td>✅</td>
      <td>באמצעות watchdog</td>
    </tr>
    <tr>
      <td>💻 CLI</td>
      <td>הרצה משורת הפקודה</td>
      <td>✅</td>
      <td>כולל flags מתקדמים</td>
    </tr>
    <tr>
      <td>🎨 ממשק</td>
      <td>Light / Dark Mode</td>
      <td>✅</td>
      <td>שמירה אוטומטית</td>
    </tr>
  </tbody>
</table>

<hr>

<h2 align="center">🗂️ קטגוריות קבצים</h2>

<table align="center">
  <thead>
    <tr>
      <th>קטגוריה</th>
      <th>אייקון</th>
      <th>סיומות</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Images</td><td>🖼️</td><td>.jpg, .png, .gif, .webp, .heic</td></tr>
    <tr><td>Documents</td><td>📄</td><td>.pdf, .docx, .txt</td></tr>
    <tr><td>Code</td><td>💻</td><td>.py, .js, .java, .cpp, .html</td></tr>
    <tr><td>Videos</td><td>🎥</td><td>.mp4, .mkv, .avi</td></tr>
    <tr><td>Audio</td><td>🎵</td><td>.mp3, .wav, .flac</td></tr>
    <tr><td>Archives</td><td>📦</td><td>.zip, .rar, .7z</td></tr>
    <tr><td>Others</td><td>❓</td><td>כל השאר</td></tr>
  </tbody>
</table>

<hr>

<h2 align="center">⚙️ התקנה והרצה</h2>

<table align="center">
  <tr>
    <td><strong>שלב 1</strong></td>
    <td><code>pip install ttkbootstrap Pillow watchdog</code></td>
  </tr>
  <tr>
    <td><strong>שלב 2</strong></td>
    <td><code>python main.py</code></td>
  </tr>
</table>

<h3>CLI</h3>

<div dir="ltr">

```bash
python main.py <folder> --no-gui [--dry-run] [--include-hidden] [--duplicates]
```

<hr>

<h2>⚠️ הערות חשובות</h2>

<ul>
  <li>מומלץ להתחיל ב־<strong>Dry-Run</strong></li>
  <li>קבצים שכבר בתיקיות היעד לא מוזזים</li>
  <li>ניתן להרחיב קטגוריות בקובץ <code>file_sorter.py</code></li>
</ul>

<hr>

<h2>📄 רישיון</h2>

<p>
  הפרויקט מופץ תחת רישיון <strong>MIT</strong> – חופשי לשימוש, שינוי והפצה עם קרדיט.
</p>

<hr>

<p align="center"><strong>👨‍💻 Raz Eini (2025)</strong></p>

</div>
