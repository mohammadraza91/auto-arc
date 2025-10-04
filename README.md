## Auto ARC – DXF Generator (Streamlit)

### What it does
- Prompt Google Gemini with natural-language floor plan requirements.
- Gemini returns Python code that uses `ezdxf` to create a DXF.
- The app runs the code, renders a preview image, and lets you download the DXF (and all outputs as ZIP).
- On Windows, you can attempt to open the latest DXF directly in AutoCAD.

### Prerequisites
- Python 3.10+
- A Google Gemini API key
  - Create one in Google AI Studio and set it as an environment variable `GOOGLE_API_KEY` or paste it in the app sidebar.

### Install
```bash
cd "auto arc"
python -m pip install -r requirements.txt
```

### Run
```bash
cd "auto arc"
streamlit run streamlit_app.py
```
Then open the URL it prints (usually `http://localhost:8501`).

### Usage
1. Enter your Gemini API key in the sidebar (or set `GOOGLE_API_KEY`).
2. Describe your floor plan (e.g., plot size, setbacks, rooms).
3. Click "Generate DXF with Gemini". The generated Python appears; the DXF is saved as `plan.dxf` inside `auto arc/work_dir`.
4. Scroll down to preview and download.
5. Optional (Windows): Click "Open latest DXF in AutoCAD" if AutoCAD is installed and associated with `.dxf`.

### Notes
- The preview uses `ezdxf.addons.drawing` with Matplotlib. Not all DXF features are supported visually, but common entities render well.
- If Gemini outputs invalid code, check the error shown and try rephrasing or simplifying your prompt.
