import pandas as pd
import re
import io
import requests

def parse_date_range(text):
    """
    Extracts start and end dates from a string like "Du 14/05/25 au 17/05/25".
    Handles "inclus" and extra text.
    Returns a tuple (start_date, end_date) as datetime objects, or None if not found.
    """
    if not isinstance(text, str):
        return None
    
    # Normalize text
    text_clean = text.lower().replace("\n", " ")
    
    # Remove everything after "inclus" if present, but "inclus" might be just before extra notes.
    # Actually, the user wants to ignore "à partir de inclus". 
    # Let's just focus on extracting the dates robustly.
    # The pattern is usually "du DD/MM/YY au DD/MM/YY"
    
    pattern = r"du\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+au\s+(\d{1,2}/\d{1,2}/\d{2,4})"
    match = re.search(pattern, text_clean)
    
    if match:
        start_str = match.group(1)
        end_str = match.group(2)
        
        try:
            # Parse dates with dayfirst=True to handle dd/mm formats correctly
            start_date = pd.to_datetime(start_str, dayfirst=True)
            end_date = pd.to_datetime(end_str, dayfirst=True)
            return start_date, end_date
        except Exception as e:
            # print(f"Error parsing dates: {e}")
            return None
    return None

def parse_extra_days(text):
    """
    Extracts extra single days from text patterns like:
    - (+2 JS : 24 et 25/02/26)
    - (+1 JS : 28/02/26)
    - (+2 JS :30/04 et 02/05/26)
    
    Returns a list of datetime objects.
    """
    if not isinstance(text, str):
        return []

    # Regex to find the content inside (+... JS : ...)
    # Case insensitive
    pattern = r"\(\+\d+\s*JS\s*:\s*(.*?)\)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    extra_dates = []
    
    for content in matches:
        # Content could be "24 et 25/02/26" or "30/04 et 02/05/26"
        # Split by ' et ' or ','
        # Normalize spaces
        content = content.replace(" et ", ",").replace(" ET ", ",")
        parts = [p.strip() for p in content.split(",")]
        
        # We need to process parts in reverse to propagate Year and Month if missing
        # Example: "24", "25/02/26" -> 24 implies /02/26
        
        parsed_parts = []
        last_date = None # To hold reference for missing year/month
        
        for part in reversed(parts):
            # Check format
            # DD/MM/YY(YY)
            d_match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", part)
            if d_match:
                d, m, y = d_match.groups()
                # Fix partial year
                if len(y) == 2:
                    y = "20" + y
                
                try:
                    dt = pd.Timestamp(year=int(y), month=int(m), day=int(d))
                    parsed_parts.append(dt)
                    last_date = dt
                except:
                    pass
                continue
                
            # DD/MM
            dm_match = re.search(r"(\d{1,2})/(\d{1,2})", part)
            if dm_match:
                d, m = dm_match.groups()
                y = last_date.year if last_date else pd.Timestamp.now().year # Fallback or inferred
                try:
                    dt = pd.Timestamp(year=y, month=int(m), day=int(d))
                    parsed_parts.append(dt)
                    last_date = dt # Update last date (though usually year doesn't change backwards often here)
                except:
                    pass
                continue
                
            # Just DD
            dd_match = re.search(r"^(\d{1,2})$", part)
            if dd_match:
                d = dd_match.group(1)
                if last_date:
                    try:
                        dt = pd.Timestamp(year=last_date.year, month=last_date.month, day=int(d))
                        parsed_parts.append(dt)
                    except:
                        pass
                continue

        extra_dates.extend(parsed_parts)
    
    return extra_dates

def load_data(source):
    """
    Loads data from a CSV file, Excel file, or Google Sheet URL.
    Returns a pandas DataFrame.
    """
    if isinstance(source, str) and source.startswith("http"):
        # Assume it's a Google Sheet URL
        # Convert /edit URL to /export format for CSV
        if "/edit" in source:
            base_url = source.split("/edit")[0]
            # Check if gid is present anywhere
            gid = "0"
            gid_match = re.search(r"[#&?]gid=(\d+)", source)
            if gid_match:
                gid = gid_match.group(1)
            
            source = f"{base_url}/gviz/tq?tqx=out:csv&gid={gid}"
            
        elif "/pub" in source:
             # User provided a "Published to web" link, use as is but ensure csv format if possible
             pass

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(source, headers=headers)
        response.raise_for_status()
        
        # Check if we got a login page (HTML) instead of CSV
        if "text/html" in response.headers.get("Content-Type", ""):
             raise ValueError("Google Sheets a demandé une connexion. Veuillez utiliser 'Fichier > Partager > Publier sur le web' et choisir le format CSV.") 

        df = pd.read_csv(io.StringIO(response.text))
    elif hasattr(source, "name"):
         # Streamlit UploadedFile object
        if source.name.endswith(".csv"):
            # Try to read with default, then fallback
            try:
                source.seek(0)
                df = pd.read_csv(source)
            except UnicodeDecodeError:
                source.seek(0)
                try:
                    df = pd.read_csv(source, encoding='latin1')
                except UnicodeDecodeError:
                    source.seek(0)
                    df = pd.read_csv(source, encoding='cp1252')
        elif source.name.endswith(".xlsx"):
            df = pd.read_excel(source)
        else:
             raise ValueError("Unsupported file format")
    else:
        # Local file path or other
        if source.endswith(".csv"):
            try:
                df = pd.read_csv(source)
            except UnicodeDecodeError:
                 try:
                     df = pd.read_csv(source, encoding='latin1')
                 except UnicodeDecodeError:
                     df = pd.read_csv(source, encoding='cp1252')
        elif source.endswith(".xlsx"):
             df = pd.read_excel(source)
        else:
             raise ValueError("Unsupported file format")
             
    return df

