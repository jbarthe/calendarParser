from parser import load_data, process_leave_data
from visualizer import create_gantt_chart
import pandas as pd

try:
    print("Loading data...")
    df_raw = load_data("test_data.csv")
    df_leaves = process_leave_data(df_raw)
    
    print("Generating chart...")
    fig = create_gantt_chart(df_leaves)
    
    print("Saving to 'test_planning.pdf'...")
    fig.savefig("test_planning.pdf", format='pdf', bbox_inches='tight')
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
