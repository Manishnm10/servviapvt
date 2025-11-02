import os
import json
import re
from difflib import SequenceMatcher
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
        self.full_text_index = []  # For fuzzy search
        
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
                    print(f"   ✅ Page {page_num + 1}")
                
                self.content = full_content
                self._parse_remedies()
                self._build_text_index()
                return True
                
        except Exception as e:
            print(f"❌ Error extracting PDF: {e}")
            return False
    
    def _parse_remedies(self):
        """Parse the PDF content to extract structured remedies"""
        if not self.content:
            return
        
        lines = self.content.split('\n')
        current_condition = None
        current_remedies = []
        
        # Common health condition keywords
        condition_keywords = ['headache', 'cough', 'cold', 'fever', 'sore throat', 
                             'stomach', 'nausea', 'diarrhea', 'constipation', 'pain',
                             'acne', 'cut', 'burn', 'bruise', 'insomnia', 'anxiety',
                             'flu', 'infection', 'inflammation']
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
                
            # Check if line contains a condition
            for keyword in condition_keywords:
                if keyword.lower() in line.lower():
                    if current_condition and current_remedies:
                        self.remedies_db[current_condition] = current_remedies
                    current_condition = keyword
                    current_remedies = []
                    break
            
            # Look for remedy patterns
            if any(word in line.lower() for word in ['remedy', 'treatment', 'cure', 'relief', 'help', 'drink', 'apply', 'use']):
                if current_condition:
                    current_remedies.append(line)
            elif line and current_condition and len(line) > 30:  # Likely remedy description
                current_remedies.append(line)
        
        # Add the last condition
        if current_condition and current_remedies:
            self.remedies_db[current_condition] = current_remedies
        
        print(f"📚 Parsed {len(self.remedies_db)} conditions: {', '.join(self.remedies_db.keys())}")
    
    def _build_text_index(self):
        """Build searchable text index for fuzzy matching"""
        if not self.content:
            return
        
        # Split into meaningful chunks
        lines = [l.strip() for l in self.content.split('\n') if len(l.strip()) > 20]
        self.full_text_index = lines
        print(f"📇 Built text index with {len(self.full_text_index)} searchable lines")
    
    def _fuzzy_match(self, query_word, text, threshold=0.6):
        """Fuzzy match a word in text using sequence matching"""
        query_lower = query_word.lower()
        text_lower = text.lower()
        
        # Direct substring match
        if query_lower in text_lower:
            return 1.0
        
        # Word-by-word fuzzy match
        words = text_lower.split()
        best_match = 0
        for word in words:
            ratio = SequenceMatcher(None, query_lower, word).ratio()
            if ratio > best_match:
                best_match = ratio
        
        return best_match if best_match >= threshold else 0
    
    def get_remedies_for_condition(self, user_query):
        """
        Get relevant remedies based on user query using Google Translate results.
        No hardcoded mappings - pure semantic search.
        """
        if not self.remedies_db:
            self.extract_and_process_content()
        
        user_query_lower = user_query.lower()
        query_words = [w for w in user_query_lower.split() if len(w) > 2]
        
        print(f"\n🔍 Searching PDF for: '{user_query}'")
        print(f"   Query words: {query_words}")
        
        matching_remedies = []
        matched_conditions = []
        match_scores = {}
        
        # Strategy 1: Direct condition keyword matching
        for condition, remedies in self.remedies_db.items():
            score = 0
            # Check if any query word matches condition
            for word in query_words:
                if word in condition.lower():
                    score += 1.0
                else:
                    # Fuzzy match
                    fuzzy_score = self._fuzzy_match(word, condition)
                    score += fuzzy_score
            
            if score > 0.5:
                matching_remedies.extend(remedies)
                matched_conditions.append(condition)
                match_scores[condition] = score
                print(f"   ✅ Matched condition: '{condition}' (score: {score:.2f})")
        
        # Strategy 2: Full-text search in PDF if no direct matches
        if not matching_remedies:
            print("   🔍 No direct matches, trying full-text search...")
            
            for line in self.full_text_index:
                line_score = 0
                for word in query_words:
                    line_score += self._fuzzy_match(word, line, threshold=0.5)
                
                if line_score > 1.0:  # At least 1 good match
                    matching_remedies.append(line)
                    if len(matching_remedies) >= 5:
                        break
            
            if matching_remedies:
                print(f"   ✅ Found {len(matching_remedies)} matches via full-text search")
        
        # Strategy 3: If still nothing, search for individual important words
        if not matching_remedies:
            print("   🔍 Trying individual keyword search...")
            important_words = [w for w in query_words if len(w) > 4]  # Longer words are more meaningful
            
            if important_words:
                for line in self.full_text_index:
                    if any(word in line.lower() for word in important_words):
                        matching_remedies.append(line)
                        if len(matching_remedies) >= 5:
                            break
        
        if matching_remedies:
            print(f"✅ Found {len(matching_remedies)} total remedies")
            if matched_conditions:
                print(f"   Conditions: {', '.join(matched_conditions)}")
        else:
            print("❌ No remedies found")
        
        return matching_remedies[:5] if matching_remedies else None

# Global instance
pdf_handler = HealthcarePDFHandler()

def get_healthcare_response_from_pdf(user_query, user_name="there"):
    """Main function to get healthcare response from PDF using pure search"""
    try:
        print(f"\n🏥 Processing: '{user_query}' for {user_name}")
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

            print(f"✅ Response generated with {len(remedies)} remedies\n")
            return response
        else:
            print(f"⚠️ No remedies found\n")
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
        print(f"❌ Error: {e}\n")
        return f"Hello {user_name}! I'm having some technical difficulties accessing the healthcare information right now. For your safety, please consult a healthcare professional. 🏥"