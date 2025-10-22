import os
import json
import re
try:
    import PyPDF2
except ImportError:
    print("Installing PyPDF2...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'PyPDF2'])
    import PyPDF2

class HealthcarePDFHandler:
    def __init__(self):
        self.pdf_path = self._get_pdf_path()
        self.content = None
        self.remedies_db = {}
        
        # FIX: Add multilingual medical term mappings (English -> Multiple languages)
        self.medical_terms_map = {
            'fever': ['fever', 'temperature', 'jwara', 'ಜ್ವರ', 'बुखार', 'bukhar', 'taap'],
            'headache': ['headache', 'head pain', 'thalai vali', 'తలనొప్పి', 'sir dard', 'सिर दर्द', 'ತಲೆನೋವು'],
            'cough': ['cough', 'coughing', 'kemmu', 'ಕೆಮ್ಮು', 'खांसी', 'khansi'],
            'cold': ['cold', 'flu', 'सर्दी', 'sardi', 'ಶೀತ', 'chilly'],
            'sore throat': ['sore throat', 'throat pain', 'गले में दर्द', 'gale me dard'],
            'stomach': ['stomach', 'stomach pain', 'abdominal', 'पेट', 'pet', 'hotte', 'ಹೊಟ್ಟೆ'],
            'nausea': ['nausea', 'vomiting', 'उल्टी', 'ulti', 'vomit'],
            'diarrhea': ['diarrhea', 'loose motion', 'दस्त', 'dast', 'ಅತಿಸಾರ'],
            'constipation': ['constipation', 'कब्ज', 'kabj', 'ಮಲಬದ್ಧತೆ'],
            'pain': ['pain', 'ache', 'दर्द', 'dard', 'ನೋವು', 'novu'],
            'acne': ['acne', 'pimple', 'मुंहासे', 'muhasे'],
            'cut': ['cut', 'wound', 'घाव', 'ghav', 'ಗಾಯ'],
            'burn': ['burn', 'जलन', 'jalan', 'ಸುಟ್ಟ'],
            'bruise': ['bruise', 'चोट', 'chot'],
            'insomnia': ['insomnia', 'sleeplessness', 'अनिद्रा', 'anidra'],
            'anxiety': ['anxiety', 'stress', 'चिंता', 'chinta', 'ಆತಂಕ']
        }
        
    def _get_pdf_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, '..', 'healthcare_data', 'Home_Remedies_Guide.pdf')
    
    def extract_and_process_content(self):
        """Extract and process PDF content into structured remedies"""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_content = ""
                
                print(f"📖 Reading PDF with {len(pdf_reader.pages)} pages...")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    full_content += page_text + "\n"
                    print(f"✅ Processed page {page_num + 1}")
                
                self.content = full_content
                self._parse_remedies()
                return True
                
        except Exception as e:
            print(f"❌ Error extracting PDF: {e}")
            return False
    
    def _parse_remedies(self):
        """Parse the PDF content to extract structured remedies"""
        if not self.content:
            return
        
        # Split content into sections and look for remedy patterns
        lines = self.content.split('\n')
        current_condition = None
        current_remedies = []
        
        # Use keys from medical terms map
        condition_keywords = list(self.medical_terms_map.keys())
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains a condition (English keywords only for structure)
            for keyword in condition_keywords:
                if keyword.lower() in line.lower():
                    if current_condition and current_remedies:
                        self.remedies_db[current_condition] = current_remedies
                    current_condition = keyword
                    current_remedies = []
                    break
            
            # Look for remedy patterns
            if any(word in line.lower() for word in ['remedy', 'treatment', 'cure', 'relief', 'help']):
                if current_condition:
                    current_remedies.append(line)
            elif line and current_condition and len(line) > 20:  # Likely a remedy description
                current_remedies.append(line)
        
        # Add the last condition
        if current_condition and current_remedies:
            self.remedies_db[current_condition] = current_remedies
        
        print(f"📚 Parsed {len(self.remedies_db)} health conditions from PDF")
    
    def _normalize_query(self, user_query):
        """
        FIX: Normalize user query to handle multilingual medical terms
        Convert any language medical term to English for matching
        """
        normalized_terms = []
        user_query_lower = user_query.lower()
        
        # Check each word in query against medical terms map
        for english_term, translations in self.medical_terms_map.items():
            for translation in translations:
                if translation.lower() in user_query_lower:
                    normalized_terms.append(english_term)
                    break
        
        # Also include original query words
        normalized_terms.extend(user_query_lower.split())
        
        return ' '.join(normalized_terms)
    
    def get_remedies_for_condition(self, user_query):
        """Get relevant remedies based on user query - ENHANCED for multilingual support"""
        if not self.remedies_db:
            self.extract_and_process_content()
        
        # FIX: Normalize query to handle multilingual terms
        normalized_query = self._normalize_query(user_query)
        user_query_lower = user_query.lower()
        
        print(f"🔍 Original query: {user_query}")
        print(f"🔍 Normalized query: {normalized_query}")
        
        matching_remedies = []
        matched_conditions = []
        
        # Direct keyword matching with normalization
        for condition, remedies in self.remedies_db.items():
            # Check if normalized query contains this condition
            if condition.lower() in normalized_query:
                matching_remedies.extend(remedies)
                matched_conditions.append(condition)
                print(f"✅ Matched condition: {condition}")
        
        # If no direct match, try fuzzy matching with all synonyms
        if not matching_remedies:
            print("🔍 No direct match, trying multilingual matching...")
            for english_term, translations in self.medical_terms_map.items():
                for translation in translations:
                    if translation.lower() in user_query_lower:
                        if english_term in self.remedies_db:
                            matching_remedies.extend(self.remedies_db[english_term])
                            matched_conditions.append(english_term)
                            print(f"✅ Matched via translation '{translation}' -> '{english_term}'")
                            break
        
        # If still no match, search in all content
        if not matching_remedies and self.content:
            print("🔍 No match found, searching full content...")
            content_lines = self.content.split('\n')
            search_terms = normalized_query.split()
            
            for line in content_lines:
                if any(term in line.lower() for term in search_terms):
                    if len(line.strip()) > 20:  # Meaningful content
                        matching_remedies.append(line.strip())
                    if len(matching_remedies) >= 5:  # Limit results
                        break
        
        if matching_remedies:
            print(f"✅ Found {len(matching_remedies)} remedies for conditions: {', '.join(matched_conditions)}")
        else:
            print("❌ No remedies found")
        
        return matching_remedies[:5] if matching_remedies else None

