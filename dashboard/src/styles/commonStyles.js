// ============================================
// PREMIUM STYLES - Crypto Dashboard
// Glassmorphism + Glow Effects + Animations
// ============================================

// Color Palette
const colors = {
  // Backgrounds
  bgPrimary: '#0a0f1a',
  bgSecondary: '#111827',
  bgCard: 'rgba(17, 24, 39, 0.6)',
  bgGlass: 'rgba(255, 255, 255, 0.03)',
  bgHover: 'rgba(255, 255, 255, 0.05)',

  // Accents
  green: '#10B981',
  greenGlow: 'rgba(16, 185, 129, 0.4)',
  greenLight: '#34D399',
  red: '#EF4444',
  redGlow: 'rgba(239, 68, 68, 0.4)',
  redLight: '#F87171',
  blue: '#3B82F6',
  purple: '#8B5CF6',
  neutral: '#6B7280',

  // Text
  textPrimary: '#F9FAFB',
  textSecondary: '#9CA3AF',
  textMuted: '#6B7280',

  // Borders
  border: 'rgba(255, 255, 255, 0.08)',
  borderHover: 'rgba(255, 255, 255, 0.15)',
};

// Export for use in components
export const COLORS = {
  positive: colors.green,
  negative: colors.red,
  neutral: colors.neutral,
  background: colors.bgCard,
  backgroundDark: colors.bgPrimary,
  border: colors.border,
  textPrimary: colors.textPrimary,
  textSecondary: colors.textSecondary,
  textMuted: colors.textMuted,
};

// ============================================
// SHARED STYLES
// ============================================

export const sharedStyles = {
  // Page container with gradient background
  pageContainer: {
    padding: '32px',
    minHeight: '100vh',
    boxSizing: 'border-box',
    animation: 'fadeIn 0.4s ease-out',
  },

  // Page title with gradient text effect
  pageTitle: {
    color: colors.textPrimary,
    fontSize: '32px',
    fontWeight: '800',
    margin: '0 0 32px 0',
    letterSpacing: '-0.02em',
    background: `linear-gradient(135deg, ${colors.textPrimary} 0%, ${colors.textSecondary} 100%)`,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },

  // Glass card effect
  card: {
    background: colors.bgCard,
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '24px',
    border: `1px solid ${colors.border}`,
    transition: 'all 0.3s ease',
    position: 'relative',
    overflow: 'hidden',
  },

  // Card with hover effect
  cardHover: {
    ':hover': {
      transform: 'translateY(-2px)',
      borderColor: colors.borderHover,
      boxShadow: `0 20px 40px rgba(0, 0, 0, 0.3)`,
    },
  },

  // Selector/Dropdown premium
  selector: {
    background: colors.bgCard,
    backdropFilter: 'blur(10px)',
    color: colors.textPrimary,
    border: `1px solid ${colors.border}`,
    borderRadius: '12px',
    padding: '12px 20px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    outline: 'none',
    minWidth: '200px',
    transition: 'all 0.2s ease',
  },

  selectorLabel: {
    color: colors.textSecondary,
    fontSize: '13px',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },

  selectorContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },

  // Premium tooltip
  tooltip: {
    background: colors.bgSecondary,
    backdropFilter: 'blur(20px)',
    border: `1px solid ${colors.border}`,
    borderRadius: '12px',
    padding: '16px',
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)',
  },

  tooltipLabel: {
    color: colors.textPrimary,
    fontWeight: '700',
    margin: '0 0 8px 0',
    fontSize: '14px',
  },

  tooltipValue: {
    margin: '4px 0',
    fontSize: '13px',
    fontWeight: '500',
  },

  // Chart card
  chartCard: {
    background: colors.bgCard,
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '28px',
    border: `1px solid ${colors.border}`,
    transition: 'all 0.3s ease',
  },

  chartTitle: {
    color: colors.textPrimary,
    fontSize: '20px',
    fontWeight: '700',
    margin: '0 0 6px 0',
    letterSpacing: '-0.01em',
  },

  chartSubtitle: {
    color: colors.textMuted,
    fontSize: '14px',
    margin: '0 0 24px 0',
    fontWeight: '500',
  },

  chartWrapper: {
    width: '100%',
    minHeight: '350px',
  },

  // Stat box with glow effect
  statBox: {
    background: colors.bgCard,
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '20px 28px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    border: `1px solid ${colors.border}`,
    transition: 'all 0.3s ease',
    cursor: 'default',
  },

  statLabel: {
    color: colors.textMuted,
    fontSize: '11px',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
    marginBottom: '8px',
  },

  statValue: {
    fontSize: '28px',
    fontWeight: '800',
    letterSpacing: '-0.02em',
  },

  // Grid layouts
  gridAutoFit: (minWidth = '220px') => ({
    display: 'grid',
    gridTemplateColumns: `repeat(auto-fit, minmax(${minWidth}, 1fr))`,
    gap: '24px',
  }),

  // Flex layouts
  flexRow: {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    gap: '24px',
  },

  flexBetween: {
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '24px',
  },
};

