import json
import hashlib
import re
from typing import Dict, Any, List
import requests

class LLMEngine:
    """Optimized LLM engine for resume analysis with robust error handling."""
    
    def __init__(self, model_name="orca-mini:latest"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434"
        self.cache = {}
        self.session = requests.Session()
        self.session.timeout = 300  # 5 minutes for CPU processing
        
    def _get_cache_key(self, resume_text: str, job_desc: str) -> str:
        """Generate cache key from inputs."""
        combined = f"{resume_text[:1000]}|{job_desc[:500]}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _test_ollama_connection(self) -> bool:
        """Test if Ollama is accessible."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _call_ollama(self, prompt: str, max_tokens: int = 2000) -> str:
        """Call Ollama API with streaming for better responsiveness."""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": 0.3,
            "top_p": 0.9,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
                "num_ctx": 4096,
            }
        }
        
        response_text = ""
        
        try:
            response = self.session.post(url, json=payload, stream=True, timeout=180)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        response_text += chunk.get("response", "")
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama connection error: {str(e)}. Ensure Ollama is running with: ollama serve")
        
        return response_text.strip()
    
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Robust JSON extraction with multiple fallback strategies."""
        if not text or not isinstance(text, str):
            return {}
        
        text = text.strip()
        
        # Strategy 1: Direct JSON parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract from code blocks
        if "```" in text:
            try:
                json_text = text.split("```")[1]
                if json_text.startswith("json"):
                    json_text = json_text[4:]
                return json.loads(json_text.strip())
            except (IndexError, json.JSONDecodeError):
                pass
        
        # Strategy 3: Find JSON object boundaries
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start != -1 and end > start:
            try:
                json_str = text[start:end]
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Fix common JSON issues
        if start != -1 and end > start:
            try:
                fixed = text[start:end]
                fixed = fixed.replace("'", '"')  # Single to double quotes
                fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)  # Remove trailing commas
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass
        
        return {}
    
    def _extract_personal_info(self, resume_text: str) -> Dict[str, str]:
        """Extract personal information using regex patterns."""
        info = {"name": "", "email": "", "phone": ""}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, resume_text)
        if email_match:
            info["email"] = email_match.group(0)
        
        # Extract phone (various formats)
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, resume_text)
        if phone_match:
            info["phone"] = phone_match.group(0)
        
        # Extract name (assume first line or first 100 chars contains name)
        lines = resume_text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            # Name is typically 2-4 words, capitalized, no special chars
            if len(line.split()) >= 2 and len(line.split()) <= 4:
                if line[0].isupper() and not any(char in line for char in ['@', 'http', '/', '\\']):
                    info["name"] = line
                    break
        
        return info
    
    def analyze(self, resume_text: str, job_desc: str) -> Dict[str, Any]:
        """Analyze resume against job description and generate optimized version."""
        
        # Check cache
        cache_key = self._get_cache_key(resume_text, job_desc)
        if cache_key in self.cache:
            print("✅ Using cached result")
            return self.cache[cache_key]
        
        # Test Ollama connection
        if not self._test_ollama_connection():
            raise Exception(
                "Cannot connect to Ollama. Please ensure:\n"
                "1. Ollama is installed\n"
                "2. Ollama service is running: ollama serve\n"
                "3. Model is downloaded: ollama pull " + self.model_name
            )
        
        # Extract personal info first
        personal_info = self._extract_personal_info(resume_text)
        
        # Prepare optimized prompt
        prompt = self._build_analysis_prompt(resume_text, job_desc)
        
        # Call LLM
        print(f"🤖 Calling Ollama with {self.model_name}...")
        response = self._call_ollama(prompt)
        
        # Parse response
        parsed_data = self._extract_json_from_response(response)
        
        # Build complete result with fallbacks
        result = self._build_result(parsed_data, personal_info, resume_text, job_desc)
        
        # Cache result
        self.cache[cache_key] = result
        
        return result
    
    def _build_analysis_prompt(self, resume_text: str, job_desc: str) -> str:
        """Build optimized prompt for LLM analysis."""
        
        # Truncate to fit context window
        resume_snippet = resume_text[:2000]
        job_snippet = job_desc[:1500]
        
        prompt = f"""You are an expert resume optimization specialist. Analyze this resume against the job description and extract REAL information.

RESUME:
{resume_snippet}

JOB DESCRIPTION:
{job_snippet}

YOUR TASK:
1. Extract the candidate's actual skills from their resume (NOT generic placeholders)
2. Identify 3-5 important keywords from the job description that are MISSING from the resume
3. Calculate match score: (skills candidate has / skills job requires) × 100
4. Write a professional 2-3 sentence summary tailored to THIS job
5. Generate 3-4 sentence cover letter highlighting relevant experience for THIS role

RESPOND WITH ONLY VALID JSON (no markdown, no code blocks, no explanation):
{{
  "skills": ["actual skill 1", "actual skill 2", "actual skill 3", "actual skill 4", "actual skill 5"],
  "missing_keywords": ["missing keyword 1", "missing keyword 2", "missing keyword 3"],
  "match_score": 75,
  "summary": "Professional with X years of experience in Y, skilled in Z. Proven track record of ABC. Seeking to leverage expertise in DEF.",
  "cover_letter": "I am excited to apply for this position. With my background in X and Y, I have successfully Z. I am confident I can contribute to your team by ABC."
}}

CRITICAL RULES:
- Extract REAL skills from resume, not placeholders like "Skill1, Skill2"
- match_score must be integer 0-100
- missing_keywords should be specific technical skills/tools from job description
- summary and cover_letter must be realistic and specific to this job, not generic templates
- Output ONLY the JSON object, nothing else"""

        return prompt
    
    def _build_result(self, parsed: Dict[str, Any], personal_info: Dict[str, str], 
                     resume_text: str, job_desc: str) -> Dict[str, Any]:
        """Build complete result with intelligent fallbacks."""
        
        # Default structure
        result = {
            "personal_info": personal_info,
            "summary": "",
            "skills": [],
            "missing_keywords": [],
            "match_score": 0,
            "experience": [],
            "education": [],
            "cover_letter": ""
        }
        
        # Extract from parsed response
        if parsed:
            result["skills"] = self._extract_list(parsed.get("skills", []))
            result["missing_keywords"] = self._extract_list(parsed.get("missing_keywords", []))
            result["match_score"] = self._extract_score(parsed.get("match_score", 0))
            result["summary"] = str(parsed.get("summary", "")).strip()
            result["cover_letter"] = str(parsed.get("cover_letter", "")).strip()
        
        # Fallback extraction if LLM didn't provide good data
        if not result["skills"] or len(result["skills"]) < 3:
            result["skills"] = self._extract_skills_fallback(resume_text)
        
        if not result["summary"]:
            result["summary"] = self._generate_fallback_summary(resume_text, job_desc)
        
        if not result["cover_letter"]:
            result["cover_letter"] = self._generate_fallback_cover_letter(
                personal_info.get("name", "Applicant"), job_desc
            )
        
        # Extract experience and education from resume
        result["experience"] = self._extract_experience(resume_text)
        result["education"] = self._extract_education(resume_text)
        
        return result
    
    def _extract_list(self, data: Any) -> List[str]:
        """Extract list from various formats."""
        if isinstance(data, list):
            return [str(item).strip() for item in data if item and str(item).strip()]
        elif isinstance(data, str):
            return [item.strip() for item in data.split(',') if item.strip()]
        return []
    
    def _extract_score(self, score: Any) -> int:
        """Extract score as integer."""
        try:
            return max(0, min(100, int(float(str(score)))))
        except (ValueError, TypeError):
            return 0
    
    def _extract_skills_fallback(self, resume_text: str) -> List[str]:
        """Extract skills using pattern matching as fallback."""
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'SQL', 'AWS', 'Azure', 'Docker',
            'Kubernetes', 'React', 'Node.js', 'Machine Learning', 'Data Analysis',
            'Project Management', 'Agile', 'Git', 'Linux', 'Communication', 'Leadership'
        ]
        
        found_skills = []
        resume_upper = resume_text.upper()
        
        for skill in common_skills:
            if skill.upper() in resume_upper:
                found_skills.append(skill)
        
        return found_skills[:8] if found_skills else ['Technical Skills', 'Problem Solving', 'Team Collaboration']
    
    def _generate_fallback_summary(self, resume_text: str, job_desc: str) -> str:
        """Generate basic summary as fallback."""
        return ("Experienced professional with demonstrated expertise in technical domains. "
                "Proven ability to deliver results and collaborate effectively with cross-functional teams. "
                "Seeking to contribute skills and drive innovation in a challenging environment.")
    
    def _generate_fallback_cover_letter(self, name: str, job_desc: str) -> str:
        """Generate basic cover letter as fallback."""
        return (f"Dear Hiring Manager,\n\n"
                f"I am writing to express my strong interest in this position. "
                f"With my background in technology and proven track record of success, "
                f"I am confident I can make valuable contributions to your team. "
                f"I look forward to discussing how my skills align with your needs.\n\n"
                f"Best regards,\n{name or 'Applicant'}")
    
    def _extract_experience(self, resume_text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume text."""
        experience = []
        
        # Look for experience section
        exp_pattern = r'(experience|employment|work history)'
        lines = resume_text.split('\n')
        
        in_experience = False
        current_exp = None
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Detect experience section start
            if re.search(exp_pattern, line_lower):
                in_experience = True
                continue
            
            # Detect section end
            if in_experience and re.search(r'(education|skills|certifications)', line_lower):
                if current_exp:
                    experience.append(current_exp)
                break
            
            if in_experience and line.strip():
                # Detect job title/company (typically has uppercase or dates)
                if any(char.isupper() for char in line) or re.search(r'\d{4}', line):
                    if current_exp:
                        experience.append(current_exp)
                    
                    current_exp = {
                        "role": line.strip(),
                        "company": "Company Name",
                        "duration": "",
                        "details": []
                    }
                    
                    # Try to extract year
                    year_match = re.search(r'(\d{4})\s*-\s*(\d{4}|present)', line, re.IGNORECASE)
                    if year_match:
                        current_exp["duration"] = year_match.group(0)
                
                # Bullet points or responsibilities
                elif current_exp and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                    detail = line.lstrip('•-* ').strip()
                    if detail:
                        current_exp["details"].append(detail)
        
        if current_exp:
            experience.append(current_exp)
        
        # If no experience found, create template
        if not experience:
            experience = [{
                "role": "Professional Experience",
                "company": "Previous Employer",
                "duration": "Years",
                "details": [
                    "Led key projects and initiatives",
                    "Collaborated with cross-functional teams",
                    "Delivered measurable results"
                ]
            }]
        
        return experience[:3]  # Limit to 3 most recent
    
    def _extract_education(self, resume_text: str) -> List[Dict[str, str]]:
        """Extract education from resume text."""
        education = []
        
        # Look for education section
        edu_pattern = r'(education|academic|degree)'
        lines = resume_text.split('\n')
        
        in_education = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if re.search(edu_pattern, line_lower):
                in_education = True
                continue
            
            if in_education and re.search(r'(experience|skills|certifications)', line_lower):
                break
            
            if in_education and line.strip():
                # Look for degree indicators
                if any(word in line_lower for word in ['bachelor', 'master', 'phd', 'degree', 'university', 'college']):
                    edu_entry = {"degree": line.strip(), "institution": "", "year": ""}
                    
                    # Extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', line)
                    if year_match:
                        edu_entry["year"] = year_match.group(0)
                    
                    education.append(edu_entry)
        
        # If no education found, create template
        if not education:
            education = [{
                "degree": "Bachelor's Degree",
                "institution": "University",
                "year": ""
            }]
        
        return education[:2]  # Limit to 2 most recent