"""
app.py - Spotify 2023 EDA Dashboard (Flask Backend)
====================================================
Loads and preprocesses the Spotify 2023 dataset,
generates 20+ interactive Plotly charts, and serves
them via API endpoints to the HTML frontend.
"""

import os, json, warnings
import numpy as np
import pandas as pd
from scipy import stats
from flask import Flask, render_template, jsonify
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.utils

warnings.filterwarnings('ignore')

app = Flask(__name__)

# ─────────────────────────────────────────────
# 1. LOAD & PREPROCESS DATA
# ─────────────────────────────────────────────
def load_data():
    path = os.path.join(os.path.dirname(__file__), 'archive', 'spotify-2023.csv')
    df = pd.read_csv(path, encoding='latin1')

    # --- Clean column names ---
    df.columns = (df.columns.str.strip()
                             .str.lower()
                             .str.replace(r'[%\(\)\s]', '_', regex=True)
                             .str.replace('__', '_')
                             .str.strip('_'))

    # Rename common variants
    col_map = {
        'artist_s__name': 'artist_name',
        'artist_s_name':  'artist_name',
        'artists_name':   'artist_name',
        'danceability__': 'danceability',
        'valence__':      'valence',
        'energy__':       'energy',
        'acousticness__': 'acousticness',
        'instrumentalness__': 'instrumentalness',
        'liveness__':     'liveness',
        'speechiness__':  'speechiness',
    }
    df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)

    # --- Fix dtypes ---
    df['streams'] = pd.to_numeric(
        df['streams'].astype(str).str.replace(',', ''), errors='coerce')
    for col in ['in_deezer_playlists', 'in_shazam_charts']:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(',', ''), errors='coerce')

    # --- Handle missing values ---
    df.dropna(subset=['streams'], inplace=True)
    num_cols = df.select_dtypes(include=np.number).columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    cat_cols = df.select_dtypes(include='object').columns
    df[cat_cols] = df[cat_cols].fillna('Unknown')

    # --- Feature Engineering ---
    df['streams_m'] = (df['streams'] / 1e6).round(2)   # Millions

    df['popularity_tier'] = pd.cut(
        df['streams'],
        bins=[0, 100e6, 500e6, 1e9, float('inf')],
        labels=['<100M', '100M-500M', '500M-1B', '>1B'])

    # Mood quadrant from valence + energy
    def mood(r):
        v = r.get('valence', 50); e = r.get('energy', 50)
        if v >= 50 and e >= 50: return 'Happy & Energetic'
        if v <  50 and e >= 50: return 'Sad & Energetic'
        if v >= 50 and e <  50: return 'Happy & Calm'
        return 'Sad & Calm'
    df['mood'] = df.apply(mood, axis=1)

    if 'mode' in df.columns:
        df['mode'] = df['mode'].astype(str).str.strip()

    return df

DF_RAW  = pd.read_csv(
    os.path.join(os.path.dirname(__file__), 'archive', 'spotify-2023.csv'),
    encoding='latin1')
DF = load_data()

# ─────────────────────────────────────────────
# 2. THEME HELPERS
# ─────────────────────────────────────────────
COLORS = ['#7c3aed','#06b6d4','#10b981','#f59e0b','#ef4444',
          '#8b5cf6','#0ea5e9','#34d399','#fbbf24','#f87171']

def theme(fig, title='', h=400):
    fig.update_layout(
        title={'text': title, 'font': {'size': 15, 'color': '#a78bfa'}, 'x': 0.01},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter,sans-serif'),
        margin=dict(l=50, r=20, t=55, b=50),
        height=h,
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)')
    return fig

def to_json(fig):
    return json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig))

# ─────────────────────────────────────────────
# 3. ROUTES
# ─────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/summary')
def api_summary():
    df = DF
    return jsonify({
        'total_tracks':    int(len(df)),
        'total_artists':   int(df['artist_name'].nunique()) if 'artist_name' in df.columns else 'N/A',
        'total_streams':   f"{df['streams'].sum()/1e9:.2f}B",
        'avg_bpm':         int(df['bpm'].mean()) if 'bpm' in df.columns else 'N/A',
        'avg_danceability':f"{df['danceability'].mean():.1f}%" if 'danceability' in df.columns else 'N/A',
        'avg_energy':      f"{df['energy'].mean():.1f}%" if 'energy' in df.columns else 'N/A',
        'top_artist':      df.groupby('artist_name')['streams'].sum().idxmax() if 'artist_name' in df.columns else 'N/A',
        'top_track':       df.nlargest(1,'streams')['track_name'].values[0] if 'track_name' in df.columns else 'N/A',
        'missing_before':  int(DF_RAW.isnull().sum().sum()),
        'missing_after':   int(df.isnull().sum().sum()),
        'year_range':      f"{int(df['released_year'].min())} – {int(df['released_year'].max())}",
    })


