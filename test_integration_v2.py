from parser import load_data, process_leave_data
from visualizer import create_gantt_chart
import pandas as pd

try:
    print("Loading data...")
    # Using the manually downloaded csv to avoid requests logic and focus on logic
    # But using load_data ensures full pipeline
    # We will override load_data to use local file for "test_url" simulation if needed
    # But here we just point to new_data.csv
    
    # Note: parser.py load_data might fail on new_data.csv if it expects specific format? 
    # No, load_data just reads CSV.
    # We need to ensure we read it as strings though (header=1 logic?)
    
    # Let's bypass load_data for this test to exactly control the DF input as parser expects
    df_raw = pd.read_csv("test_data_js.csv", header=None, dtype=str)
    
    print("Processing...")
    df_leaves = process_leave_data(df_raw)
    print(f"Extracted {len(df_leaves)} leaves.")
    print(df_leaves.head())
    
    print("Generating chart...")
    fig = create_gantt_chart(df_leaves)
    
    print("Saving to 'test_planning_v2.pdf'...")
    fig.savefig("test_planning_v2.pdf", format='pdf', bbox_inches='tight')
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
