# ⚡ Quick Start Guide - 5 Minutes Setup

Get your AI resume optimizer running in 5 minutes!

## Step 1: Install Ollama (2 min)

### macOS
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
1. Download installer: [https://ollama.com/download/windows](https://ollama.com/download/windows)
2. Run the installer
3. Ollama will start automatically

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Step 2: Download AI Model (1 min)

```bash
ollama pull orca-mini
```

*This downloads a 3GB model optimized for CPU. Takes 1-3 minutes depending on your internet.*

## Step 3: Install Python Dependencies (1 min)

```bash
pip install streamlit pandas plotly pdfplumber reportlab requests pydantic
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## Step 4: Create Project Structure (30 sec)

```
resume-optimizer/
├── main.py
├── src/
│   ├── __init__.py
│   ├── llm_engine.py
│   └── utils.py
```

Copy the code files I provided into these locations.

## Step 5: Run the App (30 sec)

```bash
# Terminal 1 - Start Ollama (if not auto-started)
ollama serve

# Terminal 2 - Start the app
streamlit run main.py
```

Your browser will open automatically to `http://localhost:8501`

## 🎉 You're Ready!

1. Upload your resume PDF
2. Paste a job description
3. Click "Analyze"
4. Wait 30-60 seconds
5. Download your optimized resume!

## ⚠️ Common Issues

**"Cannot connect to Ollama"**
```bash
# Start Ollama
ollama serve
```

**"Model not found"**
```bash
# Download model
ollama pull orca-mini
```

**"No module named 'streamlit'"**
```bash
# Install dependencies
pip install -r requirements.txt
```

## 💡 Pro Tips

1. **First run is slow**: Model loads into memory (30-60 sec). Subsequent runs are faster!
2. **Use complete job descriptions**: More details = better optimization
3. **Check your PDF**: Ensure text is selectable, not a scanned image
4. **Close other apps**: Free up RAM for better performance

## 🚀 Next Steps

- Try different models: `ollama pull phi3`, `ollama pull tinyllama`
- Customize prompts in `src/llm_engine.py`
- Tweak PDF formatting in `src/utils.py`

---

**Having issues?** Check the full README.md for detailed troubleshooting!