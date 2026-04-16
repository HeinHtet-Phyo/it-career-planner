# CareerPath AI

Streamlit-based IT career recommendation web app developed for the UWE Bristol module `UFCEKP-30-3`.

The app collects a user's technical skills, interest areas, and career preferences, then uses an `XGBoost` classification model to predict suitable IT roles and generate a personalised learning roadmap.

## Student Information

- Student: Hein Htet Phyo
- Student ID: 25036746
- Module: UFCEKP-30-3
- University: UWE Bristol
- Year: 2026

## Project Overview

This project combines:

- a `Streamlit` user interface
- an `XGBoost` machine learning model
- CSV-based datasets for user profiles, role requirements, metadata, roadmaps, and learning resources

The app provides:

- top 3 recommended IT roles
- readiness scores across all roles
- a detailed deep-dive analysis for a selected role
- skill gap analysis
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
final_app/
├── app.py
├── README.md
├── requirements.txt
└── data/
    ├── resource_catalogue.csv
    ├── roadmap_templates.csv
    ├── role_metadata.csv
    ├── role_skill_matrix.csv
    └── user_profiles.csv
```

## Datasets

The app uses five CSV files stored in the `data/` folder:

1. `user_profiles.csv`
   Training examples of user skills, interests, preferences, and target roles.
2. `role_skill_matrix.csv`
   Required skill levels for each IT role.
3. `role_metadata.csv`
   Role descriptions and related metadata.
4. `roadmap_templates.csv`
   Template learning steps for each role.
5. `resource_catalogue.csv`
   Learning resources mapped to skills, levels, and role relevance.

## How the App Works

1. The user enters skill levels, interests, and preferences in the Streamlit interface.
2. `app.py` loads the datasets from the `data/` folder.
3. The app trains an `XGBoost` model on the profile dataset.
4. The trained model predicts ranked IT career matches.
5. The app calculates readiness scores and skill gaps.
6. A role-specific roadmap and suggested resources are displayed.

## How to Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

The app will usually open at:

```text
http://localhost:8501
```

## Notes About Google Colab

This final app is not directly connected to Google Colab.

If Colab was used during development, it was likely for:

- experimenting with data
- testing the model
- prototyping machine learning code

In the final submission, the Streamlit app runs independently from `app.py` using the local project files.

## GitHub Upload

To upload the project to GitHub:

```bash
git init
git add .
git commit -m "Initial project upload"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

You can also include any `.ipynb` notebook files in the same repository if you want to show your development or experimentation work. They do not need a live connection to `app.py`.

## Submission Zip

To create a zip file for submission:

```bash
zip -r final_app.zip final_app
```

Or compress the project folder directly from Finder on macOS.

## Future Improvements

- split the large `app.py` file into smaller modules
- save and load a pre-trained model instead of retraining at runtime
- improve mobile responsiveness further
- add model evaluation visualisations inside the app

