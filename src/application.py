import datetime
import os
import re

import dotenv
import pygame

def interpret_file(filename):
    # Check if the file exists.
    if not os.path.isfile(filename):
        print(f"Unable to locate `{filename}`. Consider updating the .env file to point to a valid location.")
        return {}
    
    # Read file contents.
    lines = []
    with open(filename, "r") as file:
        lines = file.readlines()
    
    # Setup regex patterns.
    date_pattern = r"^\d\d-\d\d-\d\d\d\d$"
    time_pattern = r"^\d\d\.\d\d-\d\d\.\d\d$"
    
    # Parse lines to dictionary.
    result = {"misc": []}
    current_date = None
    temp_list = []
    for line in lines:
        line = line.strip().replace("~", "")
        if line == "":
            continue
        
        # Keep only text before the first space.
        line = line.split(" ")[0]
        
        if re.match(date_pattern, line):
            if not (current_date is None):
                result[current_date] = temp_list
                temp_list = []
            current_date = line
        elif re.match(time_pattern, line):
            temp_list.append(line)
        else:
            continue
    
    # Add currently active date.
    result[current_date] = temp_list
    
    # Transform dict of List[str] to List[tuple(int, int)] containing integer minutes indicating the start and end minute.
    for key, value in result.items():
        new_value = []
        for v in value:
            start_minute = int(v.split("-")[0].split(".")[0]) * 60 + int(v.split("-")[0].split(".")[1])
            end_minute = int(v.split("-")[1].split(".")[0]) * 60 + int(v.split("-")[1].split(".")[1])
            new_value.append((start_minute, end_minute))
        result[key] = new_value
    
    # Remove misc entry.
    del result["misc"]
    
    # Add missing dates.
    dates = result.keys()
    # Reverse all dates then sort.
    dates = sorted(["-".join(date.split("-")[::-1]) for date in dates])
    # Check if there are missing dates.
    new_dates = []
    for index, date in enumerate(dates):
        if index == 0:
            continue
        
        d1 = datetime.datetime.strptime(dates[index - 1], "%Y-%m-%d")
        d2 = datetime.datetime.strptime(dates[index], "%Y-%m-%d")
        
        if (d2 - d1).days > 1:
            while d1 <= d2:
                new_dates.append(d1.strftime("%Y-%m-%d"))
                d1 += datetime.timedelta(days=1)
        else:
            new_dates.append(d1.strftime("%Y-%m-%d"))
    # Remove duplicates.
    new_dates = sorted(list(set(new_dates)))
    # Reverse all dates again.
    new_dates = ["-".join(date.split("-")[::-1]) for date in new_dates]
    
    # Add day names to dates.
    new_dates = [datetime.datetime.strptime(date, "%d-%m-%Y").strftime("%a") + f" {date}" for date in new_dates]
    
    # Populate new result using new dates.
    new_result = {}
    for date in new_dates:
        if date.split(" ")[1] in result.keys():
            new_result[date] = result[date.split(" ")[1]]
        else:
            new_result[date] = []
    
    return new_result

def visualize_result(result, color_palette):
    # Set render parameters.
    column_width = 200
    column_height = 1440
    top_bar_height = 40
    top_bar_font_size = 16
    left_bar_width = 50
    left_bar_font_size = 11
    
    # Get colors from color palette.
    background_color = color_palette[0]
    top_bar_background_color = color_palette[1]
    block_color = color_palette[2]
    text_color = color_palette[3]
    
    # Initialize pygame.
    pygame.init()
    pygame.font.init()
    
    # Initialize font.
    top_bar_font  = pygame.font.SysFont("Courier New", top_bar_font_size)
    left_bar_font = pygame.font.SysFont("Courier New", left_bar_font_size)
    
    # Create display.
    display = pygame.display.set_mode((column_width * len(result.keys()) + left_bar_width, column_height + top_bar_height))
    
    # Render top bar background, left bar background, and background.
    pygame.draw.rect(display, top_bar_background_color, (0, 0, left_bar_width, top_bar_height + column_height))
    pygame.draw.rect(display, top_bar_background_color, (left_bar_width, 0, column_width * len(result.keys()), top_bar_height))
    pygame.draw.rect(display, background_color, (left_bar_width, top_bar_height, column_width * len(result.keys()), column_height))
    
    # Render hours to the left of the graph.
    for hour in range(24):
        text_surface = left_bar_font.render(f"{hour}:00 ", False, text_color)
        text_y = top_bar_height + column_height * (hour * 60) / 1440 - (text_surface.get_height() / 2)
        display.blit(text_surface, (left_bar_width - text_surface.get_width(), text_y))
    
    # Render calendar.
    for index, (date, times) in enumerate(result.items()):
        # Render date in center of column.
        text_surface = top_bar_font.render(date, False, text_color)
        display.blit(text_surface, (left_bar_width + ((index + 0.5) * column_width) - (text_surface.get_width() / 2), (top_bar_height - text_surface.get_height()) / 2))
        
        # Render blocks for study hours.
        for time in times:
            block_left = left_bar_width + index * column_width
            block_top = top_bar_height + (column_height / 1440) * time[0]
            block_width = column_width
            block_height = (column_height / 1440) * (time[1] - time[0])
            pygame.draw.rect(display, block_color, (block_left, block_top, block_width, block_height))
    
    # Draw horizontal lines at each hour.
    for hour in range(1, 24):
        hour_y = top_bar_height + column_height * (hour * 60) / 1440
        pygame.draw.line(display, top_bar_background_color, (left_bar_width, hour_y), (left_bar_width + column_width * len(result.keys()), hour_y))
    
    # Draw vertical lines at each day.
    for day in range(1, len(result.keys())):
        day_x = left_bar_width + column_width * day
        pygame.draw.line(display, top_bar_background_color, (day_x, top_bar_height), (day_x, top_bar_height + column_height))
    
    # Save image.
    pygame.image.save(display, "image.png")
    
    # Print message.
    print("Output saved to `image.png`.")

def load_color_palette(palette_name):
    # Check if color palette exists. If not, default to marine blue.
    if not (palette_name in ["COLOR_PALETTE_PURPLE", "COLOR_PALETTE_PURPLE_DARK", "COLOR_PALETTE_MARINE", "COLOR_PALETTE_MARINE_DARK", "COLOR_PALETTE_MARINE_BLUE"]):
        print(f"Color palette name is invalid `{palette_name}`, defaulting to `COLOR_PALETTE_MARINE_BLUE`.")
        palette_name = "COLOR_PALETTE_MARINE_BLUE"
    
    # Load color palette from dotenv file.
    color_palette = os.getenv(palette_name)
    
    # Split by comma and strip away any non integer characters.
    numbers = [int(re.sub(r"\D", "", number)) for number in color_palette.split(",")]
    
    # Join every three integers into a tuple.
    return [tuple(numbers[i:i+3]) for i in range(0, len(numbers), 3)]

def main():
    # Load dotenv file.
    dotenv.load_dotenv()
    
    # Print welcome prompt.
    print("Welcome to the study hours file interpreter and visualizer.")
    
    # Load filename from .env file and interpret file.
    filename = os.getenv("DATAPATH")
    result = interpret_file(filename)
    
    # Load color palette and visualize result.
    color_palette_name = "COLOR_PALETTE_MARINE_BLUE"
    color_palette = load_color_palette(color_palette_name)
    visualize_result(result, color_palette)

if __name__ == "__main__":
    main()