# Chart 1 – Top 10 Tracks
@app.route('/api/chart/top_tracks')
def chart_top_tracks():
    d = DF.nlargest(10,'streams').sort_values('streams')
    fig = go.Figure(go.Bar(
        x=d['streams_m'], y=d['track_name'], orientation='h',
        marker=dict(color=d['streams_m'], colorscale='Viridis', showscale=True,
                    colorbar=dict(title='Streams (M)')),
        text=d['streams_m'].apply(lambda x: f'{x:.0f}M'), textposition='outside',
        hovertemplate='<b>%{y}</b><br>Streams: %{x:.0f}M<extra></extra>'))
    theme(fig,'🎵 Top 10 Most Streamed Tracks', 420)
    fig.update_layout(xaxis_title='Streams (Millions)')
    return jsonify(to_json(fig))


# Chart 2 – Top 10 Artists
@app.route('/api/chart/top_artists')
def chart_top_artists():
    d = DF.groupby('artist_name')['streams_m'].sum().nlargest(10).sort_values()
    fig = go.Figure(go.Bar(
        x=d.values, y=d.index, orientation='h',
        marker=dict(color=d.values, colorscale='Plasma'),
        text=[f'{v:.0f}M' for v in d.values], textposition='outside',
        hovertemplate='<b>%{y}</b><br>Streams: %{x:.0f}M<extra></extra>'))
    theme(fig,'🎤 Top 10 Artists by Total Streams', 420)
    fig.update_layout(xaxis_title='Total Streams (Millions)')
    return jsonify(to_json(fig))


# Chart 3 – Streams Histogram
@app.route('/api/chart/streams_dist')
def chart_streams_dist():
    fig = go.Figure(go.Histogram(
        x=DF['streams_m'], nbinsx=50,
        marker=dict(color='#7c3aed', opacity=0.85, line=dict(color='#a78bfa',width=0.5)),
        hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'))
    theme(fig,'📊 Distribution of Streams (Millions)', 380)
    fig.update_layout(xaxis_title='Streams (Millions)', yaxis_title='Track Count')
    return jsonify(to_json(fig))


# Chart 4 – Monthly Releases
@app.route('/api/chart/monthly_releases')
def chart_monthly_releases():
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    d = DF.groupby('released_month').size().reset_index(name='count')
    d['month'] = d['released_month'].apply(lambda x: months[int(x)-1])
    fig = go.Figure(go.Bar(
        x=d['month'], y=d['count'],
        marker=dict(color=d['count'], colorscale='Turbo'),
        text=d['count'], textposition='outside',
        hovertemplate='<b>%{x}</b><br>Tracks: %{y}<extra></extra>'))
    theme(fig,'📅 Tracks Released Per Month', 380)
    fig.update_layout(xaxis_title='Month', yaxis_title='Number of Tracks')
    return jsonify(to_json(fig))


# Chart 5 – Yearly Trend (dual axis)
@app.route('/api/chart/yearly_trend')
def chart_yearly_trend():
    d = DF.groupby('released_year').agg(count=('streams','count'), avg=('streams_m','mean')).reset_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=d['released_year'], y=d['count'], name='Tracks Released',
        marker_color='#7c3aed', opacity=0.75,
        hovertemplate='Year: %{x}<br>Tracks: %{y}<extra></extra>'), secondary_y=False)
    fig.add_trace(go.Scatter(x=d['released_year'], y=d['avg'], name='Avg Streams (M)',
        mode='lines+markers', line=dict(color='#06b6d4', width=2.5), marker=dict(size=6),
        hovertemplate='Year: %{x}<br>Avg: %{y:.1f}M<extra></extra>'), secondary_y=True)
    theme(fig,'📈 Release Trend & Avg Streams by Year', 400)
    fig.update_yaxes(title_text='Track Count', secondary_y=False, gridcolor='rgba(255,255,255,0.06)')
    fig.update_yaxes(title_text='Avg Streams (M)', secondary_y=True, gridcolor='rgba(255,255,255,0.06)')
    fig.update_layout(legend=dict(orientation='h', y=-0.25))
    return jsonify(to_json(fig))


