# Design System: EMBER Knowledge Constellation Map

This document outlines the visual identity, color palette, and typography for the project, as defined in the Stitch design system.

## Visual Identity: "Cyber-Academic"
The "Cyber-Academic" aesthetic is a hybrid of high-technology precision and rigorous scholarly organization. It leverages minimalism for information density and "Cyberpunk-lite" depth for an immersive experience.

---

## Color Palette

### Core Brand Colors
| Name | Hex Code | Usage |
| :--- | :--- | :--- |
| **Primary** | `#FFC081` | Main brand color, active highlights. |
| **Primary Container** | `#FF9800` | High-priority backgrounds (Flame Orange). |
| **Secondary** | `#78DC77` | Success states, mastered nodes. |
| **Secondary Container** | `#00761F` | Subtle success backgrounds. |
| **Tertiary** | `#E1CF17` | Warning states, learning progress. |
| **Tertiary Container** | `#C4B300` | Subtle learning backgrounds. |
| **Error** | `#FFB4AB` | Error states, friction points, gaps. |

### Surface & Neutrals
| Name | Hex Code | Usage |
| :--- | :--- | :--- |
| **Background** | `#10141A` | Main application background (Deep Obsidian). |
| **Surface** | `#10141A` | Base surface for panels. |
| **Surface Bright** | `#353940` | Elevated surfaces and active containers. |
| **Surface Container** | `#1C2026` | Card and panel backgrounds. |
| **On Background** | `#DFE2EB` | Primary text on dark backgrounds. |
| **Outline** | `#A38D7A` | Borders and dividers. |

---

## Typography

The system uses a dual-typeface strategy to balance technical grit with academic readability.

### Typefaces
- **Headlines & Labels**: `Space Grotesk` (Geometric, futuristic)
- **Body & Data**: `Inter` (Clean, academic)

### Style Guide
| Style | Font Family | Size | Weight | Line Height |
| :--- | :--- | :--- | :--- | :--- |
| **Headline Large** | Space Grotesk | 32px | 700 | 40px |
| **Headline Medium** | Space Grotesk | 24px | 600 | 32px |
| **Body Medium** | Inter | 16px | 400 | 24px |
| **Label Node** | Space Grotesk | 12px | 500 | 16px |
| **Label Small** | Inter | 11px | 400 | 16px |

---

## Design Principles

### 1. Controlled Discovery
The user should feel like an operator interfacing with a sophisticated data mainframe. Minimal ornamentation, thin strokes (1px), and purposeful luminescence are used to guide focus.

### 2. State-Driven Colors
- **Mastered**: Solid green (`#78DC77`).
- **Learning**: Bright yellow (`#E1CF17`) with a subtle outer glow.
- **Gap**: Sharp red (`#FFB4AB`) for friction points.
- **Locked**: Desaturated dark gray for receding elements.

### 3. Geometric Shapes
- **Nodes**: Perfect circles (48px diameter for primary nodes).
- **UI Elements**: Sharp edges (0px border radius) for buttons, cards, and fields to maintain brutalist precision.
- **Exception**: The Floating Action Button (FAB) remains circular/rounded for interactive distinction.

### 4. Elevation
Depth is achieved through **Tonal Layers** (hex code steps) and **Luminescence** rather than traditional drop shadows. Higher elevation is indicated by lighter surfaces (e.g., `#1C2026` vs `#10141A`).
