# 🏗️ Auto ARC - AI-Powered Code Generator

> **Transform your ideas into working code with the power of AI**

Auto ARC is an intelligent Streamlit application that uses Google Gemini AI to generate Python code based on your natural language descriptions. Whether you need CAD drawings, data analysis scripts, web applications, or automation tools - just describe what you want, and Auto ARC will create it for you!

## ✨ Features

### 🎯 Smart Content Detection
- **Automatic Classification**: Detects CAD, data analysis, web apps, Python scripts, and general code
- **Context-Aware Generation**: Uses appropriate libraries and patterns for each content type
- **Keyword Recognition**: Analyzes your description to determine the best approach
- **Auto-Execution**: Generated code automatically runs and creates output files

### 🏗️ CAD & Floor Plans
- **DXF Generation**: Creates professional CAD drawings with ezdxf
- **Floor Plan Design**: Generates detailed architectural layouts
- **Layer Management**: Organized drawing layers for different elements
- **Live Preview**: Visual preview of generated DXF files
- **AutoCAD Integration**: Direct opening in AutoCAD (Windows)
- **Auto-Execution**: Generated CAD code automatically runs and creates DXF files
- **Multi-Version Support**: Works with AutoCAD 2020-2024

### 📊 Data Analysis & Visualization
- **Pandas Integration**: Data manipulation and analysis scripts
- **Chart Generation**: Matplotlib, Seaborn, and Plotly visualizations
- **Statistical Analysis**: Automated data processing workflows
- **Export Options**: CSV, JSON, and image outputs

### 🌐 Web Applications
- **Streamlit Apps**: Interactive web applications
- **Flask/Django**: Full-stack web development
- **UI Components**: Modern, responsive interfaces
- **Real-time Features**: Dynamic content and user interactions

### 🐍 Python Automation
- **Script Generation**: File processing, automation, and utilities
- **API Integration**: REST APIs and data fetching
- **Error Handling**: Robust code with proper exception handling
- **Best Practices**: Clean, documented, and maintainable code

### 🔄 Session Management
- **Generation History**: Track your last 10 generations
- **Success Tracking**: Monitor which attempts worked
- **Easy Iteration**: Refine and improve your requests
- **Context Preservation**: Remember previous generations

### 📁 Multi-Format Outputs
- **DXF Files**: CAD drawings and floor plans
- **Images**: PNG, SVG visualizations
- **Data Files**: CSV, JSON exports
- **Web Files**: HTML applications
- **Python Scripts**: Executable code files

## 🔧 Recent Fixes & Improvements

### ✅ **Fixed DXF Generation Issues**
- **Problem**: Generated Python code wasn't automatically executing to create DXF files
- **Solution**: Enhanced code sanitization to ensure all CAD code includes proper main execution blocks
- **Result**: DXF files are now automatically created when you generate floor plans

### ✅ **Enhanced AutoCAD Integration**
- **Problem**: DXF files weren't opening directly in AutoCAD
- **Solution**: Improved AutoCAD detection and integration with multiple version support
- **Result**: One-click opening in AutoCAD 2020-2024 with automatic file association

### ✅ **Improved Code Execution**
- **Problem**: Generated code sometimes failed to run due to missing execution blocks
- **Solution**: Smart code sanitization that automatically adds `if __name__ == '__main__':` blocks
- **Result**: All generated code now runs successfully and creates output files

### ✅ **Better User Experience**
- **Problem**: No feedback on DXF file creation status
- **Solution**: Added real-time status updates and file creation verification
- **Result**: Clear feedback showing when DXF files are created and ready to use

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/auto-arc.git
   cd auto-arc
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 📖 Usage Guide

### 1. Setup API Key
- Enter your Google Gemini API key in the sidebar
- Or set the `GOOGLE_API_KEY` environment variable

### 2. Describe Your Project
Simply describe what you want to create in natural language:

**🏗️ Floor Plans:**
```
"Create a 2-bedroom house with kitchen, living room, and two bathrooms"
"Design a 40x60 ft plot with 5 ft setbacks and modern layout"
```

**📊 Data Analysis:**
```
"Analyze sales data and create trend charts with pandas"
"Build a dashboard for stock market data with interactive plots"
```

**🌐 Web Applications:**
```
"Create a todo list app with Streamlit"
"Build a calculator web application with Flask"
```

**🐍 Python Scripts:**
```
"Create a file organizer that sorts files by type"
"Build a password generator with customizable options"
```

### 3. Generate & Iterate
- Click "🚀 Generate Code with Gemini"
- **Code automatically runs** and creates output files
- Review the generated code and execution results
- **For CAD content**: DXF files are automatically created
- Use generation history to iterate

### 4. Download & Use
- **For Floor Plans**: Click "🪟 Open in AutoCAD" to view in AutoCAD
- Download individual files or all outputs as ZIP
- **AutoCAD Integration**: Direct opening in AutoCAD 2020-2024
- Run generated Python scripts
- Deploy web applications

## 🎨 Content Types & Examples

