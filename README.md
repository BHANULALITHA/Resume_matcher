# 🚀 AI Resume Optimizer

An intelligent resume optimization tool that uses local AI (Ollama) to tailor your resume to specific job descriptions. Works completely offline on your CPU laptop.

## ✨ Features

- 🤖 **AI-Powered Analysis** - Uses Ollama for intelligent resume optimization
- 📊 **ATS Compatibility Scoring** - Get a match score between your resume and job description
- 🔑 **Keyword Gap Analysis** - Identify missing keywords that could improve your chances
- ✍️ **Auto Cover Letter** - Generate personalized cover letters
- 📄 **Professional PDF Export** - Download ATS-optimized resume as PDF
- 🔒 **100% Private** - All processing happens locally on your machine

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running

### Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [https://ollama.com/download](https://ollama.com/download)

### Download AI Model

```bash
# Recommended model (best balance of speed/quality on CPU)
ollama pull orca-mini

# Alternative options:
ollama pull phi3          # Good balance
ollama pull tinyllama     # Fastest (lower quality)
ollama pull neural-chat   # Best quality (slower)
```

## 🚀 Installation

1. **Clone or download this project**

2. **Create project structure:**
```
resume-optimizer/
├── main.py
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── llm_engine.py
│   └── utils.py
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Start Ollama service:**
```bash
ollama serve
```

5. **Run the application:**
```bash
streamlit run main.py
```

6. **Open your browser** to `http://localhost:8501`

## 📖 How to Use

1. **Upload Resume**: Click "Upload Your Resume (PDF)" and select your current resume
2. **Paste Job Description**: Copy the full job description and paste it in the text area
3. **Analyze**: Click "Analyze & Generate Optimized Resume"
4. **Wait**: Processing takes 30-60 seconds on CPU (be patient!)
5. **Review Results**: Check your match score and optimized resume
6. **Download**: Download the tailored resume as PDF

## 💡 Tips for Best Results

### For Resume:
- Use a standard PDF (not scanned images)
- Ensure text is selectable in your PDF
- Include your actual contact information

### For Job Description:
- Paste the **complete** job description
- Include all sections: requirements, responsibilities, qualifications
- The more detailed, the better the analysis

### Model Selection:
- **orca-mini** (Recommended): Best balance - 5-10 seconds per analysis
- **tinyllama**: Fastest - 2-3 seconds but lower quality
- **phi3**: Good middle ground
- **neural-chat**: Highest quality - 15-20 seconds

## 🔧 Troubleshooting

### "Cannot connect to Ollama"
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

### "Model not found"
```bash
# Download the model
ollama pull orca-mini

# Verify installation
ollama list
```

### "No text extracted from PDF"
- Ensure your PDF is not a scanned image
- Try converting your resume to a fresh PDF
- Check that text is selectable in the PDF viewer

### Slow processing
- This is normal on CPU! First run takes longer (30-60 seconds)
- Subsequent analyses are cached and faster
- Try smaller models like `tinyllama` for speed
- Close other applications to free up RAM

### Application won't start
```bash
# Install missing dependencies
pip install -r requirements.txt --upgrade

# Check Python version (needs 3.8+)
python --version
```

## 🎯 Understanding Your Score

- **80-100**: Excellent match - your resume aligns very well
- **60-79**: Good match - add suggested keywords to improve
- **40-59**: Moderate match - significant improvements needed
- **0-39**: Low match - consider highlighting more relevant experience

## 🔐 Privacy & Security

- ✅ All processing happens **locally** on your computer
- ✅ No data is sent to external servers
- ✅ Your resume never leaves your machine
- ✅ Ollama runs completely offline

## 📝 File Structure

```
resume-optimizer/
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── src/
    ├── __init__.py        # Package initializer
    ├── llm_engine.py      # AI analysis engine
    └── utils.py           # PDF handling utilities
```

## 🛠️ Advanced Configuration

### Customize Model Parameters

Edit `src/llm_engine.py`:
```python
payload = {
    "temperature": 0.3,  # Lower = more focused (0.0-1.0)
    "top_p": 0.9,       # Diversity of responses
    "num_predict": 2000 # Max tokens to generate
}
```

### Change Timeout Settings

For slower CPUs, increase timeout in `src/llm_engine.py`:
```python
self.session.timeout = 300  # 5 minutes (default)
```

## 🐛 Known Issues

1. **First analysis is slow**: First model load takes time. Be patient!
2. **PDF extraction varies**: Some PDFs are harder to parse than others
3. **Memory usage**: Large models need 4-8GB RAM

## 🤝 Contributing

Found a bug? Have a suggestion? Feel free to modify and improve!

## 📄 License

Free to use and modify for personal and commercial purposes.

## 🙏 Credits

- **Streamlit** - Web framework
- **Ollama** - Local AI inference
- **ReportLab** - PDF generation
- **PDFPlumber** - PDF text extraction

---

**Made with ❤️ for job seekers everywhere**

Need help? Check the troubleshooting section above or create an issue.