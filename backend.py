from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import logging
import re
import uuid
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Government Schemes Chatbot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Scheme(BaseModel):
    name: str
    description: str
    eligibility: str
    benefits: str
    application_process: str
    required_documents: str
    state: str
    domain: str
    official_website: str

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    schemes: List[Scheme]
    session_id: str
    timestamp: str

# Government schemes database
SCHEMES_DATABASE = [
    {
        "name": "Kalaignar Magalir Urimai Thogai (Women's Entitlement)",
        "description": "Monthly financial assistance scheme for women heads of households. Provides direct benefit transfer to eligible women.",
        "eligibility": "Women heads of eligible ration card households, TN residents with income criteria as per government norms",
        "benefits": "₹1,000 per month direct benefit transfer",
        "application_process": "Visit nearest village secretariat or ward office. Submit application with required documents. Officials will verify eligibility and process DBT.",
        "required_documents": "Aadhaar card, Ration card, Bank account details",
        "state": "Tamil Nadu",
        "domain": "Women Welfare",
        "official_website": "https://kmut.tn.gov.in/"
    },
    {
        "name": "Moovalur Ramamirtham Ammaiyar 'Pudhumai Penn' Scheme",
        "description": "Financial assistance scheme for girl students pursuing higher education. Encourages girls to continue education by providing monthly stipends.",
        "eligibility": "Girl students from government schools who studied 6th to 12th in government schools, currently pursuing higher education",
        "benefits": "₹1,000 per month for undergraduate studies throughout the course duration",
        "application_process": "Apply through respective college or university admission portal. Submit application form with required documents. College will forward to government for processing.",
        "required_documents": "School certificates, College admission letter, Bank account details, Aadhaar card, Community certificate",
        "state": "Tamil Nadu",
        "domain": "Education",
        "official_website": "https://www.pudhumaipenn.tn.gov.in/"
    },
    {
        "name": "Chief Minister's Comprehensive Health Insurance Scheme (CMCHIS)",
        "description": "Comprehensive health insurance coverage for economically weaker families. Provides cashless medical treatment at empaneled hospitals.",
        "eligibility": "Families with annual income less than ₹1,20,000, priority given to below poverty line families",
        "benefits": "Free medical coverage up to ₹5 lakhs per family per year for secondary and tertiary care",
        "application_process": "Get smart card from nearest Primary Health Centre. Submit family income certificate and other documents. Card issued after verification.",
        "required_documents": "Income certificate, Ration card, Aadhaar card, Family photo",
        "state": "Tamil Nadu",
        "domain": "Health",
        "official_website": "https://www.cmchistn.com/"
    },
    {
        "name": "Free Bus Travel for Women",
        "description": "Free bus travel facility for women and transgender persons in state transport buses. Part of women empowerment initiative.",
        "eligibility": "Women and transgender persons residing in Tamil Nadu",
        "benefits": "Free travel in state-run ordinary buses across Tamil Nadu",
        "application_process": "No separate application required. Board any ordinary state transport bus and show valid government ID proof to conductor.",
        "required_documents": "Any government ID proof (Aadhaar, Voter ID, Driving License)",
        "state": "Tamil Nadu",
        "domain": "Transport",
        "official_website": "https://tnstc.in/"
    },
    {
        "name": "Karunya Arogya Suraksha Padhathi (KASP)",
        "description": "Comprehensive health insurance scheme providing cashless treatment for eligible families. Covers major surgeries and treatments.",
        "eligibility": "Eligible families as per SECC/State lists, priority households identified by government",
        "benefits": "₹5 lakh per family per year cashless treatment for secondary and tertiary care at empaneled hospitals",
        "application_process": "Check eligibility at nearest Aarogya Mithra office. Get health card issued after document verification and eligibility confirmation.",
        "required_documents": "Aadhaar card, Ration card, SECC data verification",
        "state": "Kerala",
        "domain": "Health",
        "official_website": "https://sha.kerala.gov.in/"
    },
    {
        "name": "Kudumbashree",
        "description": "Women empowerment program focusing on community-based approach. Organizes women into self-help groups for economic empowerment.",
        "eligibility": "Women from poor and marginalized families in Kerala, willing to participate in group activities",
        "benefits": "Microcredit facilities, livelihood support, skill development training, entrepreneurship support",
        "application_process": "Contact local Kudumbashree coordinator in your area. Join neighbourhood group (NHG) after orientation and training sessions.",
        "required_documents": "Aadhaar card, Bank account details, Residence proof",
        "state": "Kerala",
        "domain": "Women Welfare",
        "official_website": "https://kudumbashree.org/"
    },
    {
        "name": "DCE Kerala Scholarships",
        "description": "Comprehensive scholarship program for various categories of students. Covers pre-matric, post-matric, merit and minority scholarships.",
        "eligibility": "Students from Kerala belonging to various categories: SC/ST/OBC/Minority communities, merit-based criteria",
        "benefits": "Post-matric, merit, minority and other scholarships ranging from ₹1,000 to ₹20,000 annually",
        "application_process": "Register at DCE scholarship portal online. Fill application form with accurate details and upload required documents.",
        "required_documents": "Income certificate, Caste certificate, Mark sheets, Bank account details",
        "state": "Kerala",
        "domain": "Education",
        "official_website": "https://dcescholarship.kerala.gov.in/"
    },
    {
        "name": "Kerala Farmers' Welfare Fund Board",
        "description": "Welfare scheme providing social security benefits to farmers through contributory fund. Covers pension and welfare benefits.",
        "eligibility": "Farmers meeting definitions in the Kerala Farmers Welfare Fund Act and Rules",
        "benefits": "Pension and welfare benefits through contributory fund, medical assistance, accident coverage",
        "application_process": "Visit nearest agricultural office for registration. Pay prescribed contribution amount as per rules and regulations.",
        "required_documents": "Land documents, Aadhaar card, Bank account details",
        "state": "Kerala",
        "domain": "Agriculture",
        "official_website": "https://kfwfb.kerala.gov.in/"
    },
    {
        "name": "Gruha Lakshmi",
        "description": "Monthly financial assistance scheme for women heads of families. Direct benefit transfer to support household expenses.",
        "eligibility": "Women heads of eligible families with ration cards, Karnataka state criteria as per government guidelines",
        "benefits": "₹2,000 per month direct benefit transfer to eligible women heads of households",
        "application_process": "Apply online at Seva Sindhu portal or visit nearest Seva Kendra for assistance. Submit application with required documents.",
        "required_documents": "Aadhaar card, Ration card, Bank account details",
        "state": "Karnataka",
        "domain": "Women Welfare",
        "official_website": "https://sevasindhugs.karnataka.gov.in/"
    },
    {
        "name": "Shakti (Free Bus Travel for Women)",
        "description": "Free bus travel scheme for women domiciled in Karnataka. Applicable in non-premium state transport buses.",
        "eligibility": "Women domiciled in Karnataka as per government guidelines and verification",
        "benefits": "Free travel in non-premium state-run buses within Karnataka boundaries",
        "application_process": "No separate application required for bus travel. Show any valid ID proof while traveling in state transport buses.",
        "required_documents": "Any government ID proof showing Karnataka address",
        "state": "Karnataka",
        "domain": "Transport",
        "official_website": "https://sevasindhugs.karnataka.gov.in/"
    },
    {
        "name": "Gruha Jyothi",
        "description": "Free electricity scheme for residential consumers in Karnataka. Provides free electricity up to specified units per month.",
        "eligibility": "Residential consumers within sanctioned load and average consumption limits as per government criteria",
        "benefits": "Free electricity up to 200 units per month (subject to terms and conditions)",
        "application_process": "No separate application required. Existing BESCOM/GESCOM consumers automatically enrolled based on eligibility criteria.",
        "required_documents": "Existing electricity connection, Aadhaar card linked to electricity account",
        "state": "Karnataka",
        "domain": "Electricity",
        "official_website": "https://sevasindhugs.karnataka.gov.in/gruhajyothi/"
    },
    {
        "name": "Anna Bhagya",
        "description": "Enhanced food security program providing additional rice to ration cardholders. Supplements National Food Security Act provisions.",
        "eligibility": "Priority/Antyodaya ration cardholders in Karnataka as per government database",
        "benefits": "Additional rice/foodgrain entitlement above NFSA quota at subsidized rates",
        "application_process": "Visit nearest fair price shop with valid ration card. No separate application required for existing cardholders.",
        "required_documents": "Valid ration card, Family member ID proof",
        "state": "Karnataka",
        "domain": "Food Security",
        "official_website": "https://ahara.kar.nic.in/"
    },
    {
        "name": "Majhi Kanya Bhagyashree Scheme",
        "description": "Financial assistance scheme for families with girl children. Provides financial incentives to promote girl child welfare.",
        "eligibility": "Families with annual income below ₹7.5 lakh, maximum 2 girl children per family",
        "benefits": "₹50,000 insurance policy coverage, ₹5,000 cash incentive at different stages",
        "application_process": "Apply at Anganwadi center or district collectorate. Submit birth certificate of girl child with other required documents.",
        "required_documents": "Birth certificate, Income certificate, Residence proof",
        "state": "Maharashtra",
        "domain": "Women Welfare",
        "official_website": "https://womenchild.maharashtra.gov.in/"
    },
    {
        "name": "Shravanbal Seva State Pension Scheme",
        "description": "Monthly pension scheme for elderly citizens of Maharashtra. Provides financial security to senior citizens.",
        "eligibility": "Citizens above 65 years of age, annual family income below ₹21,000",
        "benefits": "Monthly pension ranging from ₹600 to ₹2,000 based on age and income criteria",
        "application_process": "Apply at nearest Tehsildar office or online portal. Submit age proof and income documents for verification.",
        "required_documents": "Age proof, Income certificate, Aadhaar card, Bank account details",
        "state": "Maharashtra",
        "domain": "Social Welfare",
        "official_website": "https://aaplesarkar.mahaonline.gov.in/"
    },
    {
        "name": "Lek Ladki Yojana",
        "description": "Comprehensive scheme for girl children providing financial assistance at different life stages to promote gender equality.",
        "eligibility": "Families with annual income below ₹1 lakh, maximum 2 girl children per family",
        "benefits": "₹5,000 at birth, education assistance at different milestones, marriage assistance",
        "application_process": "Register at time of girl child's birth in hospital. Apply at Anganwadi center with birth certificate and documents.",
        "required_documents": "Birth certificate, Income certificate, School certificates",
        "state": "Maharashtra",
        "domain": "Women Welfare",
        "official_website": "https://womenchild.maharashtra.gov.in/"
    },
    {
        "name": "Rythu Bandhu",
        "description": "Investment support scheme providing financial assistance to farmers for agricultural activities each season.",
        "eligibility": "Landholding farmers in Telangana as per land records and revenue department verification",
        "benefits": "Per-acre investment support each season (₹5,000 per acre per season)",
        "application_process": "Land records automatically verified by revenue department. No separate application required for eligible farmers.",
        "required_documents": "Land documents, Aadhaar card, Bank account details",
        "state": "Telangana",
        "domain": "Agriculture",
        "official_website": "https://rythubandhu.telangana.gov.in/"
    },
    {
        "name": "Aasara Pensions",
        "description": "Comprehensive pension scheme for various vulnerable groups in society. Covers multiple categories of beneficiaries.",
        "eligibility": "Old age pensioners, widows, disabled persons, beedi workers, single women, etc. as per government criteria",
        "benefits": "Monthly pension with category-wise rates ranging from ₹2,016 to ₹3,016",
        "application_process": "Apply at nearest MRO office or Village Secretary. Submit required documents and complete verification process.",
        "required_documents": "Age/disability proof, Income certificate, Aadhaar card, Bank account details",
        "state": "Telangana",
        "domain": "Social Welfare",
        "official_website": "https://www.aasara.telangana.gov.in/"
    },
    {
        "name": "KCR Kit",
        "description": "Comprehensive maternal and child health scheme providing support to pregnant women delivering in government hospitals.",
        "eligibility": "Pregnant women delivering in government hospitals in Telangana",
        "benefits": "Cash benefit ₹12,000 and kit containing mother-baby care items",
        "application_process": "Register pregnancy at nearest government hospital. Get regular check-ups and follow hospital procedures for delivery.",
        "required_documents": "Aadhaar card, Hospital registration, Bank account details",
        "state": "Telangana",
        "domain": "Health",
        "official_website": "https://kcrkit.telangana.gov.in/"
    },
    {
        "name": "Telangana Dalit Bandhu",
        "description": "Unique entrepreneurship support scheme for Dalit families providing capital grant support for business ventures.",
        "eligibility": "Eligible Dalit families identified by government as per survey and selection criteria",
        "benefits": "Capital grant support ₹10 lakh per family to start enterprise/business",
        "application_process": "Wait for official notification for area coverage. Apply when scheme is launched in respective areas.",
        "required_documents": "Caste certificate, Income certificate, Aadhaar card, Business plan",
        "state": "Telangana",
        "domain": "Entrepreneurship",
        "official_website": "https://dalitbandhu.telangana.gov.in/"
    },
    {
        "name": "Aadabidda Nidhi",
        "description": "Monthly financial assistance scheme for women from economically weaker sections to support household expenses.",
        "eligibility": "Women aged 18-59 years, annual family income less than ₹2.5 lakh",
        "benefits": "₹1,500 per month directly transferred to eligible women's bank accounts",
        "application_process": "Apply online through official portal or at village secretariat. Submit application with required documents.",
        "required_documents": "Aadhaar card, Income certificate, Bank account details",
        "state": "Andhra Pradesh",
        "domain": "Women Welfare",
        "official_website": "https://navasakam.ap.gov.in/"
    },
    {
        "name": "Rythu Bharosa",
        "description": "Investment support scheme for farmers providing financial assistance for agricultural activities throughout the year.",
        "eligibility": "Eligible farmer families including tenant farmers under rules and land records verification",
        "benefits": "Annual investment support ₹13,500 (includes PM-KISAN amount) per farmer family",
        "application_process": "Land records verification done automatically by revenue department. No separate application required for eligible farmers.",
        "required_documents": "Land documents, Aadhaar card, Bank account details",
        "state": "Andhra Pradesh",
        "domain": "Agriculture",
        "official_website": "https://spandana.ap.gov.in/"
    },
    {
        "name": "Amma Vodi",
        "description": "Educational support scheme providing assistance to mothers/guardians of school-going children to encourage education.",
        "eligibility": "Mothers/guardians of children in classes I-XII with minimum attendance requirements in government schools",
        "benefits": "Annual assistance ₹15,000 per child for encouraging school enrollment and attendance",
        "application_process": "Children must be enrolled in government schools. Ensure minimum attendance as per government norms.",
        "required_documents": "School enrollment certificate, Attendance records, Aadhaar card, Bank account details",
        "state": "Andhra Pradesh",
        "domain": "Education",
        "official_website": "https://navasakam.ap.gov.in/"
    },
    {
        "name": "NTR Vaidya Seva",
        "description": "Comprehensive health insurance scheme providing cashless treatment to eligible families at empaneled hospitals.",
        "eligibility": "Eligible low-income families with white ration card or as per government income criteria",
        "benefits": "Cashless tertiary care up to ₹5 lakh for listed procedures at network hospitals",
        "application_process": "Check eligibility with white ration card or income criteria. Get health card from nearest hospital or health center.",
        "required_documents": "White ration card/Income certificate, Aadhaar card, Family details",
        "state": "Andhra Pradesh",
        "domain": "Health",
        "official_website": "https://www.ntrvaidyaseva.ap.gov.in/"
    }
]

