/**
 * ============================================
 * METRIC CARD COMPONENT - Pseudo Code
 * ============================================
 *
 * DESCRIPTION:
 * Carte affichant une métrique crypto (prix + variation %)
 * Avec effet hover (lift + glow coloré)
 *
 * IMPORTS REQUIS:
 * - useState from 'react'
 * - COLORS from '../data/mockData'
 * - metricCardStyles from '../styles/commonStyles'
 *
 * ============================================
 * PROPS
 * ============================================
 *
 * @param {string} title  - Nom de la crypto (ex: "Bitcoin (BTC)")
 * @param {string} value  - Prix formaté (ex: "$43,250.00")
 * @param {number} change - Variation en % (positif, négatif ou 0)
 *
 * ============================================
 * STATE
 * ============================================
 *
 * isHovered: boolean = false   // Track hover state pour animations
 *
 * ============================================
 * LOGIQUE
 * ============================================
 *
 * FUNCTION getChangeColor():
 *   IF change > 0  → return COLORS.positive (#10B981 vert)
 *   IF change < 0  → return COLORS.negative (#EF4444 rouge)
 *   ELSE           → return COLORS.neutral  (#6B7280 gris)
 *
 * FUNCTION getArrowIcon():
 *   IF change > 0  → return SVG flèche vers le HAUT
 *   IF change < 0  → return SVG flèche vers le BAS
 *   ELSE           → return null
 *
 * FUNCTION formatChange():
 *   IF change > 0  → return "+X.XX%"
 *   ELSE           → return "X.XX%" (ou "-X.XX%")
 *
 * ============================================
 * RENDER STRUCTURE
 * ============================================
 *
 * <div card>                               // styles.card + hover effects
 *   │
 *   ├── <div gradient-overlay>             // Overlay gradient au hover
 *   │     └── opacity: 0 → 1 on hover
 *   │     └── background: linear-gradient(changeColor)
 *   │
 *   ├── <p title>                          // styles.title
 *   │     └── "Bitcoin (BTC)"
 *   │
 *   ├── <p value>                          // styles.value (gros chiffre blanc)
 *   │     └── "$43,250.00"
 *   │
 *   └── <div changeContainer>              // styles.changeContainer + couleur
 *         ├── {arrowIcon}                  // SVG flèche haut/bas
 *         └── <span>"+2.45%"</span>
 *
 * ============================================
 * HOVER EFFECTS
 * ============================================
 *
 * ON MOUSE ENTER:
 *   - isHovered = true
 *   - transform: translateY(-4px)         // Lift effect
 *   - boxShadow: 0 20px 40px + glow coloré
 *   - borderColor: plus visible
 *   - gradient overlay opacity: 1
 *
 * ON MOUSE LEAVE:
 *   - isHovered = false
 *   - Retour état normal avec transition
 *
 * ============================================
 * STYLES DYNAMIQUES
 * ============================================
 *
 * changeContainer:
 *   - color: changeColor
 *   - background: changeColor + 15% opacity
 *   - boxShadow: glow si hover
 *
 * gradientOverlay:
 *   - position: absolute, full cover
 *   - background: linear-gradient(135deg, changeColor 8%, transparent)
 *   - opacity: 0 → 1 on hover
 *   - pointerEvents: none
 */

// TODO: Implémenter le composant MetricCard selon le pseudo-code ci-dessus
export default function MetricCard({ title, value, change = 0 }) {
  // IMPLEMENTATION ICI
  return null;
}
