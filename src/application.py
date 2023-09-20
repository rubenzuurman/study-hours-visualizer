import os

import dotenv

def interpret_file(filename):
    if not os.path.isfile(filename):
        print(f"Unable to locate `{filename}`. Consider updating the .env file to point to a valid location.")
        return {}
    
    return {}

def visualize_result(result, choice):
    pass

def main():
    # Print welcome prompt.
    print("Welcome to the study hours file interpreter and visualizer.")
    
    # Get option to render to window or to png.
    print("Where would you like to render the result?")
    print("  1) to a live window")
    print("  2) to a PNG file")
    #choice = input("")
    choice = "1"
    while not (choice.strip() in ["1", "2"]):
        print(f"Not a valid option: `{choice}`. Please try again.")
        choice = input("")
    choice = int(choice)
    
    # Interpret file.
    dotenv.load_dotenv()
    filename = os.getenv("DATAPATH")
    result = interpret_file(filename)
    
    # Visualize result.
    visualize_result(result, choice)

if __name__ == "__main__":
    main()
