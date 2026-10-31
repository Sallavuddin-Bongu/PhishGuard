# 🛡️ PhishGuard – Phishing URL Detection System

### Intelligent Phishing URL Detection & Risk Analysis System

PhishGuard is a machine learning-based web application designed to detect phishing URLs and help users identify potentially malicious websites. It analyzes submitted URLs, predicts whether they are legitimate or phishing, and provides risk information to improve online safety.

---

## 🚀 Project Overview

Phishing attacks use fake websites and malicious URLs to steal sensitive information such as passwords, banking details, and personal data.

PhishGuard aims to identify suspicious URLs using machine learning and URL analysis techniques.

## ✨ Key Features

- **URL Detection:** Analyze submitted URLs to identify potential phishing websites.
- **Machine Learning:** Uses a trained machine learning model for URL classification.
- **Risk Explanation:** Provides information to help users understand suspicious URL characteristics.
- **User Authentication:** Registration and login functionality.
- **OTP Verification:** Email-based verification and password recovery.
- **Scan History:** View previously scanned URLs.
- **Analytics Dashboard:** View scan statistics and detection results.
- **Threat Intelligence:** Supporting threat information and security insights.
- **Modern Interface:** Cybersecurity-themed web dashboard.

## 🧠 Machine Learning Model

PhishGuard uses a Random Forest classification model to classify URLs.

**Dataset:** PhiUSIIL Phishing URL Dataset

### Dataset Information

| Description | Value |
|---|---:|
| Total records | 235,795 |
| Total features | 56 |
| Legitimate URLs | 100,945 |
| Phishing URLs | 134,850 |

### Model Evaluation

| Metric | Result |
|---|---:|
| Accuracy | 99.73% |
| Macro F1-score | 99.73% |

*Note: These are evaluation results obtained during model development. They do not guarantee the same performance on unseen real-world phishing URLs.*

## 🛠️ Technologies Used

**Frontend**
- React.js
- Vite
- Tailwind CSS
- JavaScript

**Backend**
- Python
- FastAPI
- REST API

**Machine Learning**
- Scikit-learn
- Pandas
- NumPy
- Random Forest
- Joblib

**Database and Development Tools**
- SQLite
- Git
- GitHub
- Visual Studio Code

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/PhishGuard.git
```

### 2. Open the Project

```bash
cd PhishGuard
```

### 3. Backend Setup

Open a terminal:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app --reload --reload-dir app
```

Backend URL:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 4. Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

Open the local URL displayed in your terminal.

*Note: These commands assume your actual project uses the backend and frontend paths shown above. Follow your final project structure if the paths differ.*

## 🔍 How It Works

1. The user enters a URL into the PhishGuard scanner.
2. The application sends the URL to the backend.
3. The backend processes the URL and prepares the required features.
4. The trained machine learning model predicts the URL category.
5. The application displays the prediction and relevant risk information.
6. Scan results can be viewed in the user's scan history and analytics dashboard.

## 🎯 Project Objectives

- Detect potentially malicious phishing URLs.
- Apply machine learning techniques to cybersecurity.
- Help users understand URL-based security risks.
- Provide an accessible web-based phishing detection platform.

## 🔮 Future Enhancements

- Browser extension integration.
- Real-time threat intelligence integration.
- Improved detection using larger and more diverse datasets.
- Continuous model evaluation and improvement.
- Production deployment with a persistent database.

## ⚠️ Disclaimer

PhishGuard is an educational and cybersecurity project. Its predictions are not a guarantee that a website is safe or malicious. Users should avoid entering sensitive information on suspicious websites, even if a URL is classified as legitimate.

## 👨‍💻 Developer

**Bongu Sallavuddin**

B.Tech – Computer Science and Engineering (Data Science)

Rajeev Gandhi Memorial College of Engineering and Technology

---

### PhishGuard

*Detect suspicious URLs. Understand threats. Browse safely.*
