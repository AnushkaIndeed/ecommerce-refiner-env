---
title: Ecommerce Refiner
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Ecommerce Refiner 
An AI-powered agent built that extracts structured data (Brand, Color, Size) from messy e-commerce titles.

### 🚀 Features
- **FastAPI Backend:** Handles automated agentic loops via `/reset` and `/refine`.
- **Gradio Frontend:** A user-friendly interface for manual testing.
- **Gemini 2.5 Flash:** High-speed attribute extraction.

### 🛠️ Tech Stack
- Python, FastAPI, Docker, Gradio, Google Gemini API.

### 🏁 Validation
- Successfully returns `Reward: 1.0` upon correct brand identification.