# 🎯 CareerPath AI — Final Production App

**Student:** Hein Htet Phyo | **ID:** 25036746
**Module:** UFCEKP-30-3 | **University:** UWE Bristol | **April 2026**

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

Opens at: **http://localhost:8501**

---

## 📁 Folder Structure

```
final_app/
├── app.py              ← Main Streamlit app (990 lines)
├── requirements.txt    ← Python dependencies
├── README.md           ← This file
└── data/               ← All 5 CSV datasets
    ├── user_profiles.csv
    ├── role_skill_matrix.csv
    ├── role_metadata.csv
    ├── roadmap_templates.csv
    └── resource_catalogue.csv
```

---

## 🎨 Design

- **Theme:** Dark (matches IT_Career_Planner_UI_v2.html exactly)
- **Fonts:** Syne (display) + DM Sans (body) + DM Mono (code)
- **Background:** Animated mesh gradient + grid dots
- **Colours:** Purple (#a855f7) + Pink (#ec4899) + Cyan (#06b6d4) gradients
- **All buttons clickable** with hover effects

## ✨ Features

1. 🛠️ Technical Skills sliders (10 skills)
2. 💡 Interest Areas sliders (6 interests)
3. ⚙️ Preferences dropdowns (work type, learning style, career goal)
4. 🚀 Run button with animated spinner
5. 🏆 Top 3 role cards with readiness scores + progress bars
6. 📊 All 6 roles readiness chart
7. 🔍 Role pills to switch between roles
8. 💡 Why-it-fits card
9. 📊 Skill Gap tab with visual bars + colour-coded badges
10. 🗺️ Roadmap tab with steps, priorities, clickable resource links
11. Step indicators (1 → 2 → 3) that activate as you progress

---

## 🌐 Deploy Free on Streamlit Cloud

1. Push this folder to GitHub
2. Go to **share.streamlit.io**
3. Connect your repo → set `app.py` as main file
4. Click Deploy → live public URL instantly!
