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
    
    # Variables for plotting
    current_y = len(plot_items) + len(teams) # Start from top
    # COMPACT: Bar height matched to spacing (0.6 spacing -> 0.6 bar to fill)
    bar_height = 0.6
    
    # Colors logic moved to colors.py 
    
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
    # Colors
    from colors import assign_colors
    person_color_map, team_color_map = assign_colors(df_leaves)
    
    # Calculate min/max dates for axis limits and positioning
    min_date = df_leaves['Start'].min() - pd.DateOffset(months=1)
    max_date = df_leaves['End'].max() + pd.DateOffset(months=1)
    
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
        
    # Calculate Pagination
    # A3 Landscape is approx 11.7 inches high.
    # Margins take ~2 inches. Usable ~9.7 inches.
    # Title / Axis takes ~2 inches. Usable ~7-8 inches for data.
    # Row height is 0.6.
    # Approx 12-13 rows per page (people + headers) safely.
    
    # We need to chunk plot_items (which are per person) but respect Team headers.
    # Or simpler: Just iterate through layout items and break when Y exceeds limit?
    # but we are building Bottom-Up or Top-Down?
    # Current logic:
    # We built `layout` list with Y coords. Y increases upwards?
    # No, we set `ax.set_ylim(-1, y_cursor)`. So Y starts at 0 and goes up.
    # If we have 100 people, Y goes to 60.
    
    # We should chunk the `layout` list.
    # Each page will show a slice of Y range?
    # Or better: Create separate figures for chunks of people.
    
    # Let's chunk the data first.
    max_rows_per_page = 15 # Conservative for A3
    
    # Break layout items into pages
    pages = []
    current_page_items = []
    rows_on_page = 0
    
    for item in layout:
         current_page_items.append(item)
         if item['type'] in ['person', 'header']:
             rows_on_page += 1
         
         if rows_on_page >= max_rows_per_page:
             # Check if we are in the middle of a team?
             # Ideally don't break a team if small, but if large we must.
             # Just break for now.
             pages.append(current_page_items)
             current_page_items = []
             rows_on_page = 0
             
    if current_page_items:
        pages.append(current_page_items)
        
    # Reverse pages to have the "Top" of the chart (Last teams added) as the first page
    pages.reverse()
        
    figures = []
    
    for i, page_items in enumerate(pages):
        # Calculate height for this page
        # Note: We need to re-calculate Y coordinates for this page to start from 0?
        # Or just adjust limits?
        # Easier to Re-Calculate Y for clarity
        
        page_y_cursor = 0
        page_layout = []
        
        for item in page_items:
             # Deep copy to not modify original if needed, but here we just process
             # Just create new dict
             new_item = item.copy()
             new_item['y'] = page_y_cursor
             page_layout.append(new_item)
             
             if item['type'] == 'person':
                 page_y_cursor += 0.6
             elif item['type'] == 'header':
                 # Separation logic
                 # If header is first item on page, maybe don't add extra top spacing?
                 # Current logic was:
                 # y_cursor += 0.6 (spaced from previous)
                 # Here we just stack them.
                 page_y_cursor += 0.6
        
        # Fixed A3 Size: 16.5 x 11.7 inches
        # We can stick to dynamic height or force A3?
        # User asked for A3.
        fig_height = 11.7
        fig_width = 16.5
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Plotting Logic (Same as before but using page_layout)
        ax.set_ylim(-1, max(page_y_cursor, 5)) # Min height to avoid error
        
        y_ticks = []
        y_labels = []

        for item in page_layout:
            y = item['y']
            
            if item['type'] == 'person':
                person = item['name']
                team = item['team']
                
                # Get leaves
                leaves = df_leaves[(df_leaves['Name'] == person) & (df_leaves['Team'] == team)].sort_values('Start')
                
                # ... [Insert Overlap Logic Here] ...
                # To keep code simple, I will reuse the overlap logic block
                
                last_mid_point = -999 
                last_y_offset = 0.1
                
                for _, split_row in leaves.iterrows():
                    start = split_row['Start']
                    end = split_row['End']
                    label = split_row['Label']
                    duration = (end - start).days + 1
                    start_num = mdates.date2num(start)
                    mid_point = start_num + duration / 2
                    
                    proximity_threshold = 20
                    y_offset = 0
                    if (mid_point - last_mid_point) < proximity_threshold:
                        if last_y_offset > 0: y_offset = -0.15
                        else: y_offset = 0.15
                    else:
                        y_offset = 0
                    
                    last_mid_point = mid_point
                    last_y_offset = y_offset
                    
                    ax.broken_barh([(start_num, duration)], (y - bar_height/2, bar_height),
                                   facecolors=person_color_map.get((person, team), '#cccccc'), edgecolor='none')
                    ax.text(mid_point, y + y_offset, label,
                            ha='center', va='center', fontsize=6, color='black')
                
                y_ticks.append(y)
                y_labels.append(f"{person}")
                ax.axhline(y=y - 0.3, color='#eeeeee', linestyle='-', linewidth=0.5)
                
            elif item['type'] == 'header':
                xmin, xmax = mdates.date2num(min_date), mdates.date2num(max_date)
                h_band = 0.6
                y_bottom = y - h_band / 2
                y_top = y + h_band / 2
                
                rect = plt.Rectangle((xmin, y_bottom), xmax - xmin, h_band, 
                                   facecolor=team_color_map.get(item['name'], '#E8E6F0'), edgecolor='none', zorder=0)
                ax.add_patch(rect)
                ax.axhline(y=y_bottom, xmin=0, xmax=1, color='black', linewidth=1.0)
                ax.axhline(y=y_top, xmin=0, xmax=1, color='black', linewidth=1.0)
                
                text_x = xmin + (xmax - xmin) * 0.02
                ax.text(text_x, y, item['name'], ha='left', va='center', 
                        fontsize=10, fontweight='bold', color='#333344', zorder=1)

        # Axis Settings
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels, fontsize=9, fontweight='bold', color='#2D2D3A')
        ax.tick_params(axis='y', length=0)
        ax.set_xlim(mdates.date2num(min_date), mdates.date2num(max_date))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.grid(True, axis='x', linestyle='--', alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(True) 
        ax.spines['left'].set_linewidth(1.0)
        ax.spines['left'].set_color('black')
        
        # Title with Page Number
        current_year = min_date.year
        next_year = max_date.year
        page_str = f" - Page {i+1}/{len(pages)}" if len(pages) > 1 else ""
        ax.set_title(f"Calendrier des Congés {current_year} - {next_year}{page_str}", pad=20)
        
        plt.tight_layout()
        figures.append(fig)
        
    return figures

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