### 🏗️ CAD/Floor Plans
- **Keywords**: floor plan, dxf, cad, drawing, blueprint, architecture, building, room, plot, setback
- **Outputs**: DXF files with layers, dimensions, and annotations
- **Features**: Setbacks, room layouts, doors, windows, dimensions

### 📊 Data Analysis
- **Keywords**: data, analysis, chart, graph, visualization, plot, statistics, pandas, numpy, matplotlib, seaborn
- **Outputs**: CSV files, charts, statistical reports
- **Features**: Data processing, visualization, statistical analysis

### 🌐 Web Applications
- **Keywords**: web app, website, streamlit, flask, django, html, css, javascript, frontend, backend
- **Outputs**: HTML files, interactive applications
- **Features**: User interfaces, data processing, real-time updates

### 🐍 Python Scripts
- **Keywords**: python, script, function, class, algorithm, automation, tool
- **Outputs**: Executable Python files
- **Features**: File processing, API integration, automation

## 🛠️ Technical Details

### Architecture
- **Frontend**: Streamlit web interface
- **AI Engine**: Google Gemini API
- **Code Execution**: Subprocess with timeout handling
- **File Management**: Organized work directory structure
- **Error Handling**: Comprehensive sanitization and validation

### Dependencies
```
streamlit>=1.37.0          # Web interface
google-generativeai>=0.8.0 # AI integration
ezdxf>=1.3.0               # CAD file generation
matplotlib>=3.8.0          # Visualization
pandas>=2.0.0              # Data analysis
numpy>=1.24.0              # Numerical computing
seaborn>=0.12.0            # Statistical visualization
plotly>=5.0.0              # Interactive charts
```

### File Structure
```
auto-arc/
├── streamlit_app.py       # Main application
├── requirements.txt       # Dependencies
├── README.md             # Documentation
├── work_dir/             # Generated files
│   ├── generated_plan.py # Latest generated code
│   └── plan.dxf         # CAD outputs
└── venv/                # Virtual environment
```

## 🔧 Advanced Features

### Code Sanitization
- **ezdxf Fixes**: Automatic correction of common ezdxf errors
- **Unit Constants**: Proper unit handling for CAD drawings
- **Method Corrections**: Fix deprecated or incorrect method calls
- **Enum Updates**: Convert string values to proper enums

### Model Fallback System
- **Primary Model**: gemini-2.5-flash
- **Fallback Models**: Multiple Gemini model options
- **Error Recovery**: Automatic retry with different models
- **Performance Optimization**: Fastest available model selection

### Session Management
- **History Tracking**: Last 10 generations with success status
- **Context Preservation**: Maintains conversation context
- **Easy Iteration**: Quick access to previous attempts
- **Progress Monitoring**: Track generation success rates

## 🎯 Use Cases

### 🏢 Architecture & Engineering
- Floor plan generation
- Site layout design
- Technical drawings
- CAD file creation

### 📈 Data Science
- Exploratory data analysis
- Statistical modeling
- Data visualization
- Report generation

### 💻 Software Development
- Web application prototyping
- Automation script creation
- API development
- Tool creation

### 🎓 Education & Learning
- Code example generation
- Learning material creation
- Project scaffolding
- Best practice demonstrations

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup
```bash
git clone https://github.com/yourusername/auto-arc.git
cd auto-arc
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini**: AI model powering the code generation
- **Streamlit**: Web application framework
- **ezdxf**: CAD file generation library
- **Open Source Community**: For the amazing Python ecosystem

## 🔧 Troubleshooting

### Common Issues & Solutions

#### **DXF Files Not Created**
- **Issue**: Generated code runs but no DXF file appears
- **Solution**: Check that your prompt includes CAD keywords (floor plan, dxf, cad, etc.)
- **Verification**: Look for "DXF file created successfully!" message in output

#### **AutoCAD Not Opening**
- **Issue**: "Open in AutoCAD" button doesn't work
- **Solution**: Ensure AutoCAD is installed and associated with .dxf files
- **Alternative**: Download the DXF file and open manually

#### **Code Execution Errors**
- **Issue**: Generated code fails to run
- **Solution**: The app now automatically fixes common ezdxf issues
- **Fallback**: Try rephrasing your prompt or simplifying the request

#### **Preview Not Showing**
- **Issue**: DXF preview doesn't display
- **Solution**: Preview requires matplotlib - DXF files still work in AutoCAD
- **Alternative**: Use "Open in AutoCAD" for full viewing

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/auto-arc/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/auto-arc/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/auto-arc/wiki)

## 🚀 Roadmap

- [ ] **Multi-language Support**: Generate code in multiple programming languages
- [ ] **Template System**: Pre-built templates for common use cases
- [ ] **Collaboration Features**: Share and collaborate on generated code
- [ ] **Version Control**: Git integration for generated projects
- [ ] **Cloud Deployment**: One-click deployment to cloud platforms
- [ ] **Plugin System**: Extensible architecture for custom generators

---

<div align="center">

**Made with ❤️ by the Auto ARC Team**

[⭐ Star this repo](https://github.com/yourusername/auto-arc) | [🐛 Report Bug](https://github.com/yourusername/auto-arc/issues) | [💡 Request Feature](https://github.com/yourusername/auto-arc/issues)

</div>