# CV Builder

A simple, template-based CV/resume builder. Each CV design lives in its own folder as an HTML (Jinja2) template with a matching JSON data structure. Fill in your data, run one command, and get a print-ready **PDF** or a self-contained **HTML** file.

## Features

- **Multiple designs** — 3 ready-made A4 templates, each recreated from a reference image
- **Data-driven** — content is fully separated from design; edit JSON, not HTML
- **PDF & HTML output** — PDF via WeasyPrint, or a single self-contained HTML file (images embedded as base64)
- **Photo support** — use your own photo, or an automatic placeholder silhouette when none is set
- **Graceful fallbacks** — optional fields (LinkedIn, website, awards, education start dates…) simply disappear when left empty

## Project Structure

```
.
├── main.py                  # CLI entry point — controls the full operation
├── requirements.txt         # Python dependencies
├── venv/                    # Python virtual environment
├── resource/
│   ├── cv_image/            # Reference images the templates were built from
│   └── user_information.md  # Source user data (converted from PDF)
├── modern_navy_cv/          # Template 1: navy sidebar, rounded white panel
│   ├── cv.html              # Jinja2 HTML template (A4, print-ready CSS)
│   ├── data_stricture.json  # Required data fields, filled with dummy data
│   └── user_data.json       # Your data — same structure as data_stricture.json
├── elegant_gold_cv/         # Template 2: dark teal with gold ribbon accents
│   ├── cv.html
│   ├── data_stricture.json
│   └── user_data.json
├── corporate_blue_cv/       # Template 3: blue header band, slate sidebar
│   ├── cv.html
│   ├── data_stricture.json
│   └── user_data.json
└── result/                  # Generated output (created automatically)
```

## Setup

Requires Python 3.8+. WeasyPrint also needs Pango/Cairo system libraries, which are preinstalled on most Linux desktops.

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Usage

```
python3 main.py <cv_folder> <target_file_path> <format>
```

| Argument | Description |
|---|---|
| `<cv_folder>` | Template folder containing `cv.html` and your `user_data.json` |
| `<target_file_path>` | Output path. The extension (`.pdf`/`.html`) is added automatically. If the path is an existing directory, the file is written inside it, named after the template folder. |
| `<format>` | `-p` for PDF, `-h` for HTML |

Examples (use `./venv/bin/python`, or activate the venv first with `source venv/bin/activate`):

```bash
# PDF -> ./result.pdf (or ./result/modern_navy_cv.pdf if ./result is a directory)
./venv/bin/python main.py ./modern_navy_cv ./result -p

# Self-contained HTML -> ./my_cv.html
./venv/bin/python main.py ./elegant_gold_cv ./my_cv -h
```

If `user_data.json` is missing, the builder falls back to the template's dummy `data_stricture.json` (with a warning) — handy for previewing a design.

## Filling In Your Data

1. Pick a template folder.
2. Copy its `data_stricture.json` to `user_data.json` (if not already there).
3. Edit `user_data.json` with your details, **keeping the exact same structure** — same keys, same nesting; list items can be added or removed freely.
4. Optional fields (e.g. `linkedin`, `website`, `honors_awards`, education `start_date`) can be left as `""` or `[]` and won't be rendered.

### Adding a Photo

Put an image file inside the template folder and reference it by relative path:

```json
"photo": "my_photo.jpg"
```

Leave it as `""` to get a neutral placeholder silhouette. In HTML output the photo is embedded into the file itself, so the result is portable.

## Templates

| Folder | Design | Reference |
|---|---|---|
| `modern_navy_cv` | Dark navy sidebar (contact, skills, languages, hobbies) beside a rounded white panel with profile, experience and education | `resource/cv_image/cv_img_1.webp` |
| `elegant_gold_cv` | Dark teal header and sidebar with a gold ribbon divider, gold pill section headers | `resource/cv_image/cv_img_2.webp` |
| `corporate_blue_cv` | Blue header band with photo, slate personal-info sidebar, light content column with ruled section headings | `resource/cv_image/cv_img_3.png` |

All templates are sized for a single A4 page with the provided amount of content; if you add much more text, the page flows onto a second sheet.

## Adding a New Template

1. Create a new folder in the project root, e.g. `my_new_cv/`.
2. Add a `cv.html` — a Jinja2 template with inline CSS. Use `@page { size: A4; margin: 0; }` and millimetre units for reliable PDF layout.
3. Add a `data_stricture.json` describing every field the template uses, filled with dummy data.
4. Add your `user_data.json` and build it like any other template:

```bash
./venv/bin/python main.py ./my_new_cv ./result -p
```

## Dependencies

- [Jinja2](https://jinja.palletsprojects.com/) — HTML templating
- [WeasyPrint](https://weasyprint.org/) — HTML → PDF rendering
