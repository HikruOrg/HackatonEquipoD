# Dark Mode Feature Guide

## 🌙 Dark Mode Implementation

The Azure Image Processor now includes a fully functional dark mode feature with persistent theme preferences.

### Features:

1. **Theme Toggle Button**: Located in the top-right corner of the header
   - 🌙 (Moon icon) = Switch to dark mode
   - ☀️ (Sun icon) = Switch to light mode

2. **Persistent Preferences**: Your theme choice is saved in localStorage and restored on page reload

3. **Complete UI Coverage**: All components are styled for dark mode including:
   - Forms and input fields
   - Cards and containers
   - Tables and progress bars
   - Charts and visualizations
   - Buttons and badges
   - Alerts and feedback messages

### Implementation Details:

#### **Theme Context**
- Uses React Context API for global state management
- Automatic localStorage persistence
- Bootstrap 5.3+ dark mode integration

#### **CSS Custom Properties**
- Leverages CSS custom properties for dynamic theming
- Smooth transitions between light and dark modes
- Comprehensive component coverage

#### **Bootstrap Integration**
- Uses Bootstrap's built-in dark mode with `data-bs-theme` attribute
- Enhanced with custom CSS for better dark mode appearance
- Maintains Bootstrap utility classes compatibility

### How to Use:

1. **Toggle Theme**: Click the moon/sun icon in the top-right corner
2. **Persistent Storage**: Your preference is automatically saved
3. **Automatic Restoration**: Theme preference is restored when you return to the app

### Styling Highlights:

- **Background Colors**: Deep gray (#1a1a1a) for main background, lighter gray (#2d3748) for cards
- **Text Colors**: Light gray (#e9ecef) for primary text, muted colors for secondary text
- **Border Colors**: Subtle borders with improved contrast
- **Interactive Elements**: Hover states and focus indicators optimized for dark mode
- **Charts**: Recharts components adapted for dark theme visibility

### Browser Support:

- All modern browsers supporting CSS custom properties
- Graceful degradation for older browsers
- Responsive design maintained in both themes

The dark mode feature provides a comfortable viewing experience in low-light environments while maintaining full functionality and visual appeal.