// ============================================
// HEADER STYLES
// ============================================

export const headerStyles = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 32px',
    background: 'rgba(10, 15, 26, 0.8)',
    backdropFilter: 'blur(20px)',
    borderBottom: `1px solid ${colors.border}`,
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  title: {
    fontSize: '22px',
    fontWeight: '800',
    background: `linear-gradient(135deg, ${colors.green} 0%, ${colors.blue} 100%)`,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    letterSpacing: '-0.02em',
  },
  nav: {
    display: 'flex',
    gap: '8px',
    background: colors.bgCard,
    padding: '6px',
    borderRadius: '14px',
    border: `1px solid ${colors.border}`,
  },
  link: {
    padding: '10px 20px',
    borderRadius: '10px',
    textDecoration: 'none',
    color: colors.textMuted,
    fontSize: '14px',
    fontWeight: '600',
    transition: 'all 0.2s ease',
  },
  activeLink: {
    background: `linear-gradient(135deg, ${colors.green}20 0%, ${colors.blue}20 100%)`,
    color: colors.green,
    boxShadow: `0 0 20px ${colors.greenGlow}`,
  },
};

// ============================================
// METRIC CARD STYLES
// ============================================

export const metricCardStyles = {
  card: {
    background: colors.bgCard,
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '28px',
    minWidth: '200px',
    border: `1px solid ${colors.border}`,
    transition: 'all 0.3s ease',
    cursor: 'default',
    position: 'relative',
    overflow: 'hidden',
  },
  title: {
    color: colors.textSecondary,
    fontSize: '13px',
    margin: '0 0 12px 0',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  value: {
    color: colors.textPrimary,
    fontSize: '32px',
    fontWeight: '800',
    margin: '0 0 16px 0',
    letterSpacing: '-0.02em',
  },
  changeContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '15px',
    fontWeight: '700',
    padding: '8px 14px',
    borderRadius: '10px',
    width: 'fit-content',
  },
};

// ============================================
// SENTIMENT GAUGE STYLES
// ============================================

export const sentimentGaugeStyles = {
  container: {
    background: colors.bgCard,
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    padding: '28px',
    width: '100%',
    maxWidth: '340px',
    boxSizing: 'border-box',
    border: `1px solid ${colors.border}`,
    transition: 'all 0.3s ease',
  },
  label: {
    color: colors.textPrimary,
    fontSize: '16px',
    fontWeight: '700',
    margin: '0 0 20px 0',
    textAlign: 'center',
    letterSpacing: '-0.01em',
  },
  gaugeWrapper: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '12px',
  },
  svg: {
    width: '220px',
    height: '130px',
  },
  valueContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '6px',
    marginBottom: '24px',
  },
  value: {
    fontSize: '42px',
    fontWeight: '800',
    letterSpacing: '-0.02em',
  },
  sentimentText: {
    fontSize: '14px',
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: '0.15em',
  },
  progressBarContainer: {
    marginTop: '20px',
  },
  progressBarBg: {
    position: 'relative',
    height: '8px',
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '4px',
    overflow: 'visible',
  },
  progressBarFill: {
    position: 'absolute',
    left: '0',
    top: '0',
    height: '100%',
    borderRadius: '4px',
    transition: 'width 0.5s ease-out, background-color 0.3s ease',
    boxShadow: '0 0 10px currentColor',
  },
  progressBarIndicator: {
    position: 'absolute',
    top: '-6px',
    width: '6px',
    height: '20px',
    borderRadius: '3px',
    transform: 'translateX(-50%)',
    transition: 'left 0.5s ease-out, background-color 0.3s ease',
    boxShadow: '0 0 15px currentColor',
  },
  progressLabels: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '12px',
  },
  progressLabel: {
    fontSize: '11px',
    color: colors.textMuted,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
};

// ============================================
// CRYPTO CHART STYLES
// ============================================

export const cryptoChartStyles = {
  container: {
    background: colors.bgCard,
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '28px',
    width: '100%',
    border: `1px solid ${colors.border}`,
  },
  title: {
    color: colors.textPrimary,
    margin: 0,
    marginBottom: '20px',
    fontSize: '20px',
    fontWeight: '700',
    letterSpacing: '-0.01em',
  },
  chartWrapper: {
    width: '100%',
    height: 320,
  },
};

// ============================================
// EVENTS PAGE STYLES
// ============================================

