---
name: Crystalline Glass
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1b1b1b'
  surface-container: '#1f1f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353535'
  on-surface: '#e2e2e2'
  on-surface-variant: '#c1c6d7'
  inverse-surface: '#e2e2e2'
  inverse-on-surface: '#303030'
  outline: '#8b90a0'
  outline-variant: '#414755'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e69'
  primary-container: '#4b8eff'
  on-primary-container: '#00285c'
  inverse-primary: '#005bc1'
  secondary: '#53e16f'
  on-secondary: '#003911'
  secondary-container: '#05b046'
  on-secondary-container: '#003a11'
  tertiary: '#ffb595'
  on-tertiary: '#571e00'
  tertiary-container: '#ef6719'
  on-tertiary-container: '#4c1a00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a41'
  on-primary-fixed-variant: '#004493'
  secondary-fixed: '#72fe88'
  secondary-fixed-dim: '#53e16f'
  on-secondary-fixed: '#002107'
  on-secondary-fixed-variant: '#00531c'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb595'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#7c2e00'
  background: '#131313'
  on-background: '#e2e2e2'
  surface-variant: '#353535'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
  nav-width: 80px
---

## Brand & Style

This design system centers on a sophisticated, high-fidelity interpretation of modern spatial computing interfaces. The core aesthetic is **Deep Glassmorphism**, characterized by ultra-high backdrop blurs that create a sense of physical depth and optical immersion. 

The personality is precise, premium, and quiet. It avoids unnecessary decoration, relying instead on the material properties of "glass" and "light" to define hierarchy. Surfaces appear as heavy, translucent slabs that catch light at the edges, evoking the feel of high-end hardware. The user experience should feel lightweight yet grounded, with a focus on high-contrast content and frictionless navigation.

## Colors

The palette is strictly dark-mode first. The foundation is a pure Black (`#000000`) or near-black background to maximize the luminosity of the glass effects. 

- **Glass Surfaces**: Created using a semi-transparent white tint (8-12% opacity) combined with a heavy backdrop blur (40px-64px).
- **Accents**: Use a single, vibrant Apple-style Blue (`#007AFF`) or Green (`#34C759`) exclusively for active states, notifications, or primary actions. 
- **Typography**: Primary text is pure white (`#FFFFFF`) for maximum contrast, while secondary text uses a reduced opacity (60%) rather than a gray hex code, ensuring it blends naturally with underlying glass textures.

## Typography

This design system utilizes **Inter** to replicate the clean, wide, and airy feel of San Francisco. The type scale is optimized for high legibility against complex, blurred backgrounds.

- **Weight & Contrast**: Headlines should use Semi-Bold or Bold weights with tight letter-spacing to feel "architectural." 
- **Airiness**: Body text requires generous line-height to maintain an open, breathable feel. 
- **Active States**: When an item is active, a weight increase or the application of the primary accent color is preferred over underlines or boxes.

## Layout & Spacing

The layout is defined by a **Fluid Grid** that prioritizes safe zones for floating elements. 

- **Floating Navigation**: The signature element is a vertical capsule docked to the left or right of the viewport. It should be separated from the edge by at least 24px and appear to float above the content.
- **Rhythm**: Use a 4px baseline grid. Padding within glass containers should be generous (typically 24px or 32px) to prevent content from feeling crowded against the precision borders.
- **Responsive Behavior**: On mobile, the vertical floating capsule transitions into a horizontal floating tab bar at the bottom of the screen, maintaining the same pill-shaped geometry.

## Elevation & Depth

Depth is conveyed through **refraction and layering** rather than traditional drop shadows.

- **The Glass Stack**: Each elevated layer increases its backdrop blur intensity. A base card might have 32px blur, while a modal or floating nav bar sitting above it has 64px blur.
- **Texture**: Apply a very subtle monochromatic noise/grain SVG filter (approx 2-3% opacity) to glass surfaces to break up digital banding and mimic physical material.
- **Precision Edges**: Every glass element must have a 1px solid border at 20% white. This acts as a "specular highlight," defining the shape of the glass shard against dark backgrounds.

## Shapes

The shape language is strictly **geometric and organic**. 

- **Capsules**: All primary navigation containers and buttons use "full" rounding (pill-shaped) to create a soft, friendly silhouette that contrasts with the technical precision of the glass.
- **Content Cards**: Use a `rounded-xl` (1.5rem / 24px) setting for larger containers. 
- **Consistency**: Internal elements (like photo attachments) should have slightly less rounding than their parent container to maintain a nested visual harmony.

## Components

### Navigation Capsule
A vertical floating bar with a 64px backdrop blur and a 1px white/20 border. Icons inside should be high-contrast glyphs. The active state is indicated by the primary accent color or a subtle "inner glow" behind the icon.

### Buttons
Primary buttons are glass shards with higher opacity (15-20%) or solid accent colors with white text. Secondary buttons are ghost-style, relying solely on the 1px precision border until hovered.

### Input Fields
Inputs should be treated as "wells" etched into the glass. Use a slightly darker background (black at 20% opacity) with a subtle inner shadow to imply the field is recessed into the surface.

### Chips & Tags
Small pill-shaped containers with 8px blur and 12px horizontal padding. Use these for categories or status indicators, using the accent color only when critical information is present.

### Glass Cards
The primary content container. Must include the noise texture, 1px border, and a 40px backdrop blur. Titles within cards should be `headline-lg` to maintain strong hierarchy.