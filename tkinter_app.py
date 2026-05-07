import os
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import seaborn as sns
from matplotlib.figure import Figure

# Configure modern appearance
BACKGROUND_COLOR = "#1e1e1e"
FOREGROUND_COLOR = "#ffffff"
ACCENT_COLOR = "#007acc"
PANEL_COLOR = "#252526"

plt.style.use('dark_background')
sns.set_theme(style="darkgrid", rc={
    "axes.facecolor": PANEL_COLOR,
    "figure.facecolor": PANEL_COLOR,
    "text.color": FOREGROUND_COLOR,
    "axes.labelcolor": FOREGROUND_COLOR,
    "xtick.color": FOREGROUND_COLOR,
    "ytick.color": FOREGROUND_COLOR,
    "axes.edgecolor": "#333333",
    "grid.color": "#333333"
})

class ModernDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Insights - Twitter Sentiment Analysis")
        self.geometry("1400x900")
        self.configure(bg=BACKGROUND_COLOR)
        
        # Configure styles
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TFrame", background=BACKGROUND_COLOR)
        style.configure("Panel.TFrame", background=PANEL_COLOR)
        style.configure("TLabel", background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=PANEL_COLOR)
        style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), background=BACKGROUND_COLOR, foreground=ACCENT_COLOR)
        style.configure("Subheader.TLabel", font=("Segoe UI", 14), background=PANEL_COLOR, foreground=FOREGROUND_COLOR)
        style.configure("TButton", background=ACCENT_COLOR, foreground=FOREGROUND_COLOR, font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("TButton", background=[("active", "#005a9e")])
        style.configure("TNotebook", background=BACKGROUND_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL_COLOR, foreground=FOREGROUND_COLOR, padding=[15, 5], font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)], foreground=[("selected", FOREGROUND_COLOR)])

        self.dataset_path = os.path.join(os.path.dirname(__file__), 'archive', 'twitter_training.csv')
        self.df = None
        self.stats = {}
        
        self.create_layout()
        self.load_and_preprocess_data()
        self.update_stats_panel()
        self.create_visualizations()

    def create_layout(self):
        # Header
        header_frame = ttk.Frame(self, padding=(20, 10))
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Twitter Sentiment Analysis Dashboard", style="Header.TLabel").pack(side=tk.LEFT)
        
        # Main content area
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left Panel for Summary Stats
        self.left_panel = ttk.Frame(content_frame, style="Panel.TFrame", width=300)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        self.left_panel.pack_propagate(False) # Keep width
        
        ttk.Label(self.left_panel, text="Dataset Summary", style="Subheader.TLabel").pack(pady=(20, 10), padx=20, anchor="w")
        
        self.stats_frame = ttk.Frame(self.left_panel, style="Panel.TFrame")
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Right Panel for Visualizations (Notebook/Tabs)
        self.right_panel = ttk.Frame(content_frame, style="TFrame")
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(self.right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def load_and_preprocess_data(self):
        try:
            # Load Data
            self.df = pd.read_csv(self.dataset_path, header=None, names=['tweet_id', 'entity', 'sentiment', 'tweet_text'])
            
            # Basic info
            total_records_initial = len(self.df)
            
            # Handle Missing Values
            missing_text = self.df['tweet_text'].isnull().sum()
            self.df.dropna(subset=['tweet_text'], inplace=True)
            
            # Clean text (basic)
            self.df['tweet_text'] = self.df['tweet_text'].astype(str)
            self.df['tweet_length'] = self.df['tweet_text'].apply(len)
            
            # Calculate stats
            self.stats = {
                "Total Initial Records": f"{total_records_initial:,}",
                "Missing Text Dropped": f"{missing_text:,}",
                "Clean Records": f"{len(self.df):,}",
                "Unique Entities": f"{self.df['entity'].nunique()}",
                "Avg Tweet Length": f"{self.df['tweet_length'].mean():.1f} chars",
                "Sentiments": ", ".join(self.df['sentiment'].unique())
            }
        except Exception as e:
            messagebox.showerror("Data Error", f"Failed to load data: {e}")
            self.destroy()

    def update_stats_panel(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
            
        for key, value in self.stats.items():
            frame = ttk.Frame(self.stats_frame, style="Panel.TFrame")
            frame.pack(fill=tk.X, pady=10)
            ttk.Label(frame, text=key, font=("Segoe UI", 10, "bold"), foreground="#aaaaaa", style="Panel.TLabel").pack(anchor="w")
            ttk.Label(frame, text=value, font=("Segoe UI", 12), foreground=FOREGROUND_COLOR, style="Panel.TLabel").pack(anchor="w")

    def create_visualizations(self):
        # Tab 1: Overview
        tab1 = ttk.Frame(self.notebook, style="Panel.TFrame")
        self.notebook.add(tab1, text="Overview")
        self.plot_overview(tab1)
        
        # Tab 2: Entity Analysis
        tab2 = ttk.Frame(self.notebook, style="Panel.TFrame")
        self.notebook.add(tab2, text="Entity Analysis")
        self.plot_entity_analysis(tab2)
        
        # Tab 3: Text Statistics
        tab3 = ttk.Frame(self.notebook, style="Panel.TFrame")
        self.notebook.add(tab3, text="Text Statistics")
        self.plot_text_stats(tab3)

        # Tab 4: Advanced Entities
        tab4 = ttk.Frame(self.notebook, style="Panel.TFrame")
        self.notebook.add(tab4, text="Advanced Entities")
        self.plot_advanced_entities(tab4)

        # Tab 5: Word Frequencies
        tab5 = ttk.Frame(self.notebook, style="Panel.TFrame")
        self.notebook.add(tab5, text="Word Frequencies")
        self.plot_word_frequencies(tab5)

        # Tab 6: Sentiment Heatmap
        tab6 = ttk.Frame(self.notebook, style="Panel.TFrame")
        self.notebook.add(tab6, text="Sentiment Heatmap")
        self.plot_sentiment_heatmap(tab6)

    def embed_figure(self, fig, parent):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        toolbar_frame = ttk.Frame(parent, style="Panel.TFrame")
        toolbar_frame.pack(fill=tk.X, padx=10)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        toolbar.config(background=PANEL_COLOR)
        for child in toolbar.winfo_children():
            try:
                child.config(background=PANEL_COLOR)
            except:
                pass

    def plot_overview(self, parent):
        fig = Figure(figsize=(10, 6), dpi=100)
        
        # Sentiment Distribution
        ax1 = fig.add_subplot(121)
        sns.countplot(data=self.df, x='sentiment', hue='sentiment', ax=ax1, palette='viridis', order=self.df['sentiment'].value_counts().index, legend=False)
        ax1.set_title("Overall Sentiment Distribution")
        ax1.set_xlabel("Sentiment")
        ax1.set_ylabel("Count")
        ax1.tick_params(axis='x', rotation=45)
        
        # Pie chart for sentiment
        ax2 = fig.add_subplot(122)
        sentiment_counts = self.df['sentiment'].value_counts()
        ax2.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', colors=sns.color_palette('viridis', len(sentiment_counts)), startangle=90)
        ax2.set_title("Sentiment Proportions")
        
        fig.tight_layout()
        self.embed_figure(fig, parent)

    def plot_entity_analysis(self, parent):
        fig = Figure(figsize=(10, 6), dpi=100)
        
        # Top 15 Entities
        ax1 = fig.add_subplot(211)
        top_entities = self.df['entity'].value_counts().head(15)
        sns.barplot(x=top_entities.values, y=top_entities.index, hue=top_entities.index, ax=ax1, palette='mako', legend=False)
        ax1.set_title("Top 15 Mentioned Entities")
        ax1.set_xlabel("Mention Count")
        ax1.set_ylabel("Entity")
        
        # Sentiment by top 5 entities
        ax2 = fig.add_subplot(212)
        top5_entities = top_entities.head(5).index
        df_top5 = self.df[self.df['entity'].isin(top5_entities)]
        sns.countplot(data=df_top5, x='entity', hue='sentiment', ax=ax2, palette='viridis')
        ax2.set_title("Sentiment Breakdown for Top 5 Entities")
        ax2.set_xlabel("Entity")
        ax2.set_ylabel("Count")
        
        fig.tight_layout()
        self.embed_figure(fig, parent)

    def plot_text_stats(self, parent):
        fig = Figure(figsize=(10, 6), dpi=100)
        
        # Tweet Length Distribution
        ax1 = fig.add_subplot(121)
        sns.histplot(data=self.df, x='tweet_length', bins=50, ax=ax1, color='#007acc')
        ax1.set_title("Tweet Length Distribution")
        ax1.set_xlabel("Length (characters)")
        ax1.set_ylabel("Frequency")
        
        # Tweet Length by Sentiment
        ax2 = fig.add_subplot(122)
        sns.boxplot(data=self.df, x='sentiment', y='tweet_length', hue='sentiment', ax=ax2, palette='viridis', legend=False)
        ax2.set_title("Tweet Length by Sentiment")
        ax2.set_xlabel("Sentiment")
        ax2.set_ylabel("Length (characters)")
        
        fig.tight_layout()
        self.embed_figure(fig, parent)

    def plot_advanced_entities(self, parent):
        fig = Figure(figsize=(10, 6), dpi=100)
        
        # Entity with Highest Positive Sentiment %
        sentiment_pct = pd.crosstab(self.df['entity'], self.df['sentiment'], normalize='index') * 100
        
        # Top 10 Most Positive Entities
        ax1 = fig.add_subplot(121)
        top_pos = sentiment_pct.sort_values('Positive', ascending=False).head(10)['Positive']
        sns.barplot(x=top_pos.values, y=top_pos.index, hue=top_pos.index, ax=ax1, palette='Greens_r', legend=False)
        ax1.set_title("Top 10 Entities: Highest Positive %")
        ax1.set_xlabel("% Positive Tweets")
        ax1.set_ylabel("")
        
        # Top 10 Most Negative Entities
        ax2 = fig.add_subplot(122)
        top_neg = sentiment_pct.sort_values('Negative', ascending=False).head(10)['Negative']
        sns.barplot(x=top_neg.values, y=top_neg.index, hue=top_neg.index, ax=ax2, palette='Reds_r', legend=False)
        ax2.set_title("Top 10 Entities: Highest Negative %")
        ax2.set_xlabel("% Negative Tweets")
        ax2.set_ylabel("")
        
        fig.tight_layout()
        self.embed_figure(fig, parent)

    def plot_word_frequencies(self, parent):
        import re
        from collections import Counter
        
        fig = Figure(figsize=(10, 6), dpi=100)
        
        # Simple stop words list
        stop_words = set(['the', 'and', 'to', 'a', 'of', 'in', 'i', 'is', 'for', 'that', 'it', 'on', 'with', 'this', 'my', 'you', 'be', 'are', 'not', 'was', 'but', 'have', 'so', 'just', 'as', 'game', 'like', 'all', 'they', 'we'])
        
        def get_top_words(sentiment_label):
            text = " ".join(self.df[self.df['sentiment'] == sentiment_label]['tweet_text'].str.lower())
            words = re.findall(r'\b[a-z]{3,}\b', text)
            words = [w for w in words if w not in stop_words]
            return Counter(words).most_common(10)
            
        # Positive words
        ax1 = fig.add_subplot(121)
        pos_words = get_top_words('Positive')
        if pos_words:
            df_pos = pd.DataFrame(pos_words, columns=['word', 'count'])
            sns.barplot(data=df_pos, x='count', y='word', hue='word', ax=ax1, palette='Greens_r', legend=False)
        ax1.set_title("Top 10 Words in Positive Tweets")
        ax1.set_xlabel("Frequency")
        ax1.set_ylabel("")
        
        # Negative words
        ax2 = fig.add_subplot(122)
        neg_words = get_top_words('Negative')
        if neg_words:
            df_neg = pd.DataFrame(neg_words, columns=['word', 'count'])
            sns.barplot(data=df_neg, x='count', y='word', hue='word', ax=ax2, palette='Reds_r', legend=False)
        ax2.set_title("Top 10 Words in Negative Tweets")
        ax2.set_xlabel("Frequency")
        ax2.set_ylabel("")
        
        fig.tight_layout()
        self.embed_figure(fig, parent)

    def plot_sentiment_heatmap(self, parent):
        fig = Figure(figsize=(10, 6), dpi=100)
        
        # Data preparation
        heatmap_data = pd.crosstab(self.df['entity'], self.df['sentiment'])
        heatmap_data['Total'] = heatmap_data.sum(axis=1)
        heatmap_data = heatmap_data.sort_values('Total', ascending=False).drop('Total', axis=1).head(15)
        
        # Heatmap
        ax1 = fig.add_subplot(121)
        sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='mako', ax=ax1, cbar=False)
        ax1.set_title("Sentiment Density (Top 15 Entities)")
        ax1.set_xlabel("Sentiment")
        ax1.set_ylabel("Entity")
        
        # 100% Stacked Bar
        ax2 = fig.add_subplot(122)
        pct_data = heatmap_data.div(heatmap_data.sum(axis=1), axis=0) * 100
        pct_data.plot(kind='barh', stacked=True, ax=ax2, colormap='viridis')
        ax2.set_title("100% Sentiment Proportion")
        ax2.set_xlabel("Percentage (%)")
        ax2.set_ylabel("")
        ax2.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        fig.tight_layout()
        self.embed_figure(fig, parent)

if __name__ == "__main__":
    app = ModernDashboard()
    app.mainloop()
