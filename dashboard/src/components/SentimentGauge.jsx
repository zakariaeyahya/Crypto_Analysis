/**
 * ============================================
 * SENTIMENT GAUGE COMPONENT - Pseudo Code
 * ============================================
 *
 * DESCRIPTION:
 * Jauge demi-cercle affichant le sentiment marché (-100 à +100)
 * Avec aiguille animée et barre de progression
 *
 * IMPORTS REQUIS:
 * - COLORS from '../data/mockData'
 * - sentimentGaugeStyles from '../styles/commonStyles'
 *
 * ============================================
 * PROPS
 * ============================================
 *
 * @param {number} value - Score sentiment (-100 à +100)
 * @param {string} label - Label optionnel (default: "Market Sentiment")
 *
 * ============================================
 * LOGIQUE / CALCULS
 * ============================================
 *
 * 1. CLAMP VALUE:
 *    clampedValue = Math.max(-100, Math.min(100, value))
 *
 * 2. GET SENTIMENT STATE:
 *    IF value <= -20  → { text: 'Bearish', color: ROUGE }
 *    IF value >= +20  → { text: 'Bullish', color: VERT }
 *    ELSE             → { text: 'Neutral', color: GRIS }
 *
 * 3. CALCULATE ROTATION (pour aiguille SVG):
 *    rotation = (clampedValue / 100) * 90
 *    // -100 → -90°, 0 → 0°, +100 → +90°
 *
 * 4. CALCULATE PROGRESS %:
 *    progressPercent = ((clampedValue + 100) / 200) * 100
 *    // -100 → 0%, 0 → 50%, +100 → 100%
 *
 * ============================================
 * RENDER STRUCTURE
 * ============================================
 *
 * <div container>                          // styles.container (glass card)
 *   │
 *   ├── <h3 label>                         // styles.label
 *   │     └── "Market Sentiment"
 *   │
 *   ├── <div gaugeWrapper>                 // styles.gaugeWrapper (center)
 *   │     │
 *   │     └── <svg viewBox="0 0 200 120">
 *   │           │
 *   │           ├── <path arc-background>  // Arc gris de fond
 *   │           │     └── stroke: COLORS.border
 *   │           │
 *   │           ├── <defs>
 *   │           │     └── <linearGradient> // Dégradé rouge→gris→vert
 *   │           │
 *   │           ├── <path arc-colored>     // Arc avec gradient
 *   │           │     └── strokeDashoffset animé selon progress
 *   │           │
 *   │           ├── <g needle>             // Groupe aiguille (rotation)
 *   │           │     ├── <line>           // Trait de l'aiguille
 *   │           │     └── <circle>         // Point central
 *   │           │     └── transform: rotate(rotation, 100, 100)
 *   │           │
 *   │           └── <text> x2              // Labels "-100" et "+100"
 *   │
 *   ├── <div valueContainer>               // styles.valueContainer
 *   │     ├── <span value>                 // "+35" (gros chiffre coloré)
 *   │     └── <span sentimentText>         // "BULLISH" (label uppercase)
 *   │
 *   └── <div progressBarContainer>
 *         ├── <div progressBarBg>          // Barre grise de fond
 *         │     ├── <div progressBarFill>  // Barre colorée (width: progress%)
 *         │     └── <div indicator>        // Curseur vertical
 *         │
 *         └── <div progressLabels>         // "Bearish" | "Neutral" | "Bullish"
 *               └── 3x <span>
 *
 * ============================================
 * SVG DETAILS
 * ============================================
 *
 * Arc path: "M 20 100 A 80 80 0 0 1 180 100"
 *   - Demi-cercle de gauche (20,100) à droite (180,100)
 *   - Rayon: 80px
 *
 * Gradient stops:
 *   - 0%   → rouge (#EF4444)
 *   - 40%  → rouge
 *   - 50%  → gris (#6B7280)
 *   - 60%  → vert (#10B981)
 *   - 100% → vert
 *
 * Aiguille:
 *   - Ligne de (100,100) à (100,35)
 *   - Rotation autour du point (100,100)
 *   - Couleur = sentiment.color
 *
 * ============================================
 * ANIMATIONS
 * ============================================
 *
 * - strokeDashoffset: transition 0.5s ease-out
 * - Needle rotation: transition 0.3s ease
 * - Progress bar: transition 0.5s ease-out
 * - Glow effect sur l'indicateur
 */

// TODO: Implémenter le composant SentimentGauge selon le pseudo-code ci-dessus
export default function SentimentGauge({ value = 0, label = 'Market Sentiment' }) {
  // IMPLEMENTATION ICI
  return null;
}
