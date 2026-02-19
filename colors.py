import numpy as np

# Material Design Palettes (50 to 900)
COLOR_PALETTES = [
    # Blue
    ['#E3F2FD', '#BBDEFB', '#90CAF9', '#64B5F6', '#42A5F5', '#2196F3', '#1E88E5', '#1976D2', '#1565C0', '#0D47A1'],
    # Red
    ['#FFEBEE', '#FFCDD2', '#EF9A9A', '#E57373', '#EF5350', '#F44336', '#E53935', '#D32F2F', '#C62828', '#B71C1C'],
    # Green
    ['#E8F5E9', '#C8E6C9', '#A5D6A7', '#81C784', '#66BB6A', '#4CAF50', '#43A047', '#388E3C', '#2E7D32', '#1B5E20'],
    # Orange
    ['#FFF3E0', '#FFE0B2', '#FFCC80', '#FFB74D', '#FFA726', '#FF9800', '#FB8C00', '#F57C00', '#EF6C00', '#E65100'],
    # Purple
    ['#F3E5F5', '#E1BEE7', '#CE93D8', '#BA68C8', '#AB47BC', '#9C27B0', '#8E24AA', '#7B1FA2', '#6A1B9A', '#4A148C'],
    # Teal
    ['#E0F2F1', '#B2DFDB', '#80CBC4', '#4DB6AC', '#26A69A', '#009688', '#00897B', '#00796B', '#00695C', '#004D40'],
    # Indigo
    ['#E8EAF6', '#C5CAE9', '#9FA8DA', '#7986CB', '#5C6BC0', '#3F51B5', '#3949AB', '#303F9F', '#283593', '#1A237E'],
    # Amber
    ['#FFF8E1', '#FFECB3', '#FFE082', '#FFD54F', '#FFCA28', '#FFC107', '#FFB300', '#FFA000', '#FF8F00', '#FF6F00'],
    # Pink
    ['#FCE4EC', '#F8BBD0', '#F48FB1', '#F06292', '#EC407A', '#E91E63', '#D81B60', '#C2185B', '#AD1457', '#880E4F'],
    # Cyan
    ['#E0F7FA', '#B2EBF2', '#80DEEA', '#4DD0E1', '#26C6DA', '#00BCD4', '#00ACC1', '#0097A7', '#00838F', '#006064'],
    # Brown
    ['#EFEBE9', '#D7CCC8', '#BCAAA4', '#A1887F', '#8D6E63', '#795548', '#6D4C41', '#5D4037', '#4E342E', '#3E2723'],
    # Blue Grey
    ['#ECEFF1', '#CFD8DC', '#B0BEC5', '#90A4AE', '#78909C', '#607D8B', '#546E7A', '#455A64', '#37474F', '#263238']
]

def assign_colors(df_leaves):
    """
    Assigns colors to people and teams.
    Returns (person_color_map, team_color_map)
    
    Logic:
    - Teams cycle through different palettes.
    - Team Header gets a light shade (index 1 or 2).
    - People get a gradient from index 3 to 8 (Mid to Dark).
    """
    person_color_map = {}
    team_color_map = {}
    
    # Get Teams
    if 'Team' not in df_leaves.columns:
         people = df_leaves['Name'].unique()
         palette = COLOR_PALETTES[0]
         indices = np.linspace(2, 8, len(people), dtype=int)
         for i, person in enumerate(people):
             # Default to 'General' team if no team column
             person_color_map[(person, 'General')] = palette[indices[i]]
         
         team_color_map['General'] = palette[1]
         return person_color_map, team_color_map

    teams = df_leaves['Team'].unique()
    
    for team_idx, team in enumerate(teams):
        # Pick palette for this team (cycle if needed)
        palette = COLOR_PALETTES[team_idx % len(COLOR_PALETTES)]
        
        # Assign Team Header Color (Light shade for background)
        team_color_map[team] = palette[1] # Index 1 is usually 100 (Light but visible)
        
        # Get people in this team
        team_people = df_leaves[df_leaves['Team'] == team]['Name'].unique()
        num_people = len(team_people)
        
        if num_people == 0:
            continue
            
        # Distribute shades for people
        # Use range 3 (300) to 8 (800) for good visibility and contrast against white
        # If only 1 person, pick middle (5)
        
        if num_people == 1:
            indices = [5]
        else:
            # Linear space from 3 to 8
            indices = np.linspace(3, 8, num_people, dtype=int)
            
        for i, person in enumerate(team_people):
            color_idx = indices[i]
            # Key by (Name, Team) tuple to handle same person in multiple teams
            person_color_map[(person, team)] = palette[color_idx]
            
    return person_color_map, team_color_map
