# Twitter Sentiment Analysis - EDA Dashboard

A modern, professional desktop application built with Python (**Tkinter**, **Pandas**, and **Seaborn**) to perform Exploratory Data Analysis (EDA) on Twitter sentiment data. This tool provides an elegant dark-themed interface to interactively explore tweet lengths, entity distributions, word frequencies, and sentiment proportionality.

## Features

- **Modern Dark UI**: A sleek, professional interface built entirely in Tkinter using `ttk` styles and a unified `#1e1e1e` color palette.
- **Dynamic EDA Tabs**: 6 distinct analytical views rendered with high-quality Matplotlib & Seaborn charts:
  - **Overview**: Overall Sentiment Distribution (Bar & Pie Charts)
  - **Entity Analysis**: Top 15 Mentioned Entities & Sentiment Breakdown for the Top 5
  - **Text Statistics**: Tweet Length Distribution (Histogram) & Tweet Length grouped by Sentiment (Box Plot)
  - **Advanced Entities**: Top 10 Entities ranked by highest Positive and highest Negative sentiment percentages
  - **Word Frequencies**: Top 10 most common words occurring in Positive vs. Negative tweets (excluding standard stop words)
  - **Sentiment Heatmap**: Sentiment density mapped across the top 15 entities and a 100% proportional stacked bar chart
- **Extensive Data Preprocessing**: A robust pipeline that performs regex-based cleaning, URL/special character removal, text normalization (lowercasing), and automatic duplicate detection to ensure high-quality insights.

## Installation & Setup

1. **Prerequisites**: Ensure you have Python 3.8+ installed.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Required packages: `pandas`, `numpy`, `matplotlib`, `seaborn`)*
3. **Dataset**: Ensure your Twitter dataset (`twitter_training.csv`) is present inside the `archive/` folder relative to the root project directory.

## Running the Application

Execute the Python script to launch the Tkinter dashboard:

```bash
python tkinter_app.py
```

## Project Structure
```
EDA_PROJECT/
├── archive/
│   └── twitter_training.csv   # The raw Twitter dataset
├── tkinter_app.py             # Main application script & UI layout
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Built With
- **Python 3**
- **Tkinter** (Native Python GUI)
- **Pandas** & **NumPy** (Data processing)
- **Matplotlib** & **Seaborn** (Data visualization)
