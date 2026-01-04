// Images des membres de l'equipe
import BROUKIAya from '../assets/photo/BROUKIAya.png';
import ELOUMNINora from '../assets/photo/ELOUMNINora.png';
import KHAILAImane from '../assets/photo/KHAILAImane.png';
import KHARFASSEHiba from '../assets/photo/KHARFASSEHiba.png';
import KayouhSalah from '../assets/photo/KAYOUHSalaheddine.png';
import OUANADHafsa from '../assets/photo/OUANADHafsa.png';
import YAHYAZakariae from '../assets/photo/YAHYAZakariae.png';

export const TEAM_MEMBERS = [
  {
    id: 1,
    name: 'KAYOUH Salaheddine',
    role: 'Project Manager',
    responsibilities: 'Planning, coordination, integration',
    color: '#FF6B6B',
    image: KayouhSalah
  },
  {
    id: 2,
    name: 'YAHYA Zakariae',
    role: 'Data Engineer',
    responsibilities: 'Scraping, preprocessing',
    color: '#4ECDC4',
    image: YAHYAZakariae
  },
  {
    id: 3,
    name: 'EL OUMNI Nora',
    role: 'Data Engineer',
    responsibilities: 'Database, ETL',
    color: '#45B7D1',
    image: ELOUMNINora
  },
  {
    id: 4,
    name: 'KHARFASSE Hiba',
    role: 'NLP Engineer',
    responsibilities: 'Modeles de sentiment',
    color: '#FFA07A',
    image: KHARFASSEHiba
  },
  {
    id: 5,
    name: 'OUANAD Hafsa',
    role: 'NLP Engineer',
    responsibilities: 'Fine-tuning, evaluation',
    color: '#98D8C8',
    image: OUANADHafsa
  },
  {
    id: 6,
    name: 'HIDA Mohammed',
    role: 'Data Analyst',
    responsibilities: 'Correlations, statistiques',
    color: '#F7DC6F',
    image: null
  },
  {
    id: 7,
    name: 'KHAILA Imane',
    role: 'Data Analyst',
    responsibilities: 'Visualisations, insights',
    color: '#BB8FCE',
    image: KHAILAImane
  },
  {
    id: 8,
    name: 'BROUKI Aya',
    role: 'DevOps Engineer',
    responsibilities: 'Dashboard, deploiement',
    color: '#85C1E2',
    image: BROUKIAya
  }
];

export const TECH_STACK = [
  { category: 'Backend', tech: ['Python', 'FastAPI', 'Airflow'] },
  { category: 'Frontend', tech: ['React', 'JavaScript', 'Recharts'] },
  { category: 'Data Processing', tech: ['Pandas', 'NumPy', 'Scikit-learn'] },
  { category: 'NLP & ML', tech: ['Transformers', 'FinBERT', 'PyTorch'] },
  { category: 'RAG Chatbot', tech: ['Pinecone', 'Groq LLM', 'LangChain'] },
  { category: 'Evaluation', tech: ['RAGAS', 'Sentence-Transformers'] }
];

export const FEATURES = [
  {
    icon: '🔍',
    title: 'Extraction de Donnees',
    description: 'Collecte de donnees depuis Twitter et Reddit via API'
  },
  {
    icon: '🧠',
    title: 'Analyse NLP',
    description: 'Modeles FinBERT fine-tunes pour le sentiment crypto'
  },
  {
    icon: '📊',
    title: 'Correlation Prix/Sentiment',
    description: 'Analyse Pearson et lag temporel'
  },
  {
    icon: '📈',
    title: 'Dashboard Interactif',
    description: 'Visualisations temps reel avec Recharts'
  },
  {
    icon: '🤖',
    title: 'Chatbot RAG',
    description: 'Assistant IA avec Pinecone + Groq LLM'
  },
  {
    icon: '📝',
    title: 'Evaluation RAGAS',
    description: 'Metriques de qualite: Faithfulness, Relevancy'
  }
];

export const PROJECT_INFO = {
  title: 'A Propos du Projet',
  tagline: 'Analyse avancee du sentiment et correlation avec les prix des cryptomonnaies',
  teamIntro: '8 experts passionnes par les donnees et l\'innovation'
};
