import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

def create_gantt_chart(df_leaves):
    """
    Generates a Gantt chart from the processed leave data.
    df_leaves should have columns: [Name, Start, End, Label]
    Returns a Matplotlib Figure object.
    """
    if df_leaves.empty:
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.text(0.5, 0.5, "No leave data found.", ha='center', va='center')
        ax.set_axis_off()
        return fig

    # Ensure Team column exists (backwards compatibility)
    if 'Team' not in df_leaves.columns:
        df_leaves['Team'] = 'General'

    # Get unique teams in order of appearance
    teams = df_leaves['Team'].unique()
    
    # Calculate layout
    # We need a list of (y, name, team) tuples to plotting
    # We will build this starting from top (y=max) to bottom (y=0) OR
    # Just list them and then map to Y coordinates.
    # Leaving space between teams.
    
    plot_items = [] # List of dicts: {'Name': name, 'Team': team, 'Leaves': [rows]}
    
    # Group by Team and Name to handle multiple rows per person
    # But usually one person has multiple leaves in one row or multiple rows.
    # The parser produces one row per leave interval.
    # We want one Y-line per Person.
    
    for team in teams:
        team_data = df_leaves[df_leaves['Team'] == team]
        # Get unique people in this team, maintain order
        people = team_data['Name'].unique()
        
        for person in people:
            person_leaves = team_data[team_data['Name'] == person]
            plot_items.append({
                'Name': person,
                'Team': team,
                'Leaves': person_leaves
            })
        
        # Add a spacing/separator item after each team
        # We handle this by adding extra Y decrement in the loop below
    
    # Calculate Fig Height
    # Base height per person + Team headers gaps
    num_people = len(plot_items)
    num_teams = len(teams)
    # COMPACT: Significantly reduced multiplier
    # COMPACT: Adjusted multiplier for slightly larger rows
    fig_height = max(4, num_people * 0.35 + num_teams * 0.6) 
    
    fig, ax = plt.subplots(figsize=(15, fig_height))
    
    # Variables for plotting
    current_y = len(plot_items) + len(teams) # Start from top
    # COMPACT: Bar height matched to spacing (0.6 spacing -> 0.6 bar to fill)
    bar_height = 0.6
    
    # Colors
    # Colors - Light Violet / Purple palette
    colors = ['#D1C4E9', '#B39DDB', '#9575CD', '#E1BEE7', '#CE93D8'] 
    
    # Track Y positions for labels
    y_ticks = []
    y_labels = []
    
    # Track Team Y positions for separators/titles
    last_team = None
    
    # We iterate through plot_items (Person level)
    # But we need to insert Team headers.
    
    # Let's iterate by Team again to control flow better
    current_y = 0 # We'll start from 0 at top (inverted later) or just use negative?
    # Let's stick to positive Y, but we need to know max Y.
    # Easiest is to construct the list bottom-up or top-down.
    # Let's go Top-Down: Y = 0 is top line? No, Y usually increases upwards.
    # So Name 1 is at Y=Max.
    
    # Calculate min/max dates for axis limits and positioning
    min_date = df_leaves['Start'].min() - pd.DateOffset(months=1)
    max_date = df_leaves['End'].max() + pd.DateOffset(months=1)

    # Assign specific colors to people to be consistent
    all_people = df_leaves['Name'].unique()
    person_color_map = {p: colors[i % len(colors)] for i, p in enumerate(all_people)}
    
    # We detemine Y-coords
    layout = [] # (y, type, label, data)
    y_cursor = 0
    
    for team in teams[::-1]:
        team_data = df_leaves[df_leaves['Team'] == team]
        people = team_data['Name'].unique()[::-1] # Reverse people too
        
        # Add people
        for person in people:
            layout.append({'y': y_cursor, 'type': 'person', 'name': person, 'team': team})
            # COMPACT: Reduced from 1.0 to 0.6
            y_cursor += 0.6
            
        # Add Team Separator/Header space
        # Remove extra buffer for perfect stacking
        # y_cursor += 0.1 
        
        layout.append({'y': y_cursor, 'type': 'header', 'name': team, 'team': team})
        # COMPACT: 0.6 spacing for header (height 0.6)
        y_cursor += 0.6
        
    # Now Plot
    ax.set_ylim(-1, y_cursor)
    
    for item in layout:
        y = item['y']
        
        if item['type'] == 'person':
            person = item['name']
            team = item['team']
            
            # Get leaves and sort by date for overlap detection
            leaves = df_leaves[(df_leaves['Name'] == person) & (df_leaves['Team'] == team)].sort_values('Start')
            
            # Track previous label position to detect overlap
            # Heuristic: visual width of a label in 'days' units
            # A label like "22/06 - 27/06" is approx 15 chars.
            # In a year view (365 days) on 15 inches, width is roughly 20 days per inch.
            # Font size 6 is small. Let's assume a safe buffer of 25 days between centers?
            last_mid_point = -999 
            last_y_offset = 0.1 # Start slightly up? Or 0.
            
            for _, split_row in leaves.iterrows():
                start = split_row['Start']
                end = split_row['End']
                label = split_row['Label']
                duration = (end - start).days + 1
                start_num = mdates.date2num(start)
                
                mid_point = start_num + duration / 2
                
                # Check proximity
                proximity_threshold = 20 # days
                y_offset = 0
                
                if (mid_point - last_mid_point) < proximity_threshold:
                    # Overlap probable, stagger
                    # If previous was 0 or up, go down. If down, go up.
                    # Let's simple toggle between +0.15 and -0.15 relative to center
                    # Note: Row height is 0.6. Center is y. Top is y+0.3. Bottom is y-0.3.
                    # Text usually centered at y.
                    # y+0.15 is halfway top. y-0.15 is halfway bottom.
                    
                    if last_y_offset > 0:
                        y_offset = -0.15
                    else:
                        y_offset = 0.15
                else:
                    # Reset to center if no overlap
                    y_offset = 0
                
                last_mid_point = mid_point
                last_y_offset = y_offset
                
                # Bar
                ax.broken_barh([(start_num, duration)], (y - bar_height/2, bar_height),
                               facecolors=person_color_map[person], edgecolor='none')
                
                # Label inside the bar with offset
                ax.text(mid_point, y + y_offset, label,
                        ha='center', va='center', fontsize=6, color='black')
            
            # Y-Label for Person
            # We add it manually or use yticks
            y_ticks.append(y)
            y_labels.append(f"{person}")
            
            # Add separator line BELOW this person (at y - 0.3 since spacing is 0.6)
            # Actually since we build bottom up or top down, let's just draw a line between rows.
            # Grid lines?
            # User asked for "lignes pour bien distinguer chaque personnes"
            # We can draw a thin light line at y - 0.3 (halfway to next)
            ax.axhline(y=y - 0.3, color='#eeeeee', linestyle='-', linewidth=0.5)
            
        elif item['type'] == 'header':
            # Draw Team Title with colored background
            # Define band limits
            # Axis limits are numbers.
            xmin, xmax = mdates.date2num(min_date), mdates.date2num(max_date)
            
            # Band height
            h_band = 0.6
            y_bottom = y - h_band / 2
            y_top = y + h_band / 2
            
            # Draw background rectangle
            rect = plt.Rectangle((xmin, y_bottom), xmax - xmin, h_band, 
                               facecolor='#E8E6F0', edgecolor='none', zorder=0)
            ax.add_patch(rect)
            
            # Draw borders top and bottom
            ax.axhline(y=y_bottom, xmin=0, xmax=1, color='black', linewidth=1.0)
            ax.axhline(y=y_top, xmin=0, xmax=1, color='black', linewidth=1.0)
            
            # Draw Text
            # Indent slightly from the left edge
            text_x = xmin + (xmax - xmin) * 0.02 # 2% padding
            ax.text(text_x, y, item['name'], ha='left', va='center', 
                    fontsize=10, fontweight='bold', color='#333344', zorder=1)

    # Y-Axis Settings
    ax.set_yticks(y_ticks)
    # Improved visibility for names: Bold, Darker, Larger
    ax.set_yticklabels(y_labels, fontsize=9, fontweight='bold', color='#2D2D3A')
    ax.tick_params(axis='y', length=0) # Hide tick marks
    
    # X-Axis limits
    ax.set_xlim(mdates.date2num(min_date), mdates.date2num(max_date))
    
    # Major ticks: Months
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    
    # Grid
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    
    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Show left spine to act as separator for names
    ax.spines['left'].set_visible(True) 
    ax.spines['left'].set_linewidth(1.0)
    ax.spines['left'].set_color('black')
    
    # Title
    current_year = min_date.year
    next_year = max_date.year
    ax.set_title(f"Calendrier des Congés {current_year} - {next_year}", pad=20)
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Test stub
    data = [
        {"Name": "BIDULE", "Start": pd.Timestamp("2025-06-22"), "End": pd.Timestamp("2025-07-27"), "Label": "22/06 - 27/06"},
        {"Name": "TARTEMPION", "Start": pd.Timestamp("2025-05-14"), "End": pd.Timestamp("2025-05-17"), "Label": "14/05 - 17/05"}
    ]
    df_test = pd.DataFrame(data)
    fig = create_gantt_chart(df_test)
    fig.savefig("test_output.pdf")
    print("Test chart saved to test_output.pdf")
