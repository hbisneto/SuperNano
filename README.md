# SuperNanno

> Nano, but modern. With UI, syntax highlighting, and a real developer workflow

A modern terminal-based text editor inspired by nano.

SuperNanno combines simplicity with powerful editing features, providing a clean and efficient editing experience directly in your terminal.

---

## 🚀 Features

* 📝 Full text editing with cursor and selection support
* 📂 Open files via CLI, sidebar, or manual path input
* 💾 Save & Save As support
* 🔍 Search inside files (`CTRL + F`)
* 📥 Insert file into current document (`CTRL + R`)
* ♻️ Session restore (reopens last file automatically)
* ⚠️ Unsaved changes protection
* 🎨 Syntax highlighting (based on file type)
* 📊 Smart status bar (file name, language, encoding, state)
* 📁 Sidebar file explorer

---

## ⌨️ Keyboard Shortcuts

| Shortcut   | Action                |
| ---------- | --------------------- |
| `CTRL + O` | Open file             |
| `CTRL + R` | Insert file at cursor |
| `CTRL + S` | Save file             |
| `CTRL + N` | New file              |
| `CTRL + F` | Search                |
| `CTRL + Q` | Quit                  |

---

## 📦 Installation

Coming soon via PyPI:

```bash
pip install supernanno
```

---

## ▶️ Usage

```bash
supernanno file.txt
```

Or simply:

```bash
supernanno
```

---

## ⚙️ Session Restore

SuperNanno automatically restores your last opened file using a local configuration file:

```json
{
  "session": {
    "last_opened_file": "/path/to/file"
  }
}
```

---

## 🧠 Philosophy

SuperNanno is built with a simple idea:

> Be as simple as nano, but flexible enough to grow into a modern terminal editor.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📜 License

MIT License

---

## ⭐ Support

If you like this project, consider giving it a star on GitHub!
