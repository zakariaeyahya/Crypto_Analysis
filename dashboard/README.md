# Crypto Dashboard

Dashboard React pour l'analyse de sentiment et le suivi des cryptomonnaies (Bitcoin, Ethereum, Solana).

## Tech Stack

- **React 18** - Framework UI
- **React Router v6** - Navigation SPA
- **Recharts** - Visualisation de graphiques (LineChart, ComposedChart, ScatterChart)
- **CSS-in-JS** - Styles inline avec effets glassmorphism

## Installation

```bash
npm install
cp .env.example .env
npm start
```

## Structure du Projet

```
dashboard/
├── src/
│   ├── App.jsx                 # Point d'entrée, routing
│   ├── index.js                # Bootstrap React
│   ├── components/             # Composants réutilisables
│   │   ├── Header.jsx
│   │   ├── MetricCard.jsx
│   │   ├── SentimentGauge.jsx
│   │   └── CryptoChart.jsx
│   ├── pages/                  # Pages de l'application
│   │   ├── Overview.jsx
│   │   ├── Timeline.jsx
│   │   ├── Analysis.jsx
│   │   └── Events.jsx
│   ├── data/
│   │   └── mockData.js         # Données simulées
│   └── styles/
│       └── commonStyles.js     # Styles partagés
└── README.md
```

---

## Composants

### `Header.jsx`
Barre de navigation sticky avec effet glassmorphism.

| Prop | Type | Description |
|------|------|-------------|
| `activePath` | `string` | Chemin actif pour le highlight (`/`, `/timeline`, `/analysis`, `/events`) |
| `onNavigate` | `function` | Callback lors du changement de page |

**Fonctionnalités :**
- Navigation entre les 4 pages (Overview, Timeline, Analysis, Events)
- Effet de glow sur le lien actif
- Design responsive avec backdrop blur

---

### `MetricCard.jsx`
Carte affichant une métrique crypto avec variation en pourcentage.

| Prop | Type | Description |
|------|------|-------------|
| `title` | `string` | Nom de la crypto (ex: "Bitcoin (BTC)") |
| `value` | `string` | Valeur formatée (ex: "$43,250.00") |
| `change` | `number` | Variation en % (positif/négatif/neutre) |

**Fonctionnalités :**
- Couleur dynamique selon la variation (vert/rouge/gris)
- Effet hover avec lift, glow et gradient overlay
- Icône flèche haut/bas selon la tendance

---

### `SentimentGauge.jsx`
Jauge semi-circulaire affichant le sentiment du marché (-100 à +100).

| Prop | Type | Description |
|------|------|-------------|
| `value` | `number` | Score de sentiment (-100 à +100) |
| `label` | `string` | Label affiché (défaut: "Market Sentiment") |

**Fonctionnalités :**
- Jauge SVG animée avec aiguille
- Gradient de couleurs (rouge -> gris -> vert)
- Barre de progression avec indicateur
- Labels: Bearish / Neutral / Bullish

---

### `CryptoChart.jsx`
Graphique linéaire pour l'évolution des prix.

| Prop | Type | Description |
|------|------|-------------|
| `data` | `array` | Données [{date, value}, ...] |
| `title` | `string` | Titre du graphique |
| `dataKey` | `string` | Clé des données Y (défaut: "value") |
| `color` | `string` | Couleur de la ligne |

**Fonctionnalités :**
- Basé sur Recharts `LineChart`
- Tooltip personnalisé avec style glassmorphism
- Axes formatés avec séparateurs de milliers

---

## Pages

### `Overview.jsx` - `/`
Dashboard principal avec vue d'ensemble du marché.

**Contenu :**
- **Grille de MetricCards** : Prix et variations des 4 cryptos principales (BTC, ETH, SOL, BNB)
- **CryptoChart** : Evolution Bitcoin sur 7 jours
- **SentimentGauge** : Sentiment global du marché

---

### `Timeline.jsx` - `/timeline`
Evolution temporelle du sentiment par crypto.

**Fonctionnalités :**
- **Sélecteur crypto** : BTC / ETH / SOL
- **Stats en temps réel** : Sentiment actuel + moyenne 30 jours
- **Graphique Recharts** avec :
  - Ligne de sentiment quotidien
  - Moyenne mobile 7 jours (MA7)
  - Ligne de référence à 0
  - Domaine Y fixé [-100, +100]

---

### `Analysis.jsx` - `/analysis`
Analyse de corrélation sentiment/prix.

