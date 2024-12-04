import streamlit as st
import requests
import pandas as pd

# Base URL
BASE_URL = "https://iq-api-bg.fastmodelsports.com/v2/generate"

# Streamlit app title
st.title("Analysis: GPT-4o vs GPT-4o-mini")

# Input for authentication token
auth_token = st.text_input("Enter Authentication Token", type="password", value="")

# Toggle for Team or Player
analysis_type = st.radio("Select Analysis Type", options=["Team", "Player"])

# Input format instructions
if analysis_type == "Team":
    st.markdown("""
    ### Input Format
    Enter a list of team IDs and their corresponding leagues in the following format:
    ```
    [
        ["team_id_1", "NBA"],
        ["team_id_2", "WNBA"]
    ]
    ```
    """)
else:
    st.markdown("""
    ### Input Format
    Enter a list of player IDs and their corresponding leagues in the following format:
    ```
    [
        ["player_id_1", "NBA"],
        ["player_id_2", "WNBA"]
    ]
    ```
    """)

# Input field for IDs and leagues
input_data = st.text_area(f"Enter {analysis_type} IDs and League List", height=200)

# Parse input
try:
    id_league_list = eval(input_data)  # Parse input safely
    if not isinstance(id_league_list, list) or not all(isinstance(item, list) and len(item) == 2 for item in id_league_list):
        raise ValueError
except:
    id_league_list = []
    st.error("Invalid format. Please ensure the input is a list of lists as described.")

# Button to trigger API calls
if st.button("Compare Models"):
    if not auth_token:
        st.error("Please provide a valid authentication token.")
    elif not id_league_list:
        st.warning(f"Please provide a valid list of {analysis_type.lower()} IDs and leagues.")
    else:
        # Create a split layout for side-by-side comparisons
        col1, col2 = st.columns(2)

        # Initialize a list to collect results
        results_data = []

        for entity_id, league in id_league_list:
            # Common parameters
            params = {
                "season": "24",
                "emojis": "false",
                "mocked_response": "false",
                "html": "true",
                "prompt_id": "PROMPT_1",
                "response_type": "html",
                "external_stats": "true",
                analysis_type.lower(): entity_id,  # Use 'team' or 'player' dynamically
                "league": league
            }

            headers = {
                "Authorization": f"Bearer {auth_token}"
            }

            # Fetch data for both models
            results = {}
            for model in ["gpt-4o", "gpt-4o-mini"]:
                params["model"] = model
                try:
                    response = requests.get(BASE_URL, headers=headers, params=params)
                    if response.status_code == 200:
                        results[model] = response.text
                    else:
                        results[model] = f"Error: {response.status_code} - {response.reason}"
                except Exception as e:
                    results[model] = f"Error: {str(e)}"

            # Add results to the list
            results_data.append({
                "id": entity_id,
                "league": league,
                "gpt4": results.get("gpt-4o", "No data"),
                "mini": results.get("gpt-4o-mini", "No data")
            })

            # Display results side-by-side
            with col1:
                st.subheader(f"{league} - {entity_id} (GPT-4o)")
                st.markdown(results.get("gpt-4o", "No data"), unsafe_allow_html=True)

            with col2:
                st.subheader(f"{league} - {entity_id} (GPT-4o-mini)")
                st.markdown(results.get("gpt-4o-mini", "No data"), unsafe_allow_html=True)

        # Convert the list of results to a DataFrame
        results_df = pd.DataFrame(results_data)

        # Display the DataFrame
        st.markdown("### Results DataFrame")
        st.dataframe(results_df)

        # Provide download option for the DataFrame
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name=f"{analysis_type.lower()}_analysis_results.csv",
            mime="text/csv"
        )
