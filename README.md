# MaaSakhi - Smart Maternal Health App 🌸

**Developed By Balaram B**

MaaSakhi is a comprehensive, AI-powered maternal health assistant designed to support expecting mothers through their journey. It combines emotional support, health tracking, and smart diagnostics in a beautiful, soothing interface.

## Key Features

*   **AI Chatbot Assistant ("MaaSakhi")**:
    *   Powered by Gemini AI.
    *   Provides empathetic, medical-aware advice.
    *   Features a cute **Flying Robot Mascot** that greets you.
*   **Smart Dashboard**:
    *   **"Miracle Within" Hero Card**: Tracks baby's growth abstractly and beautifully.
    *   **Thought of the Day**: Daily motivation for mothers.
    *   **Glassmorphism UI**: Premium, pink-themed adoption of modern design trends.
*   **Health Diagnostics**:
    *   Upload medical reports for instant AI analysis.
    *   Direct "Emergency" quick access.
*   **Cinematic Experience**:
    *   **Massive Zoom Transitions**: Seamless entry animations that fly you into the app.
    *   **Pulsing Logo Loader**: A custom branded loading experience.

## AI Models & Architecture

MaaSakhi leverages state-of-the-art Generative AI to provide accurate, context-aware health support.

### **Core Model: Gemini 1.5 Pro**
We utilize Google's **Gemini 1.5 Pro** model for its superior reasoning capabilities and multimodal understanding.

*   **Training & Fine-Tuning Strategy**:
    *   **Instruction Tuning**: We employ advanced "System Instruction" architectures to define the persona of "MaaSakhi"—a compassionate, medically-informed Indian health assistant.
    *   **Context Injection (RAG-Lite)**: User health data (trimester, vitals) is dynamically injected into the model's context window, allowing it to give personalized advice without needing traditional model fine-tuning.
    *   **Multimodal Analysis**: The model is "trained" via prompt engineering to recognize specific Indian medical report formats (ultrasounds, blood tests) and extract key values like Heart Rate, Placenta Position, and Fluid Levels.

## Relational Database Schema

MaaSakhi uses a robust relational SQL database to ensure data integrity and security.

### **1. Users Table (`users`)**
Stores authentication and profile tokens.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INT (PK) | Unique User ID |
| `name` | VARCHAR | Full Name of the Mother |
| `email` | VARCHAR | Unique Login Email |
| `password_hash` | VARCHAR | Bcrypt Encrypted Password |

### **2. Health Records Table (`health_records`)**
A comprehensive log of all diagnostics and reports.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INT (PK) | Unique Record ID |
| `user_id` | INT (FK) | Links to `users.id` |
| `category` | VARCHAR | e.g., "First Trimester", "Routine" |
| `test_name` | VARCHAR | e.g., "Growth Scan", "Hemoglobin" |
| `value_numeric` | FLOAT | Extracted numerical value (e.g., 11.2) |
| `value_text` | TEXT | Qualitative result (e.g., "Normal") |
| `file_path` | VARCHAR | Path to uploaded report image |
| `test_date` | DATE | Date of diagnosis |

## How to Run

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Set Up Environment**:
    *   Create a `.env` file with your `GOOGLE_API_KEY`.
3.  **Run the Server**:
    ```bash
    python run.py
    ```
4.  **Access**:
    *   Open `http://127.0.0.1:5000` in your browser.

## Design Philosophy

*   **Soft & Safe**: Uses a baby-pink, lavender, and white palette (`#FF69B4`, `#FFF0F5`) to evoke warmth and care.
*   **Alive Interface**: Everything breathes. The logo pulses, blobs float in the background, and cards hover.
*   **Premium Quality**: Glassmorphism effects and custom vector assets replace standard corporate flat design.

---
*Dedicated to all mothers.* 