# Chart 6 – Correlation Heatmap
@app.route('/api/chart/correlation')
def chart_correlation():
    feats = [c for c in ['danceability','valence','energy','acousticness',
             'instrumentalness','liveness','speechiness','bpm','streams_m'] if c in DF.columns]
    corr = DF[feats].corr().round(2)
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index,
        colorscale='RdBu', zmid=0,
        text=corr.values, texttemplate='%{text}', textfont={'size':10},
        hovertemplate='%{x} vs %{y}<br>r = %{z}<extra></extra>',
        colorbar=dict(title='r')))
    theme(fig,'🔥 Audio Feature Correlation Heatmap', 480)
    return jsonify(to_json(fig))


# Chart 7 – BPM Violin
@app.route('/api/chart/bpm_dist')
def chart_bpm_dist():
    fig = go.Figure()
    for mode_val, col in [('Major','#7c3aed'),('Minor','#06b6d4')]:
        sub = DF[DF['mode'] == mode_val] if 'mode' in DF.columns else DF
        fig.add_trace(go.Violin(x=sub['bpm'], name=mode_val,
            fillcolor=col, line_color=col, opacity=0.72, meanline_visible=True))
    theme(fig,'🎵 BPM Distribution by Mode', 380)
    fig.update_layout(xaxis_title='BPM', violinmode='overlay')
    return jsonify(to_json(fig))


# Chart 8 – Danceability vs Energy
@app.route('/api/chart/dance_energy')
def chart_dance_energy():
    fig = px.scatter(DF, x='danceability', y='energy',
        color='streams_m', size='streams_m', size_max=22,
        color_continuous_scale='Viridis',
        hover_name='track_name',
        hover_data={'artist_name':True,'streams_m':':.0f'},
        labels={'danceability':'Danceability (%)','energy':'Energy (%)','streams_m':'Streams (M)'})
    theme(fig,'💃 Danceability vs Energy', 430)
    return jsonify(to_json(fig))


# Chart 9 – Valence vs Energy Mood Quadrants
@app.route('/api/chart/valence_energy')
def chart_valence_energy():
    fig = px.scatter(DF, x='valence', y='energy', color='mood',
        color_discrete_sequence=COLORS, opacity=0.65,
        hover_name='track_name',
        hover_data={'artist_name':True,'streams_m':':.0f'},
        labels={'valence':'Valence (%)','energy':'Energy (%)'})
    fig.add_hline(y=50, line_dash='dash', line_color='rgba(255,255,255,0.25)')
    fig.add_vline(x=50, line_dash='dash', line_color='rgba(255,255,255,0.25)')
    theme(fig,'😊 Mood Quadrants: Valence vs Energy', 430)
    return jsonify(to_json(fig))


# Chart 10 – Key Distribution
@app.route('/api/chart/key_dist')
def chart_key_dist():
    d = DF['key'].value_counts().reset_index()
    d.columns = ['key','count']
    fig = go.Figure(go.Bar(x=d['key'], y=d['count'],
        marker=dict(color=d['count'], colorscale='Sunset'),
        text=d['count'], textposition='outside',
        hovertemplate='Key: <b>%{x}</b><br>Tracks: %{y}<extra></extra>'))
    theme(fig,'🎹 Musical Key Distribution', 380)
    fig.update_layout(xaxis_title='Key', yaxis_title='Track Count')
    return jsonify(to_json(fig))


