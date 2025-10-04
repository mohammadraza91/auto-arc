import os
import io
import re
import sys
import time
import json
import shutil
import base64
import zipfile
import tempfile
import subprocess
from pathlib import Path

# --- Auto-install missing dependency ---
def install_and_import(package, import_name=None):
    try:
        if import_name is None:
            import_name = package
        __import__(import_name)
    except ImportError:
        print(f"⚠️ {package} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        __import__(import_name)

# Ensure google-generativeai is installed
install_and_import("google-generativeai", "google.generativeai")

import streamlit as st

# Optional imports; loaded lazily when needed for preview
# import ezdxf
# import matplotlib.pyplot as plt

APP_TITLE = "Auto ARC – DXF Generator"
WORK_DIR = Path(__file__).parent / "work_dir"
WORK_DIR.mkdir(parents=True, exist_ok=True)

# WARNING: Hardcoding API keys is insecure. Prefer environment variables.
DEFAULT_GEMINI_API_KEY = "AIzaSyCvHn6Jib9sKslQH3020xdDgdML7RJKRWw"

# Preferred and fallback model names to try in order
MODEL_CANDIDATES = [
	"gemini-2.5-flash",
	"gemini-2.0-flash-exp",
	"gemini-1.5-flash-latest",
	"gemini-1.5-flash",
	"gemini-1.5-pro-latest",
	"gemini-1.5-pro",
]


def get_api_key() -> str:
	# Priority: sidebar input > env var > hardcoded default
	key = st.session_state.get("gemini_api_key") or os.getenv("GOOGLE_API_KEY", "") or DEFAULT_GEMINI_API_KEY
	return key.strip()


def configure_gemini(api_key: str):
	import google.generativeai as genai
	genai.configure(api_key=api_key)
	return genai


def extract_python_code(text: str) -> str:
	# Extract the first fenced Python code block
	pattern = r"```(?:python)?\n([\s\S]*?)```"
	m = re.search(pattern, text, flags=re.IGNORECASE)
	if m:
		return m.group(1).strip()
	return text.strip()


def write_user_code(code: str, filename: str = "generated_plan.py") -> Path:
	path = WORK_DIR / filename
	path.write_text(code, encoding="utf-8")
	return path


def run_python_file(pyfile: Path, timeout_sec: int = 60) -> subprocess.CompletedProcess:
	env = os.environ.copy()
	cmd = [sys.executable, str(pyfile.resolve())]
	return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout_sec, text=True)


def find_outputs(suffixes=(".dxf", ".png", ".svg")):
	files = []
	for p in WORK_DIR.iterdir():
		if p.is_file() and p.suffix.lower() in suffixes:
			files.append(p)
	return sorted(files)


def preview_dxf_image(dxf_path: Path, dpi: int = 120) -> bytes:
	import ezdxf
	import matplotlib
	matplotlib.use("Agg")
	import matplotlib.pyplot as plt
	from ezdxf.addons.drawing import RenderContext, Frontend
	from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

	doc = ezdxf.readfile(str(dxf_path))
	msp = doc.modelspace()

	fig = plt.figure(figsize=(6, 6), dpi=dpi)
	ax = fig.add_axes([0, 0, 1, 1])
	ctx = RenderContext(doc)
	out = MatplotlibBackend(ax)
	Frontend(ctx, out).draw_layout(msp, finalize=True)

	buf = io.BytesIO()
	fig.savefig(buf, format="png", dpi=dpi)
	plt.close(fig)
	buf.seek(0)
	return buf.read()


def zip_work_dir() -> bytes:
	buf = io.BytesIO()
	with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
		for p in WORK_DIR.iterdir():
			if p.is_file():
				zf.write(p, arcname=p.name)
	buf.seek(0)
	return buf.read()


def default_system_instruction() -> str:
	return (
		"You are an expert Python CAD assistant. Generate a single self-contained Python script "
		"that uses the ezdxf library to create a DXF floor plan according to the user's prompt. "
		"Requirements: (1) Use feet as drawing units and consistent coordinates. (2) Include plot outline, "
		"setbacks, labeled rooms, and any requested features. (3) Save to a DXF file named 'plan.dxf' in the current working directory. "
		"(4) Do not include placeholders; write runnable code only. (5) Avoid long commentary; keep code clean. "
	)


