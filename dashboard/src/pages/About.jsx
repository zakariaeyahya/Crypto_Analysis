import React from 'react';
import {
  Server,
  Layout,
  Database,
  Brain,
  MessageSquare,
  CheckCircle,
  Download,
  Settings,
  TrendingUp,
  BarChart3,
  Linkedin,
  Github,
  Users,
  Zap,
  Target,
  ArrowRight
} from 'lucide-react';
import { TEAM_MEMBERS, TECH_STACK, PIPELINE_STEPS, STATS } from '../constants/aboutConstants';
import '../styles/about.css';

const iconMap = {
  Server, Layout, Database, Brain, MessageSquare, CheckCircle,
  Download, Settings, TrendingUp, BarChart3
};

const About = () => {
  const getIcon = (iconName, size = 24) => {
    const IconComponent = iconMap[iconName];
    return IconComponent ? <IconComponent size={size} /> : null;
  };

  return (
    <div className="about-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">Projet TALN 2025</div>
          <h1 className="hero-title">
            Crypto Sentiment
            <span className="gradient-text"> Analysis</span>
          </h1>
          <p className="hero-description">
            Plateforme d'analyse de sentiment des cryptomonnaies combinant
            NLP avance, recherche vectorielle et LLM pour des insights en temps reel.
          </p>
          <div className="hero-stats">
            {STATS.map((stat, index) => (
              <div key={index} className="stat-item">
                <span className="stat-value">{stat.value}</span>
                <span className="stat-label">{stat.label}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="hero-visual">
          <div className="floating-card card-1">
            <TrendingUp size={20} />
            <span>BTC +2.4%</span>
          </div>
          <div className="floating-card card-2">
            <Brain size={20} />
            <span>Sentiment: Positif</span>
          </div>
          <div className="floating-card card-3">
            <MessageSquare size={20} />
            <span>RAG Active</span>
          </div>
        </div>
      </section>

      {/* Pipeline Section */}
      <section className="pipeline-section">
        <div className="section-header">
          <Zap className="section-icon" size={28} />
          <h2>Notre Pipeline</h2>
          <p>Du scraping a la visualisation en 5 etapes</p>
        </div>
        <div className="pipeline-container">
          {PIPELINE_STEPS.map((step, index) => (
            <React.Fragment key={step.step}>
              <div className="pipeline-step">
                <div className="step-number">{step.step}</div>
                <div className="step-icon">
                  {getIcon(step.icon, 28)}
                </div>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </div>
              {index < PIPELINE_STEPS.length - 1 && (
                <div className="pipeline-arrow">
                  <ArrowRight size={24} />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="tech-section">
        <div className="section-header">
          <Target className="section-icon" size={28} />
          <h2>Stack Technique</h2>
          <p>Technologies modernes pour des performances optimales</p>
        </div>
        <div className="tech-grid">
          {TECH_STACK.map((stack, index) => (
            <div key={index} className="tech-card">
              <div className="tech-icon">
                {getIcon(stack.icon, 32)}
              </div>
              <h3>{stack.category}</h3>
              <div className="tech-tags">
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
        <div className="section-header">
          <Users className="section-icon" size={28} />
          <h2>Notre Equipe</h2>
          <p>8 experts passionnes par les donnees et l'IA</p>
        </div>
        <div className="team-grid">
          {TEAM_MEMBERS.map((member) => (
            <div key={member.id} className="team-card">
              <div className="member-image-container">
                {member.image ? (
                  <img src={member.image} alt={member.name} className="member-image" />
                ) : (
                  <div className="member-placeholder">
                    {member.name.split(' ').map(n => n[0]).join('')}
                  </div>
                )}
                <div className="member-overlay">
                  {member.linkedin && (
                    <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="social-link" aria-label="LinkedIn">
                      <Linkedin size={20} />
                    </a>
                  )}
                  {member.github && (
                    <a href={member.github} target="_blank" rel="noopener noreferrer" className="social-link" aria-label="GitHub">
                      <Github size={20} />
                    </a>
                  )}
                </div>
              </div>
              <div className="member-info">
                <h3>{member.name}</h3>
                <span className="member-role">{member.role}</span>
                <p className="member-resp">{member.responsibilities}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer CTA */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Explorez le Dashboard</h2>
          <p>Decouvrez nos analyses de sentiment en temps reel</p>
          <div className="cta-buttons">
            <a href="/" className="cta-btn primary">
              <BarChart3 size={20} />
              Voir le Dashboard
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
