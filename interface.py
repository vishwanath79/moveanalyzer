import gradio as gr
from typing import Dict, Any
from main import ChessComAnalyzer, analyze_with_llm
import datetime
import os
import base64

# Read and encode the chess.png image
def get_chess_logo():
    with open("chess.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"

LOGO_BASE64 = get_chess_logo()

def format_results_as_html(results):
    """Format results as an HTML table with bulleted analysis"""
    html = """
    <div style="margin: 20px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;">
        <table style="width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <thead>
                <tr style="background-color: var(--primary-500);">
                    <th style="padding: 12px; text-align: left; color: white; font-weight: 600; font-size: 15px;">Date</th>
                    <th style="padding: 12px; text-align: left; color: white; font-weight: 600; font-size: 15px;">White Player</th>
                    <th style="padding: 12px; text-align: left; color: white; font-weight: 600; font-size: 15px;">Black Player</th>
                    <th style="padding: 12px; text-align: left; color: white; font-weight: 600; font-size: 15px;">Result</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for game in results:
        # Format analysis with proper indentation and spacing
        formatted_analysis = game['analysis']
        # Replace bullet points with styled ones
        formatted_analysis = formatted_analysis.replace('• ', '<br><span style="color: var(--primary-500);">•</span> ')
        # Format sub-bullets with proper indentation
        formatted_analysis = formatted_analysis.replace('  - ', '<br>&nbsp;&nbsp;&nbsp;<span style="color: var(--primary-600);">-</span> ')
        # Format move numbers and notations
        formatted_analysis = formatted_analysis.replace('[Move ', '<span style="font-family: monospace; background: var(--background-fill-secondary); padding: 2px 4px; border-radius: 3px;">Move ')
        formatted_analysis = formatted_analysis.replace(']', '</span>')
        # Format model attribution
        formatted_analysis = formatted_analysis.replace('Analysis by:', '<br><br><em>Analysis by:</em>')
        
        html += f"""
            <tr style="background-color: var(--background-fill-primary);">
                <td style="padding: 12px; border-bottom: 1px solid var(--border-color-primary); font-size: 14px;">{game['date']}</td>
                <td style="padding: 12px; border-bottom: 1px solid var(--border-color-primary); font-size: 14px;">{game['white_player']}</td>
                <td style="padding: 12px; border-bottom: 1px solid var(--border-color-primary); font-size: 14px;">{game['black_player']}</td>
                <td style="padding: 12px; border-bottom: 1px solid var(--border-color-primary); font-size: 14px;">{game['result']}</td>
            </tr>
            <tr>
                <td colspan="4" style="padding: 16px; background-color: var(--background-fill-secondary); line-height: 1.8; font-size: 14px;">
                    <div style="margin-left: 12px; white-space: pre-line;">
                        {formatted_analysis}
                    </div>
                </td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    return html

custom_css = """
.header-row {
    align-items: center !important;
    padding: 2rem !important;
}

.header-row img {
    object-fit: contain !important;
    margin-right: 2rem !important;
    display: block !important;
}

.instruction-text {
    margin: 1rem 0 !important;
    color: var(--body-text-color) !important;
    font-size: 1.1rem !important;
    text-align: left !important;
}
"""

# Create the Gradio interface with Applio theme
with gr.Blocks(theme='Hev832/Applio', css=custom_css) as app:
    # Header with logo and title
    with gr.Row(elem_classes="header-row"):
        with gr.Column(scale=1):
            gr.HTML(f'<img src="{LOGO_BASE64}" style="height: 160px; width: 160px; object-fit: contain;">')
        with gr.Column(scale=4):
            gr.Markdown("# Move Analyzer")
        with gr.Column(scale=1):
            # center the button 
            gr.HTML('<a href="https://github.com/vishwanath79/moveanalyzer" target="_blank" style="text-decoration: none;"><button class="gr-button gr-button-primary">About</button></a>')
    
    # Search section
    with gr.Column():
        gr.Markdown("### Enter your chess.com username to analyze your games", elem_classes=["instruction-text"])
        with gr.Row():
            player_name = gr.Textbox(
                label="Player Name", 
                placeholder="Enter player name...",
                scale=2
            )
            result = gr.Dropdown(
                choices=["All", "Today", "Last 7 days", "Last 30 days", "win", "resigned", "timeout", "abandoned"], 
                label="Filter",
                value="All",
                scale=1,
                container=True,
                interactive=True
            )
        # Add loading text and progress indicator
        with gr.Row():
            search_btn = gr.Button("Show Results", variant="primary", interactive=True)
            loading = gr.HTML(visible=False, value='<div style="display: flex; align-items: center; gap: 10px;"><span class="loading"></span><span>Analyzing games...</span></div>')

    # Status and results
    status = gr.Markdown("")
    with gr.Row():
        results = gr.HTML()

    # Add CSS for loading animation
    custom_css = custom_css + """
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-top-color: var(--primary-500);
        animation: spin 1s ease-in-out infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    """

    def analyze_and_format(player_name: str, filter_value: str) -> tuple:
        """Analyze games and format results"""
        try:
            if not player_name:
                return "Please enter a player name", ""
            
            status_msg = "Analyzing games..."
            
            analyzer = ChessComAnalyzer(player_name)
            games_data = analyzer.get_all_games()
            
            # Debug print to see what we're getting from the API
            print("Games data:", games_data)
            
            if isinstance(games_data, dict) and "error" in games_data:
                return f"Error: {games_data['error']}", ""
            
            if not games_data:  # If games_data is empty list
                return "No games found for this player", ""
            
            # Get current date for filtering
            current_date = datetime.datetime.now().date()
            
            formatted_games = []
            for game_data in games_data:
                try:
                    game_date = datetime.datetime.fromtimestamp(game_data['end_time']).date()
                    
                    # Apply filters
                    if filter_value == "Today" and game_date != current_date:
                        continue
                    elif filter_value == "Last 7 days" and (current_date - game_date).days > 7:
                        continue
                    elif filter_value == "Last 30 days" and (current_date - game_date).days > 30:
                        continue
                    elif filter_value not in ["All", "Today", "Last 7 days", "Last 30 days"] and game_data['result'] != filter_value:
                        continue
                    
                    # Debug print for analysis
                    print(f"Analyzing game from {game_date}")
                    analysis = analyze_with_llm(game_data)
                    
                    formatted_game = {
                        'date': datetime.datetime.fromtimestamp(game_data['end_time']).strftime('%Y-%m-%d %H:%M:%S'),
                        'white_player': game_data['white_player'],
                        'black_player': game_data['black_player'],
                        'result': game_data['result'],
                        'analysis': analysis
                    }
                    formatted_games.append(formatted_game)
                    
                    # sort by date in descending order
                    formatted_games.sort(key=lambda x: x['date'], reverse=True)
                except Exception as e:
                    print(f"Error processing game: {str(e)}")
                    continue
            
            if not formatted_games:
                return f"No games found matching the filter: {filter_value}", ""
            
            # Debug print for results
            print(f"Found {len(formatted_games)} games")
            return "", format_results_as_html(formatted_games)
            
        except Exception as e:
            print(f"Error in analyze_and_format: {str(e)}")
            return f"Error: {str(e)}", ""
    
    def analyze_with_loading(player_name: str, filter_value: str):
        """Wrapper function to handle loading state"""
        try:
            # Show loading state
            yield True, "", ""  # loading visible, clear status and results
            
            # Get analysis results
            status_msg, results_html = analyze_and_format(player_name, filter_value)
            
            # Hide loading and show results
            yield False, status_msg, results_html
            
        except Exception as e:
            # Hide loading and show error
            yield False, f"Error: {str(e)}", ""

    # Update event handlers
    search_btn.click(
        fn=analyze_with_loading,
        inputs=[player_name, result],
        outputs=[loading, status, results],
        api_name="analyze"
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.launch(server_name="0.0.0.0", server_port=port, share=True) 