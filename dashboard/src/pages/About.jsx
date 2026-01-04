import React from 'react';
import { TEAM_MEMBERS, TECH_STACK, FEATURES, PROJECT_INFO } from '../constants/aboutConstants';
import '../styles/about.css';

const About = () => {
  return (
    <div className="about-container">
      {/* Header Section */}
      <section className="about-header">
        <h1>{PROJECT_INFO.title}</h1>
        <p className="tagline">{PROJECT_INFO.tagline}</p>
      </section>

      {/* Project Description */}
      <section className="project-description">
        <div className="description-content">
          <h2>Presentation du Projet</h2>
          <p>
            Crypto_Analysis est une plateforme complete d'analyse de sentiment et de correlation avec les prix des cryptomonnaies.
            Notre projet combine l'extraction de donnees en temps reel, le traitement du langage naturel avance et l'analyse statistique
            pour fournir des insights profonds sur les mouvements du marche des cryptomonnaies.
          </p>
          <p>
            En utilisant des modeles NLP sophistiques comme FinBERT, nous analysons les sentiments exprimes sur Twitter et Reddit
            pour determiner leur impact sur les prix de Bitcoin, Ethereum et Solana.
          </p>
          <p>
            Le projet inclut un chatbot RAG (Retrieval-Augmented Generation) intelligent qui permet aux utilisateurs de poser
            des questions en langage naturel sur le sentiment des cryptos. Le systeme utilise Pinecone pour la recherche vectorielle
            et Groq LLM (Llama 3.3 70B) pour generer des reponses contextuelles.
          </p>
          <div className="features-grid">
            {FEATURES.map((feature, index) => (
              <div key={index} className="feature-box">
                <h3>{feature.icon} {feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="tech-stack">
        <h2>Stack Technique</h2>
        <div className="stack-grid">
          {TECH_STACK.map((stack, index) => (
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
        <h2>Notre Equipe</h2>
        <p className="team-intro">{PROJECT_INFO.teamIntro}</p>
        <div className="team-grid">
          {TEAM_MEMBERS.map((member) => (
            <div key={member.id} className="team-card" style={{ '--card-color': member.color }}>
              <div className="member-avatar" style={{ backgroundColor: member.image ? 'transparent' : member.color }}>
                {member.image ? (
                  <img src={member.image} alt={member.name} className="avatar-image" />
                ) : (
                  <span className="avatar-initials">
                    {member.name.split(' ')[0][0]}{member.name.split(' ')[1]?.[0] || member.id}
                  </span>
                )}
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
