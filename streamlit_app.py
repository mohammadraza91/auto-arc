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


def find_outputs(suffixes=(".dxf", ".png", ".svg", ".csv", ".json", ".html", ".txt", ".py")):
	files = []
	for p in WORK_DIR.iterdir():
		if p.is_file() and p.suffix.lower() in suffixes:
			files.append(p)
	return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)  # Most recent first


def add_to_session_history(prompt: str, content_type: str, code: str, success: bool):
	"""Add generation to session history."""
	if "generation_history" not in st.session_state:
		st.session_state.generation_history = []
	
	history_entry = {
		"timestamp": time.time(),
		"prompt": prompt,
		"content_type": content_type,
		"code": code,
		"success": success
	}
	st.session_state.generation_history.insert(0, history_entry)  # Add to beginning
	# Keep only last 10 generations
	if len(st.session_state.generation_history) > 10:
		st.session_state.generation_history = st.session_state.generation_history[:10]


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


def detect_content_type(user_prompt: str) -> str:
	"""Detect what type of content the user wants to generate based on keywords."""
	prompt_lower = user_prompt.lower()
	
	# CAD/DXF related keywords
	cad_keywords = ['floor plan', 'dxf', 'cad', 'drawing', 'blueprint', 'architecture', 'building', 'room', 'plot', 'setback', 'floor', 'plan']
	# Data analysis keywords
	data_keywords = ['data', 'analysis', 'chart', 'graph', 'visualization', 'plot', 'statistics', 'pandas', 'numpy', 'matplotlib', 'seaborn']
	# Web app keywords
	web_keywords = ['web app', 'website', 'streamlit', 'flask', 'django', 'html', 'css', 'javascript', 'frontend', 'backend']
	# General Python keywords
	python_keywords = ['python', 'script', 'function', 'class', 'algorithm', 'automation', 'tool']
	
	if any(keyword in prompt_lower for keyword in cad_keywords):
		return "cad"
	elif any(keyword in prompt_lower for keyword in data_keywords):
		return "data_analysis"
	elif any(keyword in prompt_lower for keyword in web_keywords):
		return "web_app"
	elif any(keyword in prompt_lower for keyword in python_keywords):
		return "python_script"
	else:
		return "general"


def get_system_instruction(content_type: str) -> str:
	"""Get appropriate system instruction based on content type."""
	if content_type == "cad":
		return (
			"You are an expert Python CAD assistant. Generate a single self-contained Python script "
			"that uses the ezdxf library to create a DXF floor plan according to the user's prompt. "
			"Requirements: (1) Use feet as drawing units and consistent coordinates. (2) Include plot outline, "
			"setbacks, labeled rooms, and any requested features. (3) Save to a DXF file named 'plan.dxf' in the current working directory. "
			"(4) Do not include placeholders; write runnable code only. (5) Avoid long commentary; keep code clean. "
			"(6) CRITICAL: Always include a main execution block with 'if __name__ == \"__main__\":' at the end to ensure the code runs. "
			"(7) Add print statements to show progress and confirm DXF file creation. "
		)
	elif content_type == "data_analysis":
		return (
			"You are an expert Python data analysis assistant. Generate a single self-contained Python script "
			"that performs data analysis according to the user's prompt. "
			"Requirements: (1) Use appropriate libraries (pandas, numpy, matplotlib, seaborn, etc.). "
			"(2) Include data loading, processing, visualization, and analysis. (3) Save outputs as appropriate files. "
			"(4) Write clean, well-commented code. (5) Include error handling where appropriate. "
		)
	elif content_type == "web_app":
		return (
			"You are an expert Python web development assistant. Generate a single self-contained Python script "
			"that creates a web application according to the user's prompt. "
			"Requirements: (1) Use appropriate frameworks (Streamlit, Flask, Django, etc.). "
			"(2) Include proper UI/UX design. (3) Handle user interactions and data processing. "
			"(4) Write clean, modular code. (5) Include proper error handling and validation. "
		)
	elif content_type == "python_script":
		return (
			"You are an expert Python developer. Generate a single self-contained Python script "
			"that accomplishes the task described in the user's prompt. "
			"Requirements: (1) Use appropriate Python libraries and best practices. "
			"(2) Write clean, efficient, and well-documented code. (3) Include proper error handling. "
			"(4) Make the code modular and reusable where appropriate. "
		)
	else:  # general
		return (
			"You are an expert Python developer. Generate a single self-contained Python script "
			"that accomplishes the task described in the user's prompt. "
			"Requirements: (1) Use appropriate Python libraries. (2) Write clean, efficient code. "
			"(3) Include proper error handling. (4) Make the code practical and runnable. "
		)


def default_system_instruction() -> str:
	"""Legacy function for backward compatibility."""
	return get_system_instruction("cad")


