import spacy
import nltk
from typing import Dict, List, Any, Optional
from collections import Counter
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from dataclasses import dataclass, asdict

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

@dataclass
class ICPAttributes:
    """Dataclass to store ICP attributes with default values"""
    industry_focus: str = ""
    company_size: str = "Unknown"
    key_decision_makers: str = ""
    geographic_focus: str = ""
    technical_sophistication: str = "Unknown"
    budget_level: str = "Unknown"
    buying_cycle: str = "Unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the dataclass instance to a dictionary"""
        return asdict(self)

class ContentProcessor:
    def __init__(self):
        """Initialize the content processor with NLP tools and LLM"""
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize LLM if API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OpenAI API key not found. LLM analysis will be disabled.")
            self.llm = None
        else:
            try:
                self.llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.2
                )
            except Exception as e:
                logger.error(f"Error initializing LLM: {str(e)}")
                self.llm = None
        
        self.output_parser = PydanticOutputParser(pydantic_object=ICPAttributes)
        
    def process_content(self, scraped_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process scraped content to extract ICP information
        
        Args:
            scraped_content: Dictionary containing scraped website content
            
        Returns:
            Dictionary containing processed ICP information
        """
        try:
            # Combine relevant content for analysis
            combined_text = self._combine_content(scraped_content)
            
            # Extract initial insights using spaCy
            doc = self.nlp(combined_text)
            
            # Extract entities and key phrases
            entities = self._extract_entities(doc)
            key_phrases = self._extract_key_phrases(doc)
            
            # Use LangChain for advanced analysis if available
            if self.llm:
                try:
                    icp_analysis = self._analyze_with_llm(combined_text)
                except Exception as e:
                    logger.error(f"Error in LLM analysis: {str(e)}")
                    icp_analysis = ICPAttributes()
            else:
                logger.info("Skipping LLM analysis (no valid API key)")
                icp_analysis = ICPAttributes()
            
            return {
                'entities': entities,
                'key_phrases': key_phrases,
                'icp_analysis': icp_analysis.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error processing content: {str(e)}")
            return {
                'entities': {},
                'key_phrases': [],
                'icp_analysis': ICPAttributes().to_dict()
            }
            
    def _combine_content(self, scraped_content: Dict[str, Any]) -> str:
        """Combine relevant content sections for analysis"""
        sections = [
            scraped_content.get('title', ''),
            scraped_content.get('meta_description', ''),
            scraped_content.get('main_content', ''),
            scraped_content.get('about_page', '')
        ]
        
        # Add target sections
        target_sections = scraped_content.get('target_sections', {})
        sections.extend(target_sections.values())
        
        return ' '.join(filter(None, sections))
        
    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """Extract named entities from the text"""
        entities = {
            'organizations': [],
            'locations': [],
            'products': [],
            'job_titles': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                entities['organizations'].append(ent.text)
            elif ent.label_ == 'GPE':
                entities['locations'].append(ent.text)
            elif ent.label_ == 'PRODUCT':
                entities['products'].append(ent.text)
            
        return {k: list(set(v)) for k, v in entities.items()}
        
    def _extract_key_phrases(self, doc) -> List[str]:
        """Extract important phrases using noun chunks and verb phrases"""
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]
        
        # Extract verb phrases
        verb_phrases = []
        for token in doc:
            if token.pos_ == "VERB":
                phrase = token.text
                for child in token.children:
                    if child.dep_ in ['dobj', 'pobj']:
                        phrase = f"{phrase} {child.text}"
                        verb_phrases.append(phrase)
                        
        return list(set(noun_chunks + verb_phrases))
        
    def _analyze_with_llm(self, text: str) -> ICPAttributes:
        """Use LangChain and GPT-4 to analyze the content for ICP information"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert business analyst specializing in identifying Ideal Customer Profiles (ICP) from website content."),
            ("user", """Analyze the following website content and extract key information about the company's Ideal Customer Profile (ICP).
            Focus on identifying:
            1. Industry focus
            2. Target company size
            3. Key decision makers
            4. Geographic focus
            5. Technical sophistication level
            6. Budget level
            7. Typical buying cycle

            Website content:
            {content}

            Provide your analysis in a structured format that can be easily parsed.""")
        ])
        
        chain = prompt | self.llm
        
        try:
            result = chain.invoke({"content": text[:4000]})  # Limit content length
            return ICPAttributes(
                industry_focus=str(result.content).split("1.")[1].split("2.")[0].strip() if "1." in str(result.content) else "",
                company_size=str(result.content).split("2.")[1].split("3.")[0].strip() if "2." in str(result.content) else "Unknown",
                key_decision_makers=str(result.content).split("3.")[1].split("4.")[0].strip() if "3." in str(result.content) else "",
                geographic_focus=str(result.content).split("4.")[1].split("5.")[0].strip() if "4." in str(result.content) else "",
                technical_sophistication=str(result.content).split("5.")[1].split("6.")[0].strip() if "5." in str(result.content) else "Unknown",
                budget_level=str(result.content).split("6.")[1].split("7.")[0].strip() if "6." in str(result.content) else "Unknown",
                buying_cycle=str(result.content).split("7.")[1].strip() if "7." in str(result.content) else "Unknown"
            )
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return ICPAttributes() 