# Chart 11 – Mode Pie
@app.route('/api/chart/mode_pie')
def chart_mode_pie():
    d = DF['mode'].value_counts()
    fig = go.Figure(go.Pie(labels=d.index, values=d.values, hole=0.45,
        marker=dict(colors=['#7c3aed','#06b6d4'], line=dict(color='#0f111a',width=2)),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value} tracks<br>%{percent}<extra></extra>'))
    theme(fig,'🎼 Major vs Minor Mode', 380)
    return jsonify(to_json(fig))


# Chart 12 – Platform Comparison
@app.route('/api/chart/platform_compare')
def chart_platform_compare():
    platforms = {'Spotify':'in_spotify_playlists','Apple':'in_apple_playlists','Deezer':'in_deezer_playlists'}
    cols = {k:v for k,v in platforms.items() if v in DF.columns}
    base_col = list(cols.values())[0]
    top = DF.nlargest(10, base_col)[['track_name'] + list(cols.values())].copy()
    top['track_name'] = top['track_name'].apply(lambda x: x[:22]+'…' if len(str(x))>22 else x)
    fig = go.Figure()
    for (name, col), color in zip(cols.items(), COLORS):
        fig.add_trace(go.Bar(name=name, x=top['track_name'], y=top[col],
            marker_color=color, opacity=0.87,
            hovertemplate=f'<b>%{{x}}</b><br>{name} Playlists: %{{y}}<extra></extra>'))
    theme(fig,'🌐 Platform Playlist Presence — Top 10 Tracks', 430)
    fig.update_layout(barmode='group', xaxis_tickangle=-30,
                      xaxis_title='Track', yaxis_title='Playlist Count')
    return jsonify(to_json(fig))


# Chart 13 – Feature Box Plots
@app.route('/api/chart/feature_boxplots')
def chart_feature_boxplots():
    feats = [c for c in ['danceability','valence','energy','acousticness',
                          'liveness','speechiness','instrumentalness'] if c in DF.columns]
    fig = go.Figure()
    for i, f in enumerate(feats):
        fig.add_trace(go.Box(y=DF[f], name=f.capitalize(),
            marker_color=COLORS[i % len(COLORS)], boxmean='sd',
            hovertemplate=f'<b>{f}</b><br>Value: %{{y}}<extra></extra>'))
    theme(fig,'📦 Audio Feature Distributions (Box Plots)', 430)
    fig.update_layout(yaxis_title='Value (%)', showlegend=False)
    return jsonify(to_json(fig))


# Chart 14 – Outlier Detection (Z-Score)
@app.route('/api/chart/outliers')
def chart_outliers():
    df = DF.copy()
    df['z'] = np.abs(stats.zscore(df['streams_m'].dropna()))
    df = df.dropna(subset=['z'])
    df['outlier'] = df['z'] > 3
    norm = df[~df['outlier']]; out = df[df['outlier']]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=norm.index, y=norm['streams_m'],
        mode='markers', name='Normal',
        marker=dict(color='#7c3aed', size=4, opacity=0.5),
        text=norm.get('track_name', norm.index),
        hovertemplate='Track: %{text}<br>Streams: %{y:.0f}M<extra></extra>'))
    fig.add_trace(go.Scatter(x=out.index, y=out['streams_m'],
        mode='markers+text', name='Outlier (Z>3)',
        marker=dict(color='#ef4444', size=11, symbol='diamond'),
        text=out.get('track_name', out.index),
        textposition='top center', textfont=dict(size=9),
        hovertemplate='<b>%{text}</b><br>Streams: %{y:.0f}M<extra></extra>'))
    theme(fig,'🔍 Outlier Detection — Streams (Z-Score)', 430)
    fig.update_layout(xaxis_title='Track Index', yaxis_title='Streams (M)')
    return jsonify(to_json(fig))


