# CareerPath AI

Streamlit-based IT career recommendation web app developed for the UWE Bristol module `UFCEKP-30-3`.

The app collects a user's technical skills, interest areas, and career preferences, then uses an `XGBoost` classification model to predict suitable IT roles and generate a personalised learning roadmap.

## 🔗 Live Demo

**Streamlit Web App:** https://it-career-planner-6yurdhpjbfvgdjjnadytr9.streamlit.app

**Google Colab Notebook:** https://drive.google.com/file/d/1Y4FmKS0PQvGOy5CBG4A0bN3mr2qWq4r1/view?usp=sharing

## Student Information

- Student: Hein Htet Phyo
- Student ID: 25036746
- Module: UFCEKP-30-3
- University: UWE Bristol
- Year: 2026

## Project Overview

This project combines:

- a `Streamlit` web application (deployed online)
- a `Google Colab` notebook for ML development, EDA, and model evaluation
- an `XGBoost` classification model for IT role prediction
- five self-constructed CSV datasets for user profiles, role requirements, metadata, roadmaps, and learning resources

The app provides:

- top 3 recommended IT roles based on learner profile
- readiness scores across all 6 IT roles
- a detailed deep-dive analysis for a selected role
- skill gap analysis with priority classification
- a personalised roadmap with suggested learning resources

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Matplotlib

## Project Structure

```text
it-career-planner/
├── app.py
├── README.md
├── requirements.txt
├── 25036746_DSAI_Individual_Project.ipynb
└── data/
    ├── user_profiles.csv
    ├── role_skill_matrix.csv
    ├── role_metadata.csv
    ├── roadmap_templates.csv
    └── resource_catalogue.csv
```

## Datasets

Five self-constructed CSV files stored in the `data/` folder:

1. `user_profiles.csv` — 6000 rows. Training examples of user skills, interests, preferences, and target roles.
2. `role_skill_matrix.csv` — Required skill levels for each of the 6 IT roles.
3. `role_metadata.csv` — Role descriptions, common tasks, work type, and career goal alignment.
4. `roadmap_templates.csv` — Template learning steps for each role ordered by skill gap priority.
5. `resource_catalogue.csv` — 300 learning resources mapped to skills, levels, and role relevance.

## How the App Works

1. The user enters skill levels, interests, and preferences in the Streamlit interface.
2. `app.py` loads the five datasets from the `data/` folder.
3. The app trains an `XGBoost` model on the user profiles dataset.
4. The trained model predicts the top 3 ranked IT career matches.
5. The app calculates readiness scores and skill gaps for the selected role.
6. A personalised roadmap and matched learning resources are displayed.

## How to Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Opens at: `http://localhost:8501`

## Google Colab Notebook

The `25036746_DSAI_Individual_Project.ipynb` notebook contains:

- Full EDA and data analysis
- Data preprocessing and feature engineering
- Model training and comparison (Decision Tree, Random Forest, XGBoost)
- Model evaluation (accuracy, precision, recall, macro F1, confusion matrix)
- Readiness score and skill-gap analysis logic
- Roadmap generation and resource recommendation pipeline
- Interactive Colab widget UI demo

Datasets are auto-detected:
- In Google Colab: loaded from `Google Drive/IT_Career_Planner_Project/`
- Locally/GitHub: loaded from `data/` folder

## Future Improvements

- Replace synthetic dataset with real learner profile data from surveys
- Integrate real-time job market APIs (LinkedIn, Indeed) for dynamic role demand
- Implement SHAP-based explainability for feature-level ML prediction justification
- Extend role taxonomy to include sub-specialisations
- Add progress tracking so learners can monitor roadmap completion over time