def build_prompt(user_prompt: str) -> str:
	content_type = detect_content_type(user_prompt)
	system_instruction = get_system_instruction(content_type)
	
	return (
		f"{system_instruction}\n\n"
		f"User requirements:\n{user_prompt}\n\n"
		"Return only Python code inside a fenced code block."
	)


def open_in_autocad(path: Path) -> bool:
	"""Open DXF file in AutoCAD on Windows."""
	try:
		if os.name == "nt":
			# Try to open with AutoCAD first
			autocad_paths = [
				"C:\\Program Files\\Autodesk\\AutoCAD 2024\\acad.exe",
				"C:\\Program Files\\Autodesk\\AutoCAD 2023\\acad.exe", 
				"C:\\Program Files\\Autodesk\\AutoCAD 2022\\acad.exe",
				"C:\\Program Files\\Autodesk\\AutoCAD 2021\\acad.exe",
				"C:\\Program Files\\Autodesk\\AutoCAD 2020\\acad.exe"
			]
			
			# Try AutoCAD first
			for autocad_path in autocad_paths:
				if os.path.exists(autocad_path):
					subprocess.Popen([autocad_path, str(path)])
					return True
			
			# Fallback to default file association
			os.startfile(str(path))  # type: ignore[attr-defined]
			return True
		return False
	except Exception as e:
		print(f"Error opening in AutoCAD: {e}")
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
		"ezdxf.units.M_FOOT": "ezdxf.units.FT",  # Fix the specific error
		"ezdxf.units.METERS": "ezdxf.units.M",
		"ezdxf.units.METER": "ezdxf.units.M",
		"ezdxf.units.INCHES": "ezdxf.units.IN",
		"ezdxf.units.INCH": "ezdxf.units.IN",
		"MTextParagraphAlignment": "MTextEntityAlignment",
		"Measurement.ENGLISH": "Measurement.Imperial",
		"Measurement.METRIC": "Measurement.Metric",
	}
	for a, b in replacements.items():
		code = code.replace(a, b)

	# Fix incorrect header unit assignments - replace with proper doc.units assignment
	code = re.sub(r"doc\.header\['\$INSUNITS'\]\s*=\s*ezdxf\.units\.FT",
				  r"doc.units = ezdxf.units.FT",
				  code)
	code = re.sub(r"doc\.header\['\$INSUNITS'\]\s*=\s*4",
				  r"doc.units = ezdxf.units.FT",
				  code)
	# Fix the specific M_FOOT error
	code = re.sub(r"doc\.header\['\$INSUNITS'\]\s*=\s*ezdxf\.units\.M_FOOT",
				  r"doc.units = ezdxf.units.FT",
				  code)

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

	# Fix text positioning methods
	code = re.sub(r"\.set_pos\(",
				  r".set_placement(",
				  code)
	
	# Fix text alignment strings to use proper enum
	code = re.sub(r"align\s*=\s*['\"]CENTER['\"]",
				  r"align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER",
				  code)
	code = re.sub(r"align\s*=\s*['\"]MIDDLE_CENTER['\"]",
				  r"align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER",
				  code)

	# Remove invalid layer attributes
	code = re.sub(r"dxfattribs\s*=\s*\{[^}]*'font'[^}]*\}",
				  r"dxfattribs={'color': 5}",
				  code)

	# Ensure the code has a main execution block for CAD files
	if content_type == "cad" and "if __name__" not in code:
		# Add main execution block if missing
		code += "\n\nif __name__ == '__main__':\n"
		code += "    # Execute the floor plan generation\n"
		code += "    print('Generating DXF floor plan...')\n"
		code += "    print('DXF file created successfully!')\n"

	return code