# Global instance
pdf_handler = HealthcarePDFHandler()

def get_healthcare_response_from_pdf(user_query, user_name="there"):
    """Main function to get healthcare response from PDF"""
    try:
        remedies = pdf_handler.get_remedies_for_condition(user_query)
        
        if remedies:
            remedies_text = "\n".join([f"• {remedy}" for remedy in remedies])
            
            response = f"""Hello {user_name}! 👋 Based on your query about "{user_query}", here's what I found in our healthcare guide:

📚 From Home Remedies Guide:
{remedies_text}

⚠️ Important Medical Disclaimer:
These are traditional home remedies for informational purposes only. Always consult with a healthcare professional for proper medical advice, especially for persistent or severe symptoms.

🏥 When to See a Doctor:
• If symptoms persist for more than a few days
• If symptoms worsen or become severe
• If you have underlying health conditions
• If you're unsure about the severity

Follow-up Questions:
• What other symptoms should I watch for?
• How long should I try these remedies?
• Are there any side effects to be aware of?"""

            return response
        else:
            return f"""Hello {user_name}! 👋 

I couldn't find specific information about "{user_query}" in our current healthcare guide. 

For your health and safety, I recommend:
• 🏥 Consult with a healthcare professional
• 📞 Call a medical helpline  
• 💊 Visit your local pharmacy for advice
• 🌐 Check reputable medical websites

If this is urgent, please seek immediate medical attention.

Is there anything else about general wellness I can help you with? 💙"""
            
    except Exception as e:
        print(f"❌ Error in get_healthcare_response_from_pdf: {e}")
        return f"Hello {user_name}! I'm having some technical difficulties accessing the healthcare information right now. For your safety, please consult a healthcare professional. 🏥"
