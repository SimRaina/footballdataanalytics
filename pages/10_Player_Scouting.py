import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from utils.loader import load_data, get_current_season, get_available_seasons

st.set_page_config(page_title="Player Scouting", layout="wide")

st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .stMetric {
        background-color: #1c1f26;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 Player Scouting")
st.markdown("Generate professional scouting reports for players based on match performance")

# Helper function to safely convert values to int
def safe_int(value, default=0):
    """Safely convert value to int, handling malformed data like '28-232'"""
    if pd.isna(value) or value == '' or value == 'N/A':
        return default
    try:
        # If it's already a number, convert directly
        return int(float(value))
    except (ValueError, TypeError):
        # If it has special characters, try to extract first numeric part
        try:
            numeric_part = ''.join(c for c in str(value) if c.isdigit() or c == '.')
            if numeric_part:
                return int(float(numeric_part))
        except (ValueError, TypeError):
            pass
        return default

# Load data
teams, players, matches, seasons, teams_socials = load_data()
current_season = get_current_season()

# Define competencies based on position
COMPETENCIES = {
    "Forward": [
        "Finishing",
        "Positioning",
        "Movement in Box",
        "First Touch",
        "Physical Strength",
        "Game Intelligence",
        "Work Rate",
        "Heading Ability"
    ],
    "Winger": [
        "Pace",
        "Dribbling",
        "Crossing",
        "Shooting",
        "Work Rate",
        "Defensive Work Rate",
        "Decision Making",
        "Physical Strength"
    ],
    "Midfielder": [
        "Passing Accuracy",
        "Vision",
        "Ball Control",
        "Positioning",
        "Work Rate",
        "Tackling",
        "Game Intelligence",
        "Physical Strength"
    ],
    "Defender": [
        "Marking",
        "Tackling",
        "Positioning",
        "Heading",
        "Physical Strength",
        "Passing Accuracy",
        "Concentration",
        "Game Reading"
    ]
}

# Get available seasons
available_seasons = get_available_seasons(matches)

st.markdown("---")

# Season selection
selected_season = st.selectbox(
    "Select Season",
    available_seasons,
    index=available_seasons.index(current_season) if current_season in available_seasons else 0
)

st.markdown("---")

# Get matches for selected season
season_matches = matches[matches["season"] == selected_season].copy()
completed_matches = season_matches[season_matches["match_status"] == "completed"].sort_values("date", ascending=False)

st.markdown("---")

# Selection section
col1, col2, col3 = st.columns(3)

with col1:
    selected_player_name = st.selectbox("Select Player", players["name"].unique())
    selected_player = players[players["name"] == selected_player_name].iloc[0]
    selected_team = selected_player["team"]
    player_position = selected_player["position"]

with col2:
    # Get matches involving the selected team
    team_matches = completed_matches[
        (completed_matches["home_team"] == selected_team) | 
        (completed_matches["away_team"] == selected_team)
    ]
    
    if len(team_matches) > 0:
        match_options = [f"{row['date']} | {row['home_team']} vs {row['away_team']}" 
                        for _, row in team_matches.iterrows()]
        selected_match_idx = st.selectbox("Select Match", range(len(match_options)), 
                                         format_func=lambda i: match_options[i])
        selected_match = team_matches.iloc[selected_match_idx]
    else:
        st.warning("No completed matches found for this team")
        st.stop()

st.markdown("---")

# Display match and player information
col1, col2, col3 = st.columns(3)

with col1:
    st.write("**Match Details**")
    st.write(f"📅 Date: {selected_match['date']}")
    st.write(f"🏆 {selected_match['home_team']} vs {selected_match['away_team']}")
    st.write(f"Score: {safe_int(selected_match['home_goals'])} - {safe_int(selected_match['away_goals'])}")
    st.write(f"📍 Venue: {selected_match['venue']}")

with col2:
    st.write("**Player Information**")
    st.write(f"👤 Name: {selected_player['name']}")
    st.write(f"⚽ Team: {selected_player['team']}")
    st.write(f"📍 Position: {player_position}")
    st.write(f"🌍 Nationality: {selected_player.get('nationality', 'N/A')}")
    player_age = safe_int(selected_player.get('age', 0))
    age_display = str(player_age) if player_age > 0 else "N/A"
    st.write(f"📅 Age: {age_display}")

with col3:
    st.write("**Season Statistics**")
    st.write(f"⚽ Goals: {safe_int(selected_player['goals'])}")
    st.write(f"🎯 Assists: {safe_int(selected_player['assists'])}")
    st.write(f"⏱️ Minutes: {safe_int(selected_player['minutes'])}")
    minutes_played = safe_int(selected_player['minutes'])
    goals_per_90 = (safe_int(selected_player['goals']) / (minutes_played / 90)) if minutes_played > 0 else 0
    st.write(f"📊 Goals/90: {goals_per_90:.2f}")

st.markdown("---")

# Scouting form
st.subheader("📋 Scouting Assessment")

# Get competencies for player's position
position = player_position
competencies = COMPETENCIES.get(position, COMPETENCIES["Midfielder"])

st.write(f"**Competencies for {position}:**")

# Create competency assessment form
competency_ratings = {}
cols = st.columns(2)

for idx, comp in enumerate(competencies):
    with cols[idx % 2]:
        competency_ratings[comp] = st.slider(
            f"{comp}",
            min_value=1,
            max_value=10,
            value=5,
            help=f"Rate {comp} from 1 (Poor) to 10 (Excellent)"
        )

st.markdown("---")

# Scout notes
st.subheader("📝 Scout Notes")

scout_name = st.text_input("Scout Name", placeholder="Enter your name")
scout_comments = st.text_area(
    "Detailed Assessment",
    placeholder="Write your detailed scouting report...",
    height=200
)

strengths = st.text_area(
    "Key Strengths",
    placeholder="List the player's key strengths",
    height=100
)

improvements = st.text_area(
    "Areas for Improvement",
    placeholder="Areas where the player can improve",
    height=100
)

overall_rating = st.slider(
    "Overall Rating",
    min_value=1,
    max_value=10,
    value=6,
    help="Overall assessment of the player"
)

recommendation = st.selectbox(
    "Recommendation",
    ["Target", "Monitor", "Pass", "Follow-up Required"]
)

st.markdown("---")

# PDF Generation Function
def generate_pdf(scout_data):
    """Generate PDF scouting report"""
    buffer = io.BytesIO()
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e90ff'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e90ff'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    # Title
    elements.append(Paragraph("⚽ ISL SCOUTING REPORT", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Report meta - Make absolutely sure data is converted to string
    report_date = datetime.now().strftime("%d %B %Y")
    report_time = datetime.now().strftime("%d %B %Y at %H:%M")
    scout_name_str = str(scout_data.get('scout_name', 'Anonymous Scout'))
    
    meta_data = [
        [Paragraph("<b>Report Date:</b>", styles['Normal']), Paragraph(report_date, styles['Normal'])],
        [Paragraph("<b>Scout:</b>", styles['Normal']), Paragraph(scout_name_str, styles['Normal'])],
        [Paragraph("<b>Report Generated:</b>", styles['Normal']), Paragraph(report_time, styles['Normal'])]
    ]
    
    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#505050')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Match Information
    elements.append(Paragraph("MATCH INFORMATION", heading_style))
    
    match_date_str = str(scout_data.get('match_date', 'N/A')) if scout_data.get('match_date') else 'N/A'
    home_team_str = str(scout_data.get('home_team', 'N/A')) if scout_data.get('home_team') else 'N/A'
    away_team_str = str(scout_data.get('away_team', 'N/A')) if scout_data.get('away_team') else 'N/A'
    home_goals_str = str(int(safe_int(scout_data.get('home_goals', 0))))
    away_goals_str = str(int(safe_int(scout_data.get('away_goals', 0))))
    venue_str = str(scout_data.get('venue', 'N/A')) if scout_data.get('venue') else 'N/A'
    gameweek_str = str(int(safe_int(scout_data.get('gameweek', 0))))
    
    match_data = [
        [Paragraph("<b>Date:</b>", styles['Normal']), Paragraph(match_date_str, styles['Normal'])],
        [Paragraph("<b>Match:</b>", styles['Normal']), Paragraph(f"{home_team_str} vs {away_team_str}", styles['Normal'])],
        [Paragraph("<b>Score:</b>", styles['Normal']), Paragraph(f"{home_goals_str} - {away_goals_str}", styles['Normal'])],
        [Paragraph("<b>Venue:</b>", styles['Normal']), Paragraph(venue_str, styles['Normal'])],
        [Paragraph("<b>Gameweek:</b>", styles['Normal']), Paragraph(gameweek_str, styles['Normal'])]
    ]
    
    match_table = Table(match_data, colWidths=[2*inch, 4*inch])
    match_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#505050')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(match_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Player Information
    elements.append(Paragraph("PLAYER INFORMATION", heading_style))
    
    player_name_str = str(scout_data.get('player_name', 'N/A')) if scout_data.get('player_name') else 'N/A'
    team_str = str(scout_data.get('team', 'N/A')) if scout_data.get('team') else 'N/A'
    position_str = str(scout_data.get('position', 'N/A')) if scout_data.get('position') else 'N/A'
    nationality_str = str(scout_data.get('nationality', 'N/A')) if scout_data.get('nationality') else 'N/A'
    age_str = str(safe_int(scout_data.get('age', 0)))
    age_display = age_str if age_str != '0' else 'N/A'
    goals_str = str(safe_int(scout_data.get('goals', 0)))
    assists_str = str(safe_int(scout_data.get('assists', 0)))
    minutes_str = str(safe_int(scout_data.get('minutes', 0)))
    
    player_data = [
        [Paragraph("<b style='color:white'>Name:</b>", styles['Normal']), Paragraph(player_name_str, styles['Normal'])],
        [Paragraph("<b style='color:white'>Team:</b>", styles['Normal']), Paragraph(team_str, styles['Normal'])],
        [Paragraph("<b style='color:white'>Position:</b>", styles['Normal']), Paragraph(position_str, styles['Normal'])],
        [Paragraph("<b style='color:white'>Nationality:</b>", styles['Normal']), Paragraph(nationality_str, styles['Normal'])],
        [Paragraph("<b style='color:white'>Age:</b>", styles['Normal']), Paragraph(age_display, styles['Normal'])],
        [Paragraph("<b style='color:white'>Career Goals:</b>", styles['Normal']), Paragraph(goals_str, styles['Normal'])],
        [Paragraph("<b style='color:white'>Career Assists:</b>", styles['Normal']), Paragraph(assists_str, styles['Normal'])],
        [Paragraph("<b style='color:white'>Minutes Played:</b>", styles['Normal']), Paragraph(minutes_str, styles['Normal'])]
    ]
    
    player_table = Table(player_data, colWidths=[2*inch, 4*inch])
    player_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#505050')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(player_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Competency Assessment
    elements.append(Paragraph("COMPETENCY ASSESSMENT", heading_style))
    comp_data = [[Paragraph("<b>Competency</b>", styles['Normal']), Paragraph("<b>Rating</b>", styles['Normal']), 
                  Paragraph("<b>Competency</b>", styles['Normal']), Paragraph("<b>Rating</b>", styles['Normal'])]]
    
    competencies = scout_data.get('competencies', {})
    comp_list = list(competencies.items())
    for i in range(0, len(comp_list), 2):
        row = [Paragraph(str(comp_list[i][0]), styles['Normal']), Paragraph(str(comp_list[i][1]), styles['Normal'])]
        if i + 1 < len(comp_list):
            row.extend([Paragraph(str(comp_list[i + 1][0]), styles['Normal']), Paragraph(str(comp_list[i + 1][1]), styles['Normal'])])
        else:
            row.extend([Paragraph("", styles['Normal']), Paragraph("", styles['Normal'])])
        comp_data.append(row)
    
    comp_table = Table(comp_data, colWidths=[2*inch, 1*inch, 2*inch, 1*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e90ff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#505050')),
    ]))
    elements.append(comp_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Assessment Details
    elements.append(Paragraph("DETAILED ASSESSMENT", heading_style))
    
    overall_rating_str = str(scout_data.get('overall_rating', 'N/A'))
    recommendation_str = str(scout_data.get('recommendation', 'N/A'))
    strengths_str = str(scout_data.get('strengths', 'N/A')) if scout_data.get('strengths') else "N/A"
    improvements_str = str(scout_data.get('improvements', 'N/A')) if scout_data.get('improvements') else "N/A"
    comments_str = str(scout_data.get('comments', 'N/A')) if scout_data.get('comments') else "N/A"
    
    elements.append(Paragraph(f"<b>Overall Rating:</b> {overall_rating_str}/10", styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"<b>Recommendation:</b> {recommendation_str}", styles['Normal']))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("<b>Key Strengths:</b>", styles['Normal']))
    elements.append(Paragraph(strengths_str, styles['Normal']))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("<b>Areas for Improvement:</b>", styles['Normal']))
    elements.append(Paragraph(improvements_str, styles['Normal']))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("<b>Detailed Comments:</b>", styles['Normal']))
    elements.append(Paragraph(comments_str, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Download button
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("📥 Generate & Download PDF", key="download_btn"):
        # Prepare scout data
        scout_data = {
            'scout_name': scout_name if scout_name else "Anonymous Scout",
            'match_date': selected_match['date'],
            'home_team': selected_match['home_team'],
            'away_team': selected_match['away_team'],
            'home_goals': selected_match['home_goals'],
            'away_goals': selected_match['away_goals'],
            'venue': selected_match['venue'],
            'gameweek': selected_match['gameweek'],
            'player_name': selected_player['name'],
            'team': selected_player['team'],
            'position': player_position,
            'nationality': selected_player['nationality'],
            'age': selected_player['age'],
            'goals': selected_player['goals'],
            'assists': selected_player['assists'],
            'minutes': selected_player['minutes'],
            'competencies': competency_ratings,
            'overall_rating': overall_rating,
            'recommendation': recommendation,
            'strengths': strengths,
            'improvements': improvements,
            'comments': scout_comments
        }
        
        # Generate PDF
        pdf_buffer = generate_pdf(scout_data)
        
        # Download
        filename = f"Scouting_Report_{selected_player['name'].replace(' ', '_')}_{selected_match['date']}.pdf"
        st.download_button(
            label="✅ Download PDF",
            data=pdf_buffer,
            file_name=filename,
            mime="application/pdf"
        )
        
        st.success("✅ PDF generated successfully! Click the download button to save it.")

st.markdown("---")

# Summary display
if scout_name or scout_comments:
    st.subheader("📊 Report Summary")
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.write(f"**Scout:** {scout_name if scout_name else 'Not specified'}")
        st.write(f"**Player:** {selected_player['name']}")
        st.write(f"**Position:** {player_position}")
        st.write(f"**Overall Rating:** {overall_rating}/10")
    
    with summary_col2:
        st.write(f"**Recommendation:** {recommendation}")
        avg_competency = sum(competency_ratings.values()) / len(competency_ratings) if competency_ratings else 0
        st.write(f"**Avg Competency Score:** {avg_competency:.1f}/10")
        st.write(f"**Match:** {selected_match['home_team']} vs {selected_match['away_team']}")