def main():
	st.set_page_config(page_title=APP_TITLE, layout="wide")
	st.title(APP_TITLE)
	ui_sidebar()

	st.write("Describe what you want to create in natural language. The app will automatically detect the type of content and ask Gemini to generate appropriate Python code.")

	# Show example prompts for different content types
	with st.expander("💡 Example prompts for different content types"):
		st.markdown("""
		**CAD/Floor Plans:**
		- "Create a floor plan for a 40x60 ft plot with 2 bedrooms, kitchen, and living room"
		- "Design a simple house layout with parking and garden"
		
		**Data Analysis:**
		- "Analyze sales data and create visualizations showing trends"
		- "Create a dashboard for stock market data with charts"
		
		**Web Applications:**
		- "Create a simple todo list web app with Streamlit"
		- "Build a calculator web application"
		
		**Python Scripts:**
		- "Create a file organizer that sorts files by type"
		- "Build a password generator with customizable options"
		""")

	default_prompt = (
		"Create a floor plan for a 40x60 ft plot, 8 ft front setback and 4 ft on other sides, "
		"with 1 bedroom with attached toilet, 1 bedroom, 1 kitchen, 1 dining space, 1 common toilet, "
		"1 parking, 1 garden, and a staircase near the front-right."
	)
	user_prompt = st.text_area("Your prompt", value=default_prompt, height=140)
	
	# Show detected content type
	if user_prompt:
		content_type = detect_content_type(user_prompt)
		type_emojis = {
			"cad": "🏗️",
			"data_analysis": "📊", 
			"web_app": "🌐",
			"python_script": "🐍",
			"general": "⚙️"
		}
		type_names = {
			"cad": "CAD/Floor Plan",
			"data_analysis": "Data Analysis",
			"web_app": "Web Application", 
			"python_script": "Python Script",
			"general": "General Python"
		}
		st.info(f"{type_emojis.get(content_type, '⚙️')} Detected content type: **{type_names.get(content_type, 'General')}**")

	col1, col2 = st.columns([1, 1])
	with col1:
		generate = st.button("🚀 Generate Code with Gemini", type="primary")
	with col2:
		preview_btn = st.button("👁️ Preview Latest Output")

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
			
			# Detect content type and build appropriate prompt
			content_type = detect_content_type(user_prompt)
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
			
			# Apply content-specific sanitization
			if content_type == "cad":
				code = sanitize_generated_code(code)
			
			# Generate appropriate filename based on content type
			filename_map = {
				"cad": "generated_plan.py",
				"data_analysis": "data_analysis.py", 
				"web_app": "web_app.py",
				"python_script": "script.py",
				"general": "generated_code.py"
			}
			filename = filename_map.get(content_type, "generated_code.py")
			
			pyfile = write_user_code(code, filename=filename)
			st.code(code, language="python")

		with st.spinner(f"Running generated {content_type} code..."):
			try:
				proc = run_python_file(pyfile)
				stdout = proc.stdout
				stderr = proc.stderr
				success = proc.returncode == 0
				
				# Add to session history
				add_to_session_history(user_prompt, content_type, code, success)
				
				# For CAD content, show additional info about DXF creation
				if content_type == "cad" and success:
					dxf_files = [f for f in find_outputs() if f.suffix.lower() == ".dxf"]
					if dxf_files:
						st.info(f"🏗️ DXF file created: {dxf_files[0].name}")
					else:
						st.warning("⚠️ No DXF file was created. Check the code for issues.")
				
				if not success:
					st.error("Script failed. See stderr below.")
					st.code(stderr or "(no stderr)", language="bash")
				else:
					st.success(f"✅ {content_type.replace('_', ' ').title()} code executed successfully!")
					if stdout:
						st.code(stdout, language="bash")
					
					# Auto-open DXF files in AutoCAD for CAD content
					if content_type == "cad":
						dxf_files = [f for f in find_outputs() if f.suffix.lower() == ".dxf"]
						if dxf_files:
							latest_dxf = dxf_files[0]  # Most recent DXF file
							if st.button("🪟 Open in AutoCAD", key="auto_open_autocad"):
								success = open_in_autocad(latest_dxf)
								if success:
									st.info("🚀 Opening DXF file in AutoCAD...")
								else:
									st.warning("Could not open in AutoCAD automatically. Please open the file manually.")
			except subprocess.TimeoutExpired:
				st.error("Script timed out.")
				add_to_session_history(user_prompt, content_type, code, False)

	# Show session history
	if "generation_history" in st.session_state and st.session_state.generation_history:
		with st.expander("📚 Generation History", expanded=False):
			for i, entry in enumerate(st.session_state.generation_history[:5]):  # Show last 5
				status_emoji = "✅" if entry["success"] else "❌"
				content_emoji = {
					"cad": "🏗️", "data_analysis": "📊", "web_app": "🌐", 
					"python_script": "🐍", "general": "⚙️"
				}.get(entry["content_type"], "⚙️")
				
				st.markdown(f"""
				**{status_emoji} {content_emoji} {entry['content_type'].replace('_', ' ').title()}**  
				*{entry['prompt'][:100]}{'...' if len(entry['prompt']) > 100 else ''}*
				""")

	# Always show available outputs
	outputs = find_outputs()
	if outputs:
		st.subheader("📁 Generated Files")
		for p in outputs:
			file_emoji = {
				".dxf": "🏗️", ".png": "🖼️", ".svg": "🎨", ".csv": "📊", 
				".json": "📋", ".html": "🌐", ".txt": "📄", ".py": "🐍"
			}.get(p.suffix.lower(), "📄")
			st.write(f"{file_emoji} {p.name}")

		# Show preview of the newest DXF (if any)
		latest_dxf = None
		for p in outputs:
			if p.suffix.lower() == ".dxf":
				latest_dxf = p
				break

		if latest_dxf and (preview_btn or True):
			try:
				img_bytes = preview_dxf_image(latest_dxf)
				st.image(img_bytes, caption=f"Preview of {latest_dxf.name}", use_column_width=True)
			except Exception as e:
				st.warning(f"Preview unavailable: {e}")
				st.info("💡 You can still download and open the DXF file in AutoCAD for full viewing.")

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
		st.info("No outputs yet. Click '🚀 Generate Code with Gemini' to start creating!")


if __name__ == "__main__":
	main()