# Session management
sessions = {}

# FIX: Update the ConversationContext class to include missing attributes
class ConversationContext:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages = []
        self.current_scheme = None
        self.last_schemes = []
        self.last_query_type = None  # ADD THIS LINE
        self.conversation_step = 0   # ADD THIS LINE

# FIX: Also update the get_or_create_session function to handle existing sessions
def get_or_create_session(session_id: Optional[str] = None) -> ConversationContext:
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = ConversationContext(session_id)
    else:
        # Ensure existing sessions have the new attributes
        context = sessions[session_id]
        if not hasattr(context, 'last_query_type'):
            context.last_query_type = None
        if not hasattr(context, 'conversation_step'):
            context.conversation_step = 0
    
    return sessions[session_id]

# FIX: Also fix the uvicorn run command at the bottom
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)  # Changed port to 8001 to match frontend

# Text processing utilities
def extract_keywords(text: str) -> List[str]:
    stop_words = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
        'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
        'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
        'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
        'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
        'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
        'further', 'then', 'once'
    }
    
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return [word for word in words if word not in stop_words and len(word) > 2]

def similarity_score(text1: str, text2: str) -> float:
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

# Query processing functions
def detect_state(query: str) -> Optional[str]:
    state_aliases = {
        'Tamil Nadu': ['tamil nadu', 'tn', 'tamilnadu'],
        'Kerala': ['kerala', 'kl'],
        'Karnataka': ['karnataka', 'kt', 'ka'],
        'Andhra Pradesh': ['andhra pradesh', 'ap', 'andhra'],
        'Telangana': ['telangana', 'ts', 'tg'],
        'Maharashtra': ['maharashtra', 'mh'],
        'Puducherry': ['puducherry', 'pondicherry', 'py']
    }
    
    query_lower = query.lower()
    for state, aliases in state_aliases.items():
        if any(alias in query_lower for alias in aliases):
            return state
    return None

