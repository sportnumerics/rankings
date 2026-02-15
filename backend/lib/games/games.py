import os
import json
import logging
from datetime import datetime
from collections import defaultdict

LOGGER = logging.getLogger(__name__)


def generate_games_file(args):
    """Generate a consolidated games.json from all schedule files."""
    year = args.year
    input_dir = args.input_dir
    
    schedules_dir = os.path.join(input_dir, year, 'schedules')
    output_file = os.path.join(input_dir, year, 'games.json')
    
    if not os.path.exists(schedules_dir):
        LOGGER.warning(f"Schedules directory not found: {schedules_dir}")
        return
    
    # Collect all games organized by date
    games_by_date = defaultdict(list)
    
    for filename in os.listdir(schedules_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(schedules_dir, filename)
        with open(filepath, 'r') as f:
            schedule = json.load(f)
        
        team = schedule['team']
        for game in schedule.get('games', []):
            date = game['date']
            opponent = game['opponent']
            
            # Only add if this team is home (to avoid duplicates)
            # Away games will be captured when we process the home team's schedule
            if game.get('home'):
                game_entry = {
                    'date': date,
                    'homeTeam': team['name'],
                    'homeTeamId': team['id'],
                    'awayTeam': opponent['name'],
                    'awayTeamId': opponent['id'],
                    'homeDiv': team.get('div'),
                    'sport': team.get('sport'),
                    'source': team.get('source'),
                }
                
                # Add result if available
                if 'result' in game:
                    game_entry['result'] = game['result']
                
                games_by_date[date].append(game_entry)
    
    # Sort games within each date by home team name
    for date in games_by_date:
        games_by_date[date].sort(key=lambda g: g['homeTeam'])
    
    # Convert to regular dict and sort by date
    games_output = dict(sorted(games_by_date.items()))
    
    # Write output
    with open(output_file, 'w') as f:
        json.dump(games_output, f, indent=2)
    
    game_count = sum(len(games) for games in games_output.values())
    LOGGER.info(f"Generated games.json with {game_count} games across {len(games_output)} dates")