def build_prompt(user_prompt: str) -> str:
	return (
		f"{default_system_instruction()}\n\n"
		f"User requirements:\n{user_prompt}\n\n"
		"Return only Python code inside a fenced code block."
	)


def open_in_autocad(path: Path) -> bool:
	try:
		if os.name == "nt":
			os.startfile(str(path))  # type: ignore[attr-defined]
			return True
		return False
	except Exception:
		return False


def ui_sidebar():
	with st.sidebar:
		st.header("Settings")
		api_key_input = st.text_input("Google Gemini API Key", type="password", value=get_api_key())
		st.session_state["gemini_api_key"] = api_key_input
		st.caption("Set the key here, via GOOGLE_API_KEY, or use the built-in default (not recommended).")

		st.subheader("Model")
		selected_model = st.selectbox("Choose model", MODEL_CANDIDATES, index=0)
		st.session_state["gemini_model_name"] = selected_model

		st.markdown("---")
		st.subheader("Output")
		st.text(f"Work dir: {WORK_DIR}")
		if st.button("Clear work dir"):
			for p in WORK_DIR.iterdir():
				if p.is_file():
					p.unlink(missing_ok=True)
			st.success("Cleared.")


def get_model_with_fallback(genai, preferred_name: str):
	"""Try preferred model, then fallbacks in MODEL_CANDIDATES order."""
	ordered = [preferred_name] + [m for m in MODEL_CANDIDATES if m != preferred_name]
	last_err = None
	for name in ordered:
		try:
			return genai.GenerativeModel(name), name
		except Exception as e:  # some SDKs may validate name eagerly
			last_err = e
			continue
	# If all failed eagerly, raise the last error
	raise last_err if last_err else RuntimeError("No valid Gemini model available")


def sanitize_generated_code(code: str) -> str:
	# Fix common ezdxf unit constants and MTEXT alignment issues from LLM outputs
	replacements = {
		"ezdxf.units.M_FEET": "ezdxf.units.FT",
		"ezdxf.units.FEET": "ezdxf.units.FT",
		"ezdxf.units.FOOT": "ezdxf.units.FT",
		"ezdxf.units.METERS": "ezdxf.units.M",
		"ezdxf.units.METER": "ezdxf.units.M",
		"ezdxf.units.INCHES": "ezdxf.units.IN",
		"ezdxf.units.INCH": "ezdxf.units.IN",
		"MTextParagraphAlignment": "MTextEntityAlignment",
	}
	for a, b in replacements.items():
		code = code.replace(a, b)

	# Comment out unsupported doc.units assignments if any remain
	code = re.sub(r"^(\s*doc\.units\s*=\s*ezdxf\.units\.[A-Za-z_]+\s*)$",
				  r"# \1  # sanitized: unsupported unit constant",
				  code, flags=re.MULTILINE)

	# Replace invalid custom linetype definitions with a no-op 'pass' preserving indentation
	code = re.sub(r"^(\s*)doc\.linetypes\.add\([\s\S]*?\)\s*$",
				  r"\1pass  # sanitized: removed invalid custom linetype definition",
				  code, flags=re.MULTILINE)

	# Replace any unknown linetype strings in layer definitions with built-in DASHED
	code = re.sub(r"(linetype\s*:\s*)\"[A-Za-z0-9_\-]+\"",
				  r"\1\"DASHED\"",
				  code)

	# Also fix calls like doc.layers.new(..., dxfattribs={"linetype": "Something"}) to DASHED
	code = re.sub(r"(doc\.layers\.new\([\s\S]*?dxfattribs\s*=\s*\{[\s\S]*?\"linetype\"\s*:\s*)\"[A-Za-z0-9_\-]+\"",
				  r"\1\"DASHED\"",
				  code)

	# Remove stray escaping around quotes that can cause SyntaxError, e.g., \"DASHED\"
	code = code.replace('\\"', '"')

	# Normalize TEXT set_placement align strings (double or single quotes) to proper enum
	code = re.sub(r"(set_placement\([^\)]*align\s*=)\s*\"([A-Za-z_]+)\"",
				  r"\1 ezdxf.enums.TextEntityAlignment.\2",
				  code)
	code = re.sub(r"(set_placement\([^\)]*align\s*=)\s*\'([A-Za-z_]+)\'",
				  r"\1 ezdxf.enums.TextEntityAlignment.\2",
				  code)

	# Replace unsupported align_point=(...) with enum align argument
	code = re.sub(r"align_point\s*=\s*\([^\)]*\)",
				  r"align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER",
				  code)

	return code