def detect_domain(query: str) -> Optional[str]:
    domain_keywords = {
        'Health': ['health', 'medical', 'hospital', 'insurance', 'treatment', 'healthcare', 'medicine'],
        'Education': ['education', 'scholarship', 'student', 'school', 'college', 'study', 'academic'],
        'Women Welfare': ['women', 'woman', 'girl', 'female', 'mother', 'ladies'],
        'Agriculture': ['agriculture', 'farming', 'farmer', 'crop', 'land', 'agricultural'],
        'Transport': ['transport', 'bus', 'travel', 'free travel', 'transportation'],
        'Social Welfare': ['pension', 'elderly', 'old age', 'disabled', 'welfare'],
        'Food Security': ['food', 'ration', 'rice', 'grain'],
        'Electricity': ['electricity', 'power', 'electric'],
        'Entrepreneurship': ['business', 'enterprise', 'entrepreneurship', 'startup']
    }
    
    query_lower = query.lower()
    for domain, keywords in domain_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            return domain
    return None

def detect_intent(query: str) -> str:
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
        return 'greeting'
    
    if any(word in query_lower for word in ['thank', 'thanks', 'thank you']):
        return 'thanks'
    
    if any(word in query_lower for word in ['eligibility', 'eligible', 'qualify', 'who can apply']):
        return 'eligibility'
    
    if any(word in query_lower for word in ['benefit', 'benefits', 'what do i get', 'what will i get']):
        return 'benefits'
    
    if any(word in query_lower for word in ['apply', 'application', 'how to apply', 'registration', 'register']):
        return 'application'
    
    if any(word in query_lower for word in ['link', 'website', 'official', 'registration link']):
        return 'website'
    
    if any(word in query_lower for word in ['document', 'documents', 'papers', 'required']):
        return 'documents'
    
    if any(word in query_lower for word in ['list', 'show', 'tell me about', 'schemes', 'available']):
        return 'list'
    
    return 'general'