def process_leave_data(df):
    """
    Process the raw DataFrame to extract leave intervals.
    Returns a DataFrame with columns: [Name, Team, Start, End, Label]
    """
    leaves = []
    current_team = "General"
    
    # Iterate through rows
    for index, row in df.iterrows():
        # Clean col 0
        col0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        
        # Check if this row is a Team Header
        # Heuristic: Col 0 has text, AND ALL other columns are empty.
        # This prevents a person who has no leave in Period 1 but has leave in Period 2 from being seen as a Team.
        
        is_row_content_empty = True
        for col_idx in range(1, len(row)):
            val = str(row.iloc[col_idx]).strip() if pd.notna(row.iloc[col_idx]) else ""
            if val:
                is_row_content_empty = False
                break
        
        if col0 and is_row_content_empty:
             # Likely a header or empty filler
             # Check if it looks like a team name (uppercase, or just assume it is if not empty)
             # Also ignore some metadata rows like "Période de référence..." or empty instructions
             if "Période" in col0 or "CONGES" in col0 or "FORMULAIRE" in col0 or "Instructions" in col0:
                 continue
             current_team = col0
             continue
             
        if not col0:
            continue
            
        # It's an employee row
        person_name = col0.split("\n")[0].strip() # Take first line of name (remove "(23 jours...)")
        
        # Iterating columns for dates
        for col_idx in range(1, len(row)):
            cell_value = row.iloc[col_idx]
            dates = parse_date_range(cell_value)
            
            if dates:
                start, end = dates
                # Create label: "DD/MM - DD/MM"
                label = f"{start.strftime('%d/%m')} - {end.strftime('%d/%m')}"
                
                leaves.append({
                    "Name": person_name,
                    "Team": current_team,
                    "Start": start,
                    "End": end,
                    "Label": label
                })

            # Check for extra days (JS)
            extra_days = parse_extra_days(cell_value)
            for js_date in extra_days:
                leaves.append({
                    "Name": person_name,
                    "Team": current_team,
                    "Start": js_date,
                    "End": js_date,
                    "Label": "JS" # Label for visualizer
                })
                
    df = pd.DataFrame(leaves)
    if df.empty:
        return df

    # Logic to merge consecutive JS days
    # Separate JS and non-JS
    df_js = df[df['Label'] == 'JS'].copy()
    df_other = df[df['Label'] != 'JS'].copy()

    if df_js.empty:
        return df

    # Sort JS to ensure order
    df_js['Start'] = pd.to_datetime(df_js['Start'])
    df_js['End'] = pd.to_datetime(df_js['End'])
    df_js = df_js.sort_values(by=['Name', 'Team', 'Start'])

    merged_js = []
    
    # Group by Name and Team to merge consecutive days
    # We use groupby to handle each person separately
    for (name, team), group in df_js.groupby(['Name', 'Team']):
        group = group.sort_values('Start')
        
        current_block = None
        
        for _, row in group.iterrows():
            if current_block is None:
                current_block = row.to_dict()
                current_block['Count'] = 1
                continue
            
            # Check continuity
            # If row['Start'] == current_block['End'] + 1 day
            if row['Start'] == current_block['End'] + pd.Timedelta(days=1):
                current_block['End'] = row['End']
                current_block['Count'] += 1
            else:
                # Push current and start new
                merged_js.append(current_block)
                current_block = row.to_dict()
                current_block['Count'] = 1
        
        if current_block:
            merged_js.append(current_block)

    if not merged_js:
        return df_other

    # Convert merged list back to DF
    df_merged_js = pd.DataFrame(merged_js)
    # Update Label based on Count
    df_merged_js['Label'] = df_merged_js['Count'].apply(lambda x: f"{x} JS" if x > 1 else "JS")
    
    # cleanup count
    if 'Count' in df_merged_js.columns:
        df_merged_js = df_merged_js.drop(columns=['Count'])

    return pd.concat([df_other, df_merged_js], ignore_index=True)

if __name__ == "__main__":
    # Test with local file
    test_file = "new_data.csv"
    try:
        # Load csv directly to avoid header confusion using 'header=None' might be safer 
        # but let's stick to default load_data for consistency, or adjust load_data
        # Actually load_data uses pd.read_csv which assumes first row is header.
        # For this file, header is row 1 (garbage). Data starts later.
        # We should probably treat all as strings.
        
        # Overriding load for this test to match what load_data does but ensuring string type
        df_raw = pd.read_csv(test_file, header=None, dtype=str)
        
        print("Raw Data Loaded")
        print(df_raw.iloc[5:10]) # Show some team section
        
        df_leaves = process_leave_data(df_raw)
        print("\nProcessed Leaves:")
        print(df_leaves.head(10))
        print(df_leaves['Team'].unique())
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