def main():
	st.set_page_config(page_title=APP_TITLE, layout="wide")
	st.title(APP_TITLE)
	ui_sidebar()

	st.write("Describe your floor plan in natural language. The app will ask Gemini to generate a Python script that creates a DXF and then preview it.")

	default_prompt = (
		"Create a floor plan for a 40x60 ft plot, 8 ft front setback and 4 ft on other sides, "
		"with 1 bedroom with attached toilet, 1 bedroom, 1 kitchen, 1 dining space, 1 common toilet, "
		"1 parking, 1 garden, and a staircase near the front-right."
	)
	user_prompt = st.text_area("Your prompt", value=default_prompt, height=140)

	col1, col2 = st.columns([1, 1])
	with col1:
		generate = st.button("Generate DXF with Gemini", type="primary")
	with col2:
		preview_btn = st.button("Preview latest DXF")

	api_key = get_api_key()
	if generate:
		if not api_key:
			st.error("Please provide your Google Gemini API key in the sidebar.")
			st.stop()

		with st.spinner("Calling Gemini and generating code..."):
			genai = configure_gemini(api_key)
			preferred = st.session_state.get("gemini_model_name", MODEL_CANDIDATES[0])
			model, active_model = get_model_with_fallback(genai, preferred)
			st.caption(f"Using model: {active_model}")
			prompt = build_prompt(user_prompt)
			try:
				resp = model.generate_content(prompt)
			except Exception as e:
				# If the call fails (e.g., NotFound), iterate fallbacks at call time
				for alt in [m for m in MODEL_CANDIDATES if m != preferred]:
					try:
						model = genai.GenerativeModel(alt)
						resp = model.generate_content(prompt)
						st.caption(f"Fell back to model: {alt}")
						break
					except Exception:
						continue
				else:
					st.error(f"All model attempts failed: {e}")
					st.stop()
			text = resp.text or ""
			code = extract_python_code(text)
			code = sanitize_generated_code(code)

			pyfile = write_user_code(code, filename="generated_plan.py")
			st.code(code, language="python")

		with st.spinner("Running generated Python to produce DXF..."):
			try:
				proc = run_python_file(pyfile)
				stdout = proc.stdout
				stderr = proc.stderr
				if proc.returncode != 0:
					st.error("Script failed. See stderr below.")
					st.code(stderr or "(no stderr)", language="bash")
				else:
					st.success("Script executed successfully.")
					if stdout:
						st.code(stdout, language="bash")
			except subprocess.TimeoutExpired:
				st.error("Script timed out.")

	# Always show available outputs
	outputs = find_outputs()
	if outputs:
		st.subheader("Outputs in work dir")
		for p in outputs:
			st.write(f"- {p.name}")

		# Show preview of the newest DXF
		latest_dxf = None
		for p in reversed(outputs):
			if p.suffix.lower() == ".dxf":
				latest_dxf = p
				break

		if latest_dxf and (preview_btn or True):
			try:
				img_bytes = preview_dxf_image(latest_dxf)
				st.image(img_bytes, caption=f"Preview of {latest_dxf.name}", use_column_width=True)
			except Exception as e:
				st.warning(f"Preview unavailable: {e}")

		# Download options
		st.subheader("Download")
		for p in outputs:
			with open(p, "rb") as f:
				st.download_button(
					label=f"Download {p.name}",
					data=f.read(),
					file_name=p.name,
					mime="application/octet-stream",
					key=f"dl-{p.name}",
				)

		# Zip all
		zip_bytes = zip_work_dir()
		st.download_button(
			label="Download all outputs (ZIP)",
			data=zip_bytes,
			file_name="auto_arc_outputs.zip",
			mime="application/zip",
		)

		# Optional: open locally in AutoCAD (Windows only, local run)
		if latest_dxf and os.name == "nt":
			if st.button("Open latest DXF in AutoCAD (local Windows)"):
				success = open_in_autocad(latest_dxf)
				if success:
					st.info("Attempted to open in AutoCAD. If AutoCAD is installed and associated with .dxf, it should launch.")
				else:
					st.warning("Could not open file automatically. Please open the downloaded file in AutoCAD manually.")
	else:
		st.info("No outputs yet. Click 'Generate DXF with Gemini' to start.")


if __name__ == "__main__":
	main()