# Chart 15 – Mood Distribution
@app.route('/api/chart/mood_dist')
def chart_mood_dist():
    d = DF['mood'].value_counts().reset_index()
    d.columns = ['mood','count']
    mood_colors = {'Happy & Energetic':'#f59e0b','Sad & Energetic':'#ef4444',
                   'Happy & Calm':'#10b981','Sad & Calm':'#7c3aed'}
    fig = go.Figure(go.Pie(labels=d['mood'], values=d['count'], hole=0.42,
        marker=dict(colors=[mood_colors.get(m,'#8b5cf6') for m in d['mood']],
                    line=dict(color='#0f111a',width=2)),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value} tracks (%{percent})<extra></extra>'))
    theme(fig,'🎭 Mood Distribution (Valence × Energy)', 390)
    return jsonify(to_json(fig))


# Chart 16 – Top Keys by Streams
@app.route('/api/chart/key_streams')
def chart_key_streams():
    d = DF.groupby('key')['streams_m'].sum().sort_values(ascending=False).reset_index()
    fig = go.Figure(go.Bar(x=d['key'], y=d['streams_m'],
        marker=dict(color=d['streams_m'], colorscale='Electric'),
        text=d['streams_m'].apply(lambda x: f'{x:.0f}M'), textposition='outside',
        hovertemplate='Key: <b>%{x}</b><br>Total Streams: %{y:.0f}M<extra></extra>'))
    theme(fig,'🎹 Total Streams per Musical Key', 380)
    fig.update_layout(xaxis_title='Key', yaxis_title='Total Streams (Millions)')
    return jsonify(to_json(fig))


# Chart 17 – Energy by Mode Violin
@app.route('/api/chart/energy_mode')
def chart_energy_mode():
    fig = go.Figure()
    for mode_val, col in [('Major','#7c3aed'),('Minor','#06b6d4')]:
        sub = DF[DF['mode'] == mode_val] if 'mode' in DF.columns else DF
        fig.add_trace(go.Violin(y=sub['energy'], name=mode_val,
            fillcolor=col, line_color=col, opacity=0.72,
            meanline_visible=True, box_visible=True))
    theme(fig,'⚡ Energy Distribution: Major vs Minor', 390)
    fig.update_layout(yaxis_title='Energy (%)')
    return jsonify(to_json(fig))


# Chart 18 – BPM vs Danceability
@app.route('/api/chart/bpm_dance')
def chart_bpm_dance():
    fig = px.scatter(DF, x='bpm', y='danceability',
        color='energy', color_continuous_scale='Turbo',
        size='streams_m', size_max=18,
        hover_name='track_name' if 'track_name' in DF.columns else None,
        labels={'bpm':'BPM','danceability':'Danceability (%)','energy':'Energy (%)','streams_m':'Streams (M)'})
    theme(fig,'🥁 BPM vs Danceability (size = Streams)', 430)
    return jsonify(to_json(fig))


# Chart 19 – Liveness vs Speechiness
@app.route('/api/chart/live_speech')
def chart_live_speech():
    fig = px.scatter(DF, x='liveness', y='speechiness',
        color='popularity_tier',
        color_discrete_sequence=COLORS,
        hover_name='track_name' if 'track_name' in DF.columns else None,
        hover_data={'streams_m':':.0f','artist_name':True},
        labels={'liveness':'Liveness (%)','speechiness':'Speechiness (%)'},
        opacity=0.7)
    theme(fig,'🎙️ Liveness vs Speechiness (by Popularity Tier)', 430)
    return jsonify(to_json(fig))


# Chart 20 – Statistical Summary (Descriptive Stats Table)
@app.route('/api/chart/stats_table')
def chart_stats_table():
    feats = [c for c in ['streams_m','bpm','danceability','valence','energy',
                          'acousticness','liveness','speechiness'] if c in DF.columns]
    desc = DF[feats].describe().round(2)
    fig = go.Figure(go.Table(
        header=dict(values=['Statistic'] + list(desc.columns),
            fill_color='#2d1b69', line_color='rgba(255,255,255,0.1)',
            font=dict(color='#a78bfa', size=12), align='center'),
        cells=dict(values=[desc.index] + [desc[c] for c in desc.columns],
            fill_color=[['#1a1033','#15192e']*10],
            line_color='rgba(255,255,255,0.06)',
            font=dict(color='#e2e8f0', size=11), align='center')))
    theme(fig,'📊 Descriptive Statistics Summary', 430)
    return jsonify(to_json(fig))


# Chart 21 – Acousticness vs Instrumentalness
@app.route('/api/chart/acoustic_instrument')
def chart_acoustic_instrument():
    fig = px.scatter(DF, x='acousticness', y='instrumentalness',
        color='streams_m', color_continuous_scale='Magma',
        size='streams_m', size_max=18, opacity=0.75,
        hover_name='track_name' if 'track_name' in DF.columns else None,
        labels={'acousticness':'Acousticness (%)','instrumentalness':'Instrumentalness (%)','streams_m':'Streams (M)'})
    theme(fig,'🎸 Acousticness vs Instrumentalness', 430)
    return jsonify(to_json(fig))


# Chart 22 – Popularity Tier Distribution
@app.route('/api/chart/popularity_tier')
def chart_popularity_tier():
    d = DF['popularity_tier'].value_counts().reset_index()
    d.columns = ['tier','count']
    fig = go.Figure(go.Bar(
        x=d['tier'].astype(str), y=d['count'],
        marker=dict(color=COLORS[:len(d)]),
        text=d['count'], textposition='outside',
        hovertemplate='Tier: <b>%{x}</b><br>Tracks: %{y}<extra></extra>'))
    theme(fig,'🏆 Tracks by Popularity Tier (Stream Count)', 380)
    fig.update_layout(xaxis_title='Popularity Tier', yaxis_title='Track Count')
    return jsonify(to_json(fig))


if __name__ == '__main__':
    print("=" * 55)
    print("  🎵 Spotify EDA Dashboard running!")
    print("  Open: http://127.0.0.1:5000")
    print("=" * 55)
    app.run(debug=True, host='127.0.0.1', port=5000)
