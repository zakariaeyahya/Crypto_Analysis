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
    role: 'Project Manager & Team Lead',
    responsibilities: 'Project management, Agile, coordination, intégration',
    image: KayouhSalah,
    linkedin: 'https://www.linkedin.com/in/salaheddine-kayouh/',
    github: 'https://github.com/771salameche'
  },
  {
    id: 2,
    name: 'YAHYA Zakariae',
    role: 'Data Engineer',
    responsibilities: 'Scraping, data preprocessing, RAG, fine-tuning',
    image: YAHYAZakariae,
    linkedin: 'https://www.linkedin.com/in/zakariae-yahya/',
    github: 'https://github.com/zakariaeyahya'
  },
  {
    id: 3,
    name: 'EL OUMNI Nora',
    role: 'Data Analyst',
    responsibilities: 'Correlation analysis, statistics, market sentiment',
    image: ELOUMNINora,
    linkedin: 'https://www.linkedin.com/in/nora-el-oumni/',
    github: 'https://github.com/Noraoum'
  },
  {
    id: 4,
    name: 'KHARFASSE Hiba',
    role: 'NLP Engineer',
    responsibilities: 'Sentiment analysis, NLP pipelines, text classification',
    image: KHARFASSEHiba,
    linkedin: 'https://www.linkedin.com/in/kharfasse-hiba-344250316/',
    github: 'https://github.com/HibvKh'
  },
  {
    id: 5,
    name: 'OUANAD Hafsa',
    role: 'NLP Engineer',
    responsibilities: 'Sentiment analysis, NLP pipelines, model evaluation',
    image: OUANADHafsa,
    linkedin: 'https://www.linkedin.com/in/hafsa-ouanad-383860301/',
    github: 'https://github.com/Hafsawnd'
  },
  {
    id: 6,
    name: 'HIDA Mohammed',
    role: 'Data Analyst',
    responsibilities: 'Correlation analysis, statistics, anomaly detection',
    image: null,
    linkedin: null,
    github: null
  },
  {
    id: 7,
    name: 'KHAILA Imane',
    role: 'DevOps Engineer',
    responsibilities: 'Dashboards, data visualization, reporting',
    image: KHAILAImane,
    linkedin: 'https://www.linkedin.com/in/imane-khaila-a680b42a1/',
    github: 'https://github.com/imanekh02'
  },
  {
    id: 8,
    name: 'BROUKI Aya',
    role: 'DevOps Engineer',
    responsibilities: 'Dashboards, data visualization, reporting',
    image: BROUKIAya,
    linkedin: 'https://www.linkedin.com/in/aya-brouki-783709294/',
    github: 'https://github.com/Aya943-br'
  }
];

export const TECH_STACK = [
  {
    category: 'Backend',
    tech: ['Python', 'FastAPI', 'Airflow'],
    icon: 'Server'
  },
  {
    category: 'Frontend',
    tech: ['React', 'JavaScript', 'Recharts'],
    icon: 'Layout'
  },
  {
    category: 'Data Processing',
    tech: ['Pandas', 'NumPy', 'Scikit-learn'],
    icon: 'Database'
  },
  {
    category: 'NLP & ML',
    tech: ['Transformers', 'FinBERT', 'PyTorch'],
    icon: 'Brain'
  },
  {
    category: 'RAG Chatbot',
    tech: ['Pinecone', 'Groq LLM', 'LangChain'],
    icon: 'MessageSquare'
  },
  {
    category: 'Evaluation',
    tech: ['RAGAS', 'Sentence-Transformers'],
    icon: 'CheckCircle'
  }
];

export const PIPELINE_STEPS = [
  {
    step: 1,
    title: 'Collecte',
    description: 'Scraping Twitter & Reddit',
    icon: 'Download'
  },
  {
    step: 2,
    title: 'Traitement',
    description: 'Nettoyage & preprocessing',
    icon: 'Settings'
  },
  {
    step: 3,
    title: 'Analyse NLP',
    description: 'FinBERT sentiment analysis',
    icon: 'Brain'
  },
  {
    step: 4,
    title: 'Correlation',
    description: 'Prix vs Sentiment',
    icon: 'TrendingUp'
  },
  {
    step: 5,
    title: 'Visualisation',
    description: 'Dashboard interactif',
    icon: 'BarChart3'
  }
];

export const STATS = [
  { value: '26K+', label: 'Documents indexes' },
  { value: '3', label: 'Cryptomonnaies' },
  { value: '95%', label: 'Precision NLP' },
  { value: '24/7', label: 'Monitoring' }
];