**Fonctionnalités :**
- **Sélecteur crypto** : BTC / ETH / SOL
- **Statistiques calculées** :
  - Sentiment moyen (30 jours)
  - Volatilité du sentiment (écart-type)
  - Volatilité du prix (%)
  - Coefficient de corrélation Pearson
- **ComposedChart** : Overlay sentiment (Area) + prix (Line) avec double axe Y
- **ScatterChart** : Dispersion sentiment vs variation de prix
- **Interprétation** : Analyse textuelle basée sur le coefficient de corrélation

---

### `Events.jsx` - `/events`
Timeline des événements crypto avec filtrage.

**Fonctionnalités :**
- **Filtres** : All / BTC / ETH / SOL
- **Modes de vue** : Expand (accordion) / Modal
- **Stats** : Total, Positifs, Négatifs, Neutres
- **Timeline visuelle** : Ligne avec points colorés selon le type
- **EventCard** : Date, type (badge couleur), crypto, titre, description expandable
- **EventModal** : Vue détaillée en modal overlay

---

## Mock Data (`mockData.js`)

### Constantes

```javascript
COLORS = {
  positive: '#10B981',  // Vert
  negative: '#EF4444',  // Rouge
  neutral: '#6B7280',   // Gris
  ...
}

cryptoOptions = [
  { value: 'BTC', label: 'Bitcoin (BTC)' },
  { value: 'ETH', label: 'Ethereum (ETH)' },
  { value: 'SOL', label: 'Solana (SOL)' }
]
```

### Données Overview

| Export | Type | Description |
|--------|------|-------------|
| `overviewCryptoData` | `array` | 4 cryptos avec titre, valeur, variation |
| `overviewChartData` | `array` | 7 jours de données BTC (date, value) |
| `overviewSentiment` | `number` | Score sentiment global (35) |

### Générateurs Timeline

```javascript
generateTimelineData(crypto)  // Retourne 30 jours de sentiment + MA7
```

**Paramètres de génération :**
- `baseValues`: BTC=25, ETH=10, SOL=-5
- `volatility`: BTC=30, ETH=40, SOL=50

### Générateurs Analysis

```javascript
generateAnalysisData(crypto)     // 30 jours: date, sentiment, price, priceChange
calculateAnalysisStats(data)     // Stats: avgSentiment, volatilité, corrélation
getCorrelationLabel(corr)        // "Forte" | "Moyenne" | "Faible" | "Negligeable"
```

**Configuration prix de base :**
- BTC: $43,000
- ETH: $2,300
- SOL: $95

### Données Events

```javascript
eventsData = [
  {
    id: 1,
    date: '2024-12-30',
    crypto: 'BTC',
    title: 'Bitcoin ETF Record Inflows',
    description: '...',
    type: 'positive'  // positive | negative | neutral
  },
  // ... 15 événements au total
]

typeLabels = { positive: 'Positive', negative: 'Negative', neutral: 'Neutral' }
```

### Fonctions Utilitaires

| Fonction | Description |
|----------|-------------|
| `formatDate(dateString)` | Formate en "Wed, Dec 30" |
| `getCorrelationLabel(corr)` | Label textuel de corrélation |

---

## Styles (`commonStyles.js`)

### Palette de Couleurs

```javascript
colors = {
  bgPrimary: '#0a0f1a',      // Fond principal
  bgCard: 'rgba(17,24,39,0.6)', // Cartes glassmorphism
  green: '#10B981',          // Positif
  red: '#EF4444',            // Négatif
  textPrimary: '#F9FAFB',    // Texte principal
  textSecondary: '#9CA3AF',  // Texte secondaire
  border: 'rgba(255,255,255,0.08)'
}
```

### Styles Partagés

| Style | Usage |
|-------|-------|
| `sharedStyles.pageContainer` | Container de page avec padding |
| `sharedStyles.pageTitle` | Titre avec gradient text |
| `sharedStyles.card` | Carte glassmorphism avec blur |
| `sharedStyles.gridAutoFit(min)` | Grille responsive auto-fit |
| `sharedStyles.flexBetween` | Flexbox space-between |

### Effets Visuels
- **Glassmorphism** : `backdrop-filter: blur(20px)` + fond semi-transparent
- **Glow Effects** : `box-shadow` avec couleurs alpha
- **Hover Animations** : `transform: translateY(-2px)` + transitions

---

## Routes

| Route | Page | Description |
|-------|------|-------------|
| `/` | Overview | Dashboard principal |
| `/timeline` | Timeline | Evolution sentiment |
| `/analysis` | Analysis | Corrélation sentiment/prix |
| `/events` | Events | Actualités crypto |