def find_schemes(query: str, state: Optional[str] = None, domain: Optional[str] = None) -> List[Dict]:
    relevant_schemes = []
    query_keywords = extract_keywords(query)
    
    for scheme in SCHEMES_DATABASE:
        score = 0
        
        if similarity_score(query, scheme['name']) > 0.6:
            score += 1000
        
        if state and scheme['state'].lower() == state.lower():
            score += 500
        elif state and scheme['state'].lower() != state.lower():
            continue
        
        if domain and scheme['domain'].lower() == domain.lower():
            score += 300
        elif domain and scheme['domain'].lower() != domain.lower():
            continue
        
        scheme_text = f"{scheme['name']} {scheme['description']} {scheme['domain']}".lower()
        for keyword in query_keywords:
            if keyword in scheme_text:
                score += 50
        
        for word in query_keywords:
            if word in scheme['name'].lower():
                score += 100
        
        if score > 0:
            relevant_schemes.append((score, scheme))
    
    relevant_schemes.sort(key=lambda x: x[0], reverse=True)
    return [scheme for score, scheme in relevant_schemes[:5]]

def generate_response(query: str, schemes: List[Dict], intent: str, context: ConversationContext) -> str:
    query_lower = query.lower()
    
    # Handle greetings and thanks
    if intent == 'greeting':
        context.last_query_type = None
        context.current_scheme = None
        context.conversation_step = 0
        return ("Hello! I can help you find government schemes across Southern Indian states.\n\n"
                "Try asking:\n"
                "• 'Health schemes in Tamil Nadu'\n"
                "• 'Education schemes in Kerala'\n"
                "• 'Women welfare schemes in Karnataka'\n\n"
                "What would you like to know?")

    if intent == 'thanks':
        return "You're welcome! Is there anything else you'd like to know about government schemes?"

    # FIX: Handle follow-up questions when there's a current scheme selected
    if context.current_scheme:
        # Check if this is a follow-up question about the current scheme
        is_follow_up = any(word in query_lower for word in [
            'eligibility', 'benefits', 'application', 'process', 'website', 'documents',
            'qualify', 'apply', 'how to', 'required', 'link', 'portal'
        ]) or len(query.strip()) < 15  # Short queries are likely follow-ups
        
        if is_follow_up:
            scheme = context.current_scheme
            context.last_query_type = 'specific_info'
            
            if any(word in query_lower for word in ['eligibility', 'eligible', 'qualify', 'criteria', 'who can']):
                return f"**Eligibility for {scheme['name']}:**\n\n{scheme['eligibility']}"
            elif any(word in query_lower for word in ['benefit', 'benefits', 'what do i get', 'advantages']):
                return f"**Benefits of {scheme['name']}:**\n\n{scheme['benefits']}"
            elif any(word in query_lower for word in ['apply', 'application', 'process', 'how to', 'registration']):
                return f"**How to apply for {scheme['name']}:**\n\n{scheme['application_process']}"
            elif any(word in query_lower for word in ['website', 'link', 'official', 'portal', 'online']):
                return f"**Official website for {scheme['name']}:**\n\n{scheme['official_website']}"
            elif any(word in query_lower for word in ['document', 'documents', 'required', 'papers', 'proof']):
                return f"**Required documents for {scheme['name']}:**\n\n{scheme['required_documents']}"
            else:
                # Default to showing description again
                return (f"**{scheme['name']}**\n\n"
                       f"**Description:** {scheme['description']}\n\n"
                       "What would you like to know about this scheme?\n"
                       "• Eligibility criteria\n"
                       "• Benefits offered\n"
                       "• Application process\n"
                       "• Required documents\n"
                       "• Official website")

    # Handle direct scheme + info queries like "CMCHIS eligibility"
    if not context.current_scheme and intent in ['eligibility', 'benefits', 'application', 'website', 'documents']:
        # Try to find the scheme mentioned in the query
        for scheme in SCHEMES_DATABASE:
            scheme_name_lower = scheme['name'].lower()
            if any(word in query_lower for word in scheme_name_lower.split() if len(word) > 4):
                context.current_scheme = scheme
                context.last_schemes = [scheme]
                context.last_query_type = 'specific_info'
                
                if intent == 'eligibility':
                    return f"**Eligibility for {scheme['name']}:**\n\n{scheme['eligibility']}"
                elif intent == 'benefits':
                    return f"**Benefits of {scheme['name']}:**\n\n{scheme['benefits']}"
                elif intent == 'application':
                    return f"**How to apply for {scheme['name']}:**\n\n{scheme['application_process']}"
                elif intent == 'website':
                    return f"**Official website for {scheme['name']}:**\n\n{scheme['official_website']}"
                elif intent == 'documents':
                    return f"**Required documents for {scheme['name']}:**\n\n{scheme['required_documents']}"

    # Handle scheme selection from previous list
    if context.last_query_type == 'list' and context.last_schemes:
        if query.strip().isdigit():
            try:
                scheme_index = int(query.strip()) - 1
                if 0 <= scheme_index < len(context.last_schemes):
                    selected_scheme = context.last_schemes[scheme_index]
                    context.current_scheme = selected_scheme
                    context.last_query_type = 'scheme_detail'
                    return (f"**{selected_scheme['name']}**\n\n"
                           f"**Description:** {selected_scheme['description']}\n\n"
                           "What would you like to know about this scheme?\n"
                           "• Eligibility criteria\n"
                           "• Benefits offered\n" 
                           "• Application process\n"
                           "• Required documents\n"
                           "• Official website")
                else:
                    return f"Please select a number between 1 and {len(context.last_schemes)}."
            except ValueError:
                pass
        else:
            # Try to match scheme name from the last list
            for scheme in context.last_schemes:
                if any(word in query_lower for word in scheme['name'].lower().split() if len(word) > 4):
                    context.current_scheme = scheme
                    context.last_query_type = 'scheme_detail'
                    return (f"**{scheme['name']}**\n\n"
                           f"**Description:** {scheme['description']}\n\n"
                           "What would you like to know about this scheme?\n"
                           "• Eligibility criteria\n"
                           "• Benefits offered\n"
                           "• Application process\n"
                           "• Required documents\n"
                           "• Official website")

    # For state+domain queries, ONLY list names
    if schemes:
        context.last_schemes = schemes
        context.last_query_type = 'list'
        context.current_scheme = None
        
        scheme_names = []
        for i, scheme in enumerate(schemes, 1):
            scheme_names.append(f"{i}. {scheme['name']} ({scheme['state']})")
        
        schemes_text = "\n".join(scheme_names)
        
        if len(schemes) == 1:
            return (f"I found 1 scheme matching your query:\n\n"
                   f"{schemes_text}\n\n"
                   "Type the number or scheme name to get more details.")
        else:
            return (f"I found {len(schemes)} schemes matching your query:\n\n"
                   f"{schemes_text}\n\n"
                   "Which scheme would you like to know about? (Type the number or scheme name)")

    # No schemes found
    return ("I couldn't find any schemes matching your query.\n\n"
            "Try being more specific:\n"
            "• 'Health schemes in Tamil Nadu'\n"
            "• 'Education scholarships in Kerala'\n"
            "• 'Women welfare schemes in Karnataka'")

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Government Schemes Chatbot API",
        "version": "1.0.0",
        "status": "active",
        "supported_states": ["Tamil Nadu", "Kerala", "Karnataka", "Andhra Pradesh", "Telangana", "Maharashtra", "Puducherry"],
        "total_schemes": len(SCHEMES_DATABASE)
    }

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Received query: {query}")
        
        # Get or create session
        context = get_or_create_session(request.session_id)
        
        # Add user message to context
        context.messages.append({
            "role": "user",
            "content": query,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process query
        detected_state = detect_state(query)
        detected_domain = detect_domain(query)
        intent = detect_intent(query)
        
        logger.info(f"Detected - State: {detected_state}, Domain: {detected_domain}, Intent: {intent}")
        
        # Handle scheme selection from numbered list
        if query.strip().isdigit() and context.last_schemes:
            try:
                scheme_index = int(query.strip()) - 1
                if 0 <= scheme_index < len(context.last_schemes):
                    selected_scheme = context.last_schemes[scheme_index]
                    context.current_scheme = selected_scheme
                    schemes = [selected_scheme]
                    response_text = (f"You selected **{selected_scheme['name']}** from {selected_scheme['state']}.\n\n"
                                   f"**Description:** {selected_scheme['description']}\n\n"
                                   "What would you like to know about this scheme?\n"
                                   "• Eligibility criteria\n"
                                   "• Benefits offered\n"
                                   "• Application process\n"
                                   "• Required documents\n"
                                   "• Official website")
                else:
                    schemes = []
                    response_text = f"Please select a number between 1 and {len(context.last_schemes)}."
            except ValueError:
                schemes = find_schemes(query, detected_state, detected_domain)
                response_text = generate_response(query, schemes, intent, context)
        else:
            # Find relevant schemes
            schemes = find_schemes(query, detected_state, detected_domain)
            response_text = generate_response(query, schemes, intent, context)
        
        # Add assistant response to context
        context.messages.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat(),
            "schemes": schemes
        })
        
        # Convert schemes to Scheme objects
        scheme_objects = [Scheme(**scheme) for scheme in schemes]
        
        return QueryResponse(
            response=response_text,
            schemes=scheme_objects,
            session_id=context.session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing your request: {str(e)}")

@app.get("/schemes")
async def get_all_schemes():
    """Get all available schemes"""
    return {
        "total_schemes": len(SCHEMES_DATABASE),
        "schemes": [Scheme(**scheme) for scheme in SCHEMES_DATABASE]
    }

@app.get("/schemes/states")
async def get_states():
    """Get all available states"""
    states = list(set(scheme['state'] for scheme in SCHEMES_DATABASE))
    return {"states": sorted(states)}

@app.get("/schemes/domains")
async def get_domains():
    """Get all available domains/categories"""
    domains = list(set(scheme['domain'] for scheme in SCHEMES_DATABASE))
    return {"domains": sorted(domains)}

@app.get("/schemes/search")
async def search_schemes(state: Optional[str] = None, domain: Optional[str] = None, keyword: Optional[str] = None):
    """Search schemes with filters"""
    filtered_schemes = SCHEMES_DATABASE.copy()
    
    if state:
        filtered_schemes = [s for s in filtered_schemes if s['state'].lower() == state.lower()]
    
    if domain:
        filtered_schemes = [s for s in filtered_schemes if s['domain'].lower() == domain.lower()]
    
    if keyword:
        keyword_lower = keyword.lower()
        filtered_schemes = [
            s for s in filtered_schemes 
            if keyword_lower in s['name'].lower() or 
               keyword_lower in s['description'].lower() or 
               keyword_lower in s['domain'].lower()
        ]
    
    return {
        "total_found": len(filtered_schemes),
        "schemes": [Scheme(**scheme) for scheme in filtered_schemes]
    }

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"Session {session_id} cleared successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

# ... all your existing backend code ...

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(sessions),
        "total_schemes": len(SCHEMES_DATABASE)
    }

# FIXED: Correct uvicorn run command
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8001, reload=True)