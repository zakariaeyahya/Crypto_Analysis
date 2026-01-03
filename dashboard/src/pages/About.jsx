import React from 'react';
import '../styles/about.css';

const About = () => {
  const teamMembers = [
    {
      id: 1,
      name: 'KAYOUH Salaheddine',
      role: 'Project Manager',
      responsibilities: 'Planning, coordination, intégration',
      color: '#FF6B6B'
    },
    {
      id: 2,
      name: 'YAHYA Zakariae',
      role: 'Data Engineer',
      responsibilities: 'Scraping, preprocessing',
      color: '#4ECDC4'
    },
    {
      id: 3,
      name: 'EL OUMNI Nora',
      role: 'Data Engineer',
      responsibilities: 'Database, ETL',
      color: '#45B7D1'
    },
    {
      id: 4,
      name: 'KHARFASSE Hiba',
      role: 'NLP Engineer',
      responsibilities: 'Modèles de sentiment',
      color: '#FFA07A'
    },
    {
      id: 5,
      name: 'OUANAD Hafsa',
      role: 'NLP Engineer',
      responsibilities: 'Fine-tuning, évaluation',
      color: '#98D8C8'
    },
    {
      id: 6,
      name: 'HIDA Mohammed',
      role: 'Data Analyst',
      responsibilities: 'Corrélations, statistiques',
      color: '#F7DC6F'
    },
    {
      id: 7,
      name: 'KHAILA Imane',
      role: 'Data Analyst',
      responsibilities: 'Visualisations, insights',
      color: '#BB8FCE'
    },
    {
      id: 8,
      name: 'BROUKI Aya',
      role: 'DevOps Engineer',
      responsibilities: 'Dashboard, déploiement',
      color: '#85C1E2'
    }
  ];

  const techStack = [
    { category: 'Backend', tech: ['Python', 'FastAPI', 'Airflow'] },
    { category: 'Frontend', tech: ['React', 'JavaScript', 'CSS'] },
    { category: 'Data Processing', tech: ['Pandas', 'NumPy', 'Scikit-learn'] },
    { category: 'NLP & ML', tech: ['Transformers', 'RoBERTa', 'PyTorch'] },
    { category: 'Database', tech: ['PostgreSQL', 'MongoDB'] },
    { category: 'DevOps', tech: ['Docker', 'Docker Compose', 'Airflow'] }
  ];

  return (
    <div className="about-container">
      {/* Header Section */}
      <section className="about-header">
        <h1>À Propos du Projet</h1>
        <p className="tagline">Analyse avancée du sentiment et corrélation avec les prix des cryptomonnaies</p>
      </section>

      {/* Project Description */}
      <section className="project-description">
        <div className="description-content">
          <h2>Présentation du Projet</h2>
          <p>
            Crypto_Analysis est une plateforme complète d'analyse de sentiment et de corrélation avec les prix des cryptomonnaies. 
            Notre projet combine l'extraction de données en temps réel, le traitement du langage naturel avancé et l'analyse statistique 
            pour fournir des insights profonds sur les mouvements du marché des cryptomonnaies.
          </p>
          <p>
            En utilisant des modèles NLP sophistiqués comme RoBERTa, nous analysons les sentiments exprimés sur Reddit et d'autres 
            sources pour déterminer leur impact sur les prix de Bitcoin, Ethereum et Solana.
          </p>
          <div className="features-grid">
            <div className="feature-box">
              <h3>🔍 Extraction de Données</h3>
              <p>Scraping et collecte de données depuis Kaggle et Reddit</p>
            </div>
            <div className="feature-box">
              <h3>🧠 Analyse NLP</h3>
              <p>Modèles de sentiment avancés basés sur Transformers</p>
            </div>
            <div className="feature-box">
              <h3>📊 Analyse Statistique</h3>
              <p>Corrélations et statistiques détaillées</p>
            </div>
            <div className="feature-box">
              <h3>📈 Visualisations</h3>
              <p>Dashboard interactif et visualisations enrichies</p>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="tech-stack">
        <h2>Stack Technique</h2>
        <div className="stack-grid">
          {techStack.map((stack, index) => (
            <div key={index} className="stack-card">
              <h3>{stack.category}</h3>
              <div className="tech-list">
                {stack.tech.map((tech, idx) => (
                  <span key={idx} className="tech-tag">{tech}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Team Section */}
      <section className="team-section">
        <h2>Notre Équipe</h2>
        <p className="team-intro">8 experts passionnés par les données et l'innovation</p>
        <div className="team-grid">
          {teamMembers.map((member) => (
            <div key={member.id} className="team-card" style={{ '--card-color': member.color }}>
              <div className="member-avatar" style={{ backgroundColor: member.color }}>
                <span className="avatar-initials">{member.name.split(' ')[0][0]}{member.name.split(' ')[1]?.[0] || member.id}</span>
              </div>
              <h3 className="member-name">{member.name}</h3>
              <p className="member-role">{member.role}</p>
              <p className="member-responsibilities">{member.responsibilities}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default About;