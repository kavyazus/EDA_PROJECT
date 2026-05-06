# 🎵 Spotify 2023 — Exploratory Data Analysis Dashboard

An interactive EDA dashboard built with **Flask + Plotly** for the  
[Most Streamed Spotify Songs 2023](https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023) dataset.

---

## 📁 Project Structure

```
EDA_project/
├── archive/
│   └── spotify-2023.csv        # Raw dataset
├── app.py                      # Flask backend (data loading + 22 chart APIs)
├── templates/
│   └── index.html              # Dashboard HTML
├── static/
│   ├── style.css               # Dark glassmorphism theme
│   └── dashboard.js            # Tab switching + Plotly rendering
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🚀 How to Run Locally (Step-by-Step)

### Step 1 — Make sure Python is installed
```
python --version   # should show Python 3.8+
```
If not installed, download from https://www.python.org/downloads/

---

### Step 2 — Open a terminal in the project folder
```
cd C:\Users\kavya\Desktop\EDA_project
```

---

### Step 3 — Create a virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

---

### Step 4 — Install all dependencies
```bash
pip install -r requirements.txt
```

---

### Step 5 — Run the Flask app
```bash
python app.py
```

You should see:
```
=======================================================
  🎵 Spotify EDA Dashboard running!
  Open: http://127.0.0.1:5000
=======================================================
```

---

### Step 6 — Open the dashboard
Open your browser and go to:
```
http://127.0.0.1:5000
```

---

## 📊 What's Inside

### Data Preprocessing
| Step | Details |
|------|---------|
| Encoding fix | CSV loaded with `latin1` to handle special characters |
| Column rename | Standardized all column names (lowercase, no spaces) |
| Type conversion | `streams`, `in_deezer_playlists` converted to numeric |
| Missing values | Rows with missing `streams` dropped; others filled with median |
| Feature engineering | `streams_m`, `popularity_tier`, `mood`, `mode_label` created |

### 22 Interactive Charts

| # | Chart | Insight |
|---|-------|---------|
| 1 | Top 10 Most Streamed Tracks | Bar chart with color scale |
| 2 | Top 10 Artists by Streams | Aggregated per artist |
| 3 | Streams Distribution | Heavy right skew |
| 4 | Popularity Tier Breakdown | Pie/bar of stream ranges |
| 5 | Outlier Detection | Z-score method, Z>3 flagged |
| 6 | Release Year Trend | Dual-axis: count + avg streams |
| 7 | Monthly Release Pattern | Best months to release |
| 8 | Correlation Heatmap | Energy↔Acousticness = −0.7 |
| 9 | Danceability vs Energy | Scatter, colored by streams |
| 10 | Mood Quadrants | Valence × Energy |
| 11 | Feature Box Plots | All 7 audio features |
| 12 | Mood Distribution | Pie of 4 mood categories |
| 13 | BPM by Mode | Violin plot Major vs Minor |
| 14 | BPM vs Danceability | Scatter with energy color |
| 15 | Energy by Mode | Violin + box |
| 16 | Acousticness vs Instrumentalness | Scatter |
| 17 | Liveness vs Speechiness | Colored by popularity |
| 18 | Musical Key Distribution | Bar chart all keys |
| 19 | Major vs Minor Pie | Donut chart |
| 20 | Streams by Musical Key | Total streams per key |
| 21 | Platform Comparison | Spotify vs Apple vs Deezer |
| 22 | Descriptive Stats Table | Mean, std, min, max, quartiles |

---

## 🔬 Key Insights

1. **Streams are heavily right-skewed** — a handful of mega-hits dominate
2. **Energy and Acousticness are strongly negatively correlated (r ≈ −0.7)**
3. **Major key + ~120 BPM** is the "hit formula" for mainstream pop
4. **January & May** are the most popular release months
5. **Spotify playlists** dwarf Apple Music and Deezer by 10×
6. **Older songs (2017–2020)** average higher streams — more time to accumulate plays

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Data | Pandas, NumPy, SciPy |
| Charts | Plotly (served as JSON, rendered by Plotly.js) |
| Frontend | HTML5, Vanilla CSS, Vanilla JS |
| Theme | Dark glassmorphism, Inter font |

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Port 5000 already in use | Change `port=5000` to `port=5001` in `app.py` |
| Charts not loading | Check browser console (F12) for errors |
| Encoding error on CSV | The app already uses `encoding='latin1'` — should be fine |

---

*Made with ❤️ · Dataset from Kaggle*