export const eventsStyles = {
  header: {
    marginBottom: '32px',
  },
  filterRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '24px',
    alignItems: 'center',
    marginBottom: '24px',
  },
  filterContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  filterLabel: {
    color: colors.textSecondary,
    fontSize: '13px',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  filterSelect: {
    background: colors.bgCard,
    backdropFilter: 'blur(10px)',
    color: colors.textPrimary,
    border: `1px solid ${colors.border}`,
    borderRadius: '12px',
    padding: '12px 20px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    outline: 'none',
    minWidth: '180px',
    transition: 'all 0.2s ease',
  },
  viewToggle: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    background: colors.bgCard,
    padding: '6px',
    borderRadius: '12px',
    border: `1px solid ${colors.border}`,
  },
  toggleButton: {
    color: colors.textPrimary,
    border: 'none',
    borderRadius: '8px',
    padding: '10px 18px',
    fontSize: '13px',
    fontWeight: '600',
    cursor: 'pointer',
    outline: 'none',
    transition: 'all 0.2s ease',
    background: 'transparent',
  },
  statsRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '16px',
  },
  statBox: {
    background: colors.bgCard,
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '16px 24px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minWidth: '90px',
    border: `1px solid ${colors.border}`,
    transition: 'all 0.3s ease',
  },
  statValue: {
    color: colors.textPrimary,
    fontSize: '28px',
    fontWeight: '800',
    letterSpacing: '-0.02em',
  },
  statLabel: {
    color: colors.textMuted,
    fontSize: '11px',
    marginTop: '6px',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  timeline: {
    position: 'relative',
    paddingLeft: '36px',
  },
  timelineLine: {
    position: 'absolute',
    left: '11px',
    top: '0',
    bottom: '0',
    width: '2px',
    background: `linear-gradient(180deg, ${colors.green}40 0%, ${colors.purple}40 50%, ${colors.red}40 100%)`,
    borderRadius: '1px',
  },
  timelineItem: {
    position: 'relative',
    marginBottom: '20px',
  },
  timelineDot: {
    position: 'absolute',
    left: '-30px',
    top: '24px',
    width: '14px',
    height: '14px',
    borderRadius: '50%',
    border: `3px solid ${colors.bgPrimary}`,
    boxShadow: '0 0 15px currentColor',
    transition: 'all 0.3s ease',
  },
  eventCard: {
    background: colors.bgCard,
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '20px 24px',
    borderLeft: '4px solid',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    border: `1px solid ${colors.border}`,
    borderLeftWidth: '4px',
  },
  eventHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
  },
  eventMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    flexWrap: 'wrap',
  },
  eventDate: {
    color: colors.textSecondary,
    fontSize: '13px',
    fontWeight: '500',
  },
  eventType: {
    fontSize: '10px',
    fontWeight: '700',
    padding: '6px 10px',
    borderRadius: '6px',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  cryptoBadge: {
    background: 'rgba(255, 255, 255, 0.1)',
    color: colors.textPrimary,
    fontSize: '11px',
    fontWeight: '700',
    padding: '6px 10px',
    borderRadius: '6px',
    letterSpacing: '0.02em',
  },
  expandIcon: {
    color: colors.textMuted,
    fontSize: '20px',
    fontWeight: '300',
    transition: 'transform 0.2s ease',
  },
  eventTitle: {
    color: colors.textPrimary,
    fontSize: '17px',
    fontWeight: '700',
    margin: '0',
    letterSpacing: '-0.01em',
  },
  eventDetails: {
    marginTop: '16px',
    paddingTop: '16px',
    borderTop: `1px solid ${colors.border}`,
    animation: 'fadeIn 0.3s ease-out',
  },
  eventDescription: {
    color: colors.textSecondary,
    fontSize: '14px',
    lineHeight: '1.7',
    margin: '0',
  },
  noEvents: {
    color: colors.textMuted,
    fontSize: '16px',
    textAlign: 'center',
    padding: '60px 20px',
    fontWeight: '500',
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.8)',
    backdropFilter: 'blur(8px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '20px',
    animation: 'fadeIn 0.2s ease-out',
  },
  modalContent: {
    background: colors.bgSecondary,
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    padding: '32px',
    maxWidth: '540px',
    width: '100%',
    borderTop: '4px solid',
    maxHeight: '85vh',
    overflow: 'auto',
    border: `1px solid ${colors.border}`,
    boxShadow: '0 25px 50px rgba(0, 0, 0, 0.5)',
    animation: 'fadeIn 0.3s ease-out',
  },
  modalHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '20px',
  },
  modalMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    flexWrap: 'wrap',
  },
  modalDate: {
    color: colors.textSecondary,
    fontSize: '14px',
    fontWeight: '500',
  },
  closeButton: {
    background: 'rgba(255, 255, 255, 0.1)',
    border: 'none',
    color: colors.textSecondary,
    fontSize: '16px',
    cursor: 'pointer',
    padding: '8px 12px',
    borderRadius: '8px',
    fontWeight: '600',
    transition: 'all 0.2s ease',
  },
  modalTitle: {
    color: colors.textPrimary,
    fontSize: '24px',
    fontWeight: '800',
    margin: '0 0 20px 0',
    letterSpacing: '-0.02em',
  },
  modalDescription: {
    color: colors.textSecondary,
    fontSize: '15px',
    lineHeight: '1.8',
    margin: '0 0 24px 0',
  },
  modalFooter: {
    paddingTop: '20px',
    borderTop: `1px solid ${colors.border}`,
  },
  footerText: {
    color: colors.textSecondary,
    fontSize: '13px',
    fontWeight: '500',
  },
};
