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
        
        condition_keywords = ['headache', 'cough', 'cold', 'fever', 'sore throat', 
                             'stomach', 'nausea', 'diarrhea', 'constipation', 'pain',
                             'acne', 'cut', 'burn', 'bruise', 'insomnia', 'anxiety']
        
        for line in lines:
            line = line.strip()
            if not line:
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
            if any(word in line.lower() for word in ['remedy', 'treatment', 'cure', 'relief', 'help']):
                if current_condition:
                    current_remedies.append(line)
            elif line and current_condition and len(line) > 20:  # Likely a remedy description
                current_remedies.append(line)
        
        # Add the last condition
        if current_condition and current_remedies:
            self.remedies_db[current_condition] = current_remedies
        
        print(f"📚 Parsed {len(self.remedies_db)} health conditions from PDF")
    
    def get_remedies_for_condition(self, user_query):
        """Get relevant remedies based on user query"""
        if not self.remedies_db:
            self.extract_and_process_content()
        
        user_query_lower = user_query.lower()
        matching_remedies = []
        
        # Direct keyword matching
        for condition, remedies in self.remedies_db.items():
            if condition.lower() in user_query_lower or any(word in user_query_lower for word in condition.split()):
                matching_remedies.extend(remedies)
        
        # If no direct match, search in all content
        if not matching_remedies and self.content:
            content_lines = self.content.split('\n')
            for line in content_lines:
                if any(word in line.lower() for word in user_query_lower.split()):
                    if len(line.strip()) > 20:  # Meaningful content
                        matching_remedies.append(line.strip())
                    if len(matching_remedies) >= 5:  # Limit results
                        break
        
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

**📚 From Home Remedies Guide:**
{remedies_text}

**⚠️ Important Medical Disclaimer:**
These are traditional home remedies for informational purposes only. Always consult with a healthcare professional for proper medical advice, especially for persistent or severe symptoms.

**🏥 When to See a Doctor:**
• If symptoms persist for more than a few days
• If symptoms worsen or become severe
• If you have underlying health conditions
• If you're unsure about the severity

**Follow-up Questions:**
• What other symptoms should I watch for?
• How long should I try these remedies?
• Are there any side effects to be aware of?"""

            return response
        else:
            return f"""Hello {user_name}! 👋 

I couldn't find specific information about "{user_query}" in our current healthcare guide. 

**For your health and safety, I recommend:**
• 🏥 Consult with a healthcare professional
• 📞 Call a medical helpline  
• 💊 Visit your local pharmacy for advice
• 🌐 Check reputable medical websites

**If this is urgent, please seek immediate medical attention.**

Is there anything else about general wellness I can help you with? 💙"""
            
    except Exception as e:
        return f"Hello {user_name}! I'm having some technical difficulties accessing the healthcare information right now. For your safety, please consult a healthcare professional. 🏥"