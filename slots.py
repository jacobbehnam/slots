import tkinter as tk
import customtkinter as ctk
import random
import time
from PIL import Image

win = ctk.CTk()
win.title("Gamba")
win.geometry("1000x1000")

#Variables
SF = 4 # Scale factor -- don't touch will remove later
EXTRA_SPINS = 6 # Change to increase/decrease displacement of reel before stopping
MOVE_AMOUNT = (800 + 100*EXTRA_SPINS)*SF
chosenColorIndex = []
colors = ["purple", "green", "pink", "yellow", "red", "blue", "black"]
mults = [[1,1,1],
         [1,1,1],
         [1,1,1]
         ]
mult_labels = {}
probability_labels = {}
money = [10] # In dollars
remaining_spins = [1]
current_round = [1]
colors_purchased = [0]
colors_removed = [0]
purchased_mults = [0]
bomb_hit_chance = [0]

def ease_in_out_derivative(t):
    # Derivative of ease_in_out function t^2(3-2t)
    return 6*t*(1-t)

def start_button_click(start_frame):
    start_frame.pack_forget()
    game_frame.pack(expand=True, fill="both")

def round_complete():
    bonus_payout = ctk.CTkLabel(canvas, text=f"Round \n Complete \n Bonus: \n ${current_round[0] * 5}",
                                font=("Arial", 100, "bold"))
    bonus_payout.place(relx=0.5, rely=0.5, anchor="center")
    money_label.configure(text=f"Money: ${money[0]} + ${current_round[0] * 5}")
    bomb_hit_chance[0] = min(bomb_hit_chance[0]+0.04, 1) # Adds 4% Chance to a max of 100%
    bomb_hit_chance_label.configure(text=f"Next Round Bomb Hit Chance: {int(bomb_hit_chance[0]*100)}%")
    money[0] += current_round[0] * 5
    win.after(2000, lambda: bonus_payout.destroy())
    win.after(2000, lambda: continue_button.configure(state="normal"))
    win.after(2000, lambda: money_label.configure(text=f"Money: ${money[0]}"))
    spin_button.pack_forget()
    tutorial_frame.pack_forget()
    min_next_round_label.configure(text=f"Minimum for next round: ${((2**(current_round[0]))-1)*5}")
    min_next_round_label.pack()
    continue_button.pack(pady=20, padx=10)
    shop_frame.pack(fill="both", pady=10)

def animate_paylines(paylines_animated=0):
    if money[0] < ((2**(current_round[0]-1))-1):
        game_over()
    else:       
        paylines = canvas.find_withtag("payline")
        flashing_payline = canvas.find_withtag("flashing_payline")
        
        if len(flashing_payline) != 0: # If there's a payline on the screen, delete it
            canvas.delete(flashing_payline[0])
            canvas.delete(flashing_payline[1])
            
        # Flash all the paylines one by one
        if len(paylines) != 0:
            for i in range(2):
                paylines = canvas.find_withtag("payline")
                line = paylines[0]
                payline_value = float(canvas.gettags(line)[1])
                canvas.itemconfig(line, state="normal", tag="flashing_payline")
            
            # This block of code gives the player a visual representation of how the paylines are paying out
            # In calculate_paylines the formula was line_pays*hits so this is summing up all the lines pays and multiplying it by the total hits (paylines animated)
            current_money_text = money_label.cget("text").rstrip(f") x {paylines_animated}")
            if "(" in current_money_text:
                money_label.configure(text=f"{current_money_text} + ${payline_value}) x {paylines_animated+1}")
            else:
                money_label.configure(text=f"{current_money_text} + (${payline_value}) x {paylines_animated+1}")
            
            # Recursively call this function until all paylines have been animated
            win.after(750 - paylines_animated*50, animate_paylines, paylines_animated+1)
        else:
            money_label.configure(text=f"Money: ${money[0]}")
            remaining_spins[0] -= 1
            spins_remaining_label.configure(text=f"Spins remaining: {remaining_spins[0]}")
            spin_button.configure(state="normal")
            if remaining_spins[0] == 0:
                round_complete()

def calculate_paylines(chosen_colors):
    paylines = {
        "Top Line": [(0,2), (1,2), (2,2)],
        "Middle Line": [(0,3), (1,3), (2,3)],
        "Bottom Line": [(0,4), (1,4), (2,4)],
        "Top Diagonal": [(0,2), (1,3), (2,4)],
        "Bottom Diagonal": [(0,4), (1,3), (2,2)],
        "Up Zigzag 1": [(0,2), (1,3), (2,2)],
        "Up Zigzag 2": [(0,3), (1,4), (2,3)],
        "Down Zigzag 1": [(0,3), (1,2), (2,3)],
        "Down Zigzag 2": [(0,4), (1,3), (2,4)]
    }
    hits = 0
    line_pays = 0
    # Checks how many paylines hit and draws the paylines as hidden (animated once spin() is finished)
    for name, payline in paylines.items():
        if chosen_colors[0][payline[0][1]] == chosen_colors[1][payline[1][1]] == chosen_colors[2][payline[2][1]]:
            hits += 1
            mult = mults[0][payline[0][1]-2] * mults[1][payline[1][1]-2] * mults[2][payline[2][1]-2]
            line_pays += 10*mult
            canvas.create_line(50*SF, ((payline[0][1]-2)*100+50)*SF, 150*SF, ((payline[1][1]-2)*100+50)*SF, width=7, state="hidden", fill="grey", tags=("payline",f"{10*mult}"))
            canvas.create_line(150 * SF, ((payline[1][1] - 2) * 100 + 50) * SF, 250 * SF, ((payline[2][1] - 2) * 100 + 50) * SF, width=7, state="hidden", fill="grey", tags=("payline",f"{10*mult}"))
    if hits != 0:
        money[0] += line_pays*hits

def bomb_hit(chosen_colors):
    for i, column in enumerate(chosen_colors):
        if "BOMB" in column:
            bomb_column = i
            bomb_row = column.index("BOMB") - 2
            break
    else:
        return

    bomb_rectangle = ctk.CTkLabel(canvas, text="", image=scaled_bomb_image, fg_color="lightsteelblue2")
    if (bomb_column, bomb_row) in mult_labels: # Ensures the bomb is always below the mult label on that square (if it exists)
        bomb_rectangle.lower(mult_labels[(bomb_column, bomb_row)][0])
    bomb_rectangle.place(relx=bomb_column/3, rely=bomb_row/3, y=5*SF)
    win.after(500, lambda: bomb_rectangle.destroy())
    
    if mults[bomb_column][bomb_row] > 0:
        mults[bomb_column][bomb_row] = 0
        if (bomb_column, bomb_row) in mult_labels:
            old_label = mult_labels[(bomb_column, bomb_row)][0]
            old_label.destroy()
        label = ctk.CTkLabel(canvas, width=50 * SF, height=10 * SF, text=f"❌ {0}",
                             font=("Arial", 20, "bold"), fg_color="lightsteelblue2", text_color="white")
        mult_labels[(bomb_column, bomb_row)] = [label, 0]
        label.place(x=0 + bomb_column * 50 * SF, y=bomb_row * 50 * SF)

def spin_button_click():   
    spin_button.configure(state="disabled")
    chosen_colors = []
    
    # This determines what the final state of the spin will be. Can be edited to anything.
    # Chosen colors is a 3 x 7 2D list. What will show up on the 3x3 spinner will be the middle elements
    # Ex. if one column is ['red', 'yellow', 'blue', 'pink', 'red', 'blue', 'black'], the spinner will land on blue, pink, red, in that order in that column.
    for j in range(3):
        column = []
        for i in range(7):
            #column.append(colors[2])
            column.append(colors[random.randint(0,len(colors)-1)])
        chosen_colors.append(column)
    
    is_bomb = random.random() >= 1-bomb_hit_chance[0] # Change to change chance of hitting bomb
    if is_bomb:
        random_column = random.randint(0, 2)
        random_row = random.randint(0, 2)
        chosen_colors[random_column][random_row + 2] = "BOMB"
    
    start_time = time.perf_counter()
    money[0] -= (2**(current_round[0]-1))-1 # Price per spin
    money_label.configure(text=f"Money: ${money[0]}")
    calculate_paylines(chosen_colors)
    spin(chosen_colors, start_time, start_time)
    
def continue_button_click():
    current_round[0] += 1
    if money[0] < ((2**(current_round[0]-1))-1):
        game_over()
    else:
        continue_button.configure(state="disabled")
        continue_button.pack_forget()
        shop_frame.pack_forget()
        min_next_round_label.pack_forget()
        spin_button.pack(pady=20, padx=10)
        tutorial_frame.pack(fill="both", expand=True)
        cost_to_spin_label.configure(text=f"Cost per spin: ${(2**(current_round[0]-1))-1}")
        remaining_spins[0] = 5
        spins_remaining_label.configure(text=f"Spins remaining: {remaining_spins[0]}")
        rounds_label.configure(text=f"Round {current_round[0]}")
        bomb_hit_chance_label.configure(text=f"Bomb Hit Chance: {int(bomb_hit_chance[0]*100)}%")

def mult_purchase(row_frames, row, column):
    for frame in row_frames:
        frame.destroy()
        
    current_mult = mults[column][row]
    purchased_mults[0] += 1
    continue_button.configure(state="normal")
    buy_mult_button.configure(state="normal", text=f"Buy Mult \n ${4 + 2**purchased_mults[0]}")
    
    if (column,row) in mult_labels:
        old_label = mult_labels[(column, row)][0]
        old_label.destroy()
    
    if current_mult == 0:
        mults[column][row] = current_mult + 1
        mult_labels.pop((column, row))
    else:
        mults[column][row] *= 2
        new_mult = mults[column][row]
        label = ctk.CTkLabel(canvas, width=50 * SF, height=10 * SF, text=f"❌ {new_mult}", font=("Arial", 20, "bold"),
                             fg_color="lightsteelblue2", text_color="white")
        mult_labels[(column, row)] = [label, new_mult]
        label.place(x=0 + column * 50 * SF, y=row * 50 * SF)
        
def buy_mult_click():
    if money[0] >= (4 + 2**purchased_mults[0]):
        money[0] -= (4 + 2**purchased_mults[0])
        money_label.configure(text=f"Money: ${money[0]}")
        continue_button.configure(state="disabled")
        buy_mult_button.configure(state="disabled")
        row_frames = []
        for row in range(3):
            row_frame = ctk.CTkFrame(canvas, width=150*SF)
            row_frames.append(row_frame)
            row_frame.pack_propagate(False)
            row_frame.pack()
            for column in range(3):
                mult_of_square = mults[column][row]
                if mult_of_square == 0:
                    new_mult = 1
                else:
                    new_mult = mult_of_square*2
                button = ctk.CTkButton(row_frame, width=50*SF, height=100*SF, text=f"Click to place mult here \n\n New mult: x{new_mult}", command=lambda row=row, column=column: mult_purchase(row_frames, row, column))
                button.pack(side="left", anchor="nw")
            for mult in mult_labels.values():
                mult[0].lift()
    else:
        buy_mult_button.configure(text="Not enough money!", state="disabled")
        win.after(1000, lambda: buy_mult_button.configure(text=f"Buy Mult \n ${4+2**purchased_mults[0]}", state="normal"))

def update_probabilities():
    for color, label in probability_labels.items():
        num_colors = colors.count(color)
        label.configure(text=f"{color} \n {num_colors/len(colors)*100:.1f}%")

def color_remove_click():
    if money[0] >= (49 + 5**(colors_removed[0]*2)):
        if color_remove_button.cget("text") != "Remove":
            continue_button.configure(state="disabled")
            buy_mult_button.configure(state="disabled")
            color_add_button.configure(state="disabled")
            color_remove_options.pack(side="bottom", pady=5)
            color_remove_button.configure(text="Remove")
        elif color_remove_options.get() == "Select a Color":
            color_remove_button.configure(text="Select Color!", state="disabled")
            win.after(1000, lambda: color_remove_button.configure(text="Remove", state="normal"))
        else:
            money[0] -= (49 + 5**(colors_removed[0]*2))
            colors_removed[0] += 1
            money_label.configure(text=f"Money: ${money[0]}")
            selected_color = color_remove_options.get()
            colors.remove(selected_color)
            update_probabilities()
            color_remove_options.configure(values = [color for color in colors])
            color_remove_options.set("Select a Color")
            color_remove_options.pack_forget()
            color_remove_button.configure(text=f"Remove a Color \n ${(49 + 5**(colors_removed[0]*2))}")
            continue_button.configure(state="normal")
            buy_mult_button.configure(state="normal")
            color_add_button.configure(state="normal")
    else:
        color_remove_button.configure(text="Not enough money!", state="disabled")
        win.after(1000, lambda: color_remove_button.configure(text=f"Remove a Color \n ${(49 + 5**(colors_removed[0]*2))}", state="normal"))

def color_add_click():
    if money[0] >= (14 + 5**(colors_purchased[0]*2)):
        if color_add_button.cget("text") != "Add":
            continue_button.configure(state="disabled")
            buy_mult_button.configure(state="disabled")
            color_remove_button.configure(state="disabled")
            color_add_options.pack(side="bottom", pady=5)
            color_add_button.configure(text="Add")
        elif color_add_options.get() == "Select a Color":
            color_add_button.configure(text="Select Color!", state="disabled")
            win.after(1000, lambda: color_add_button.configure(text="Add", state="normal"))
        else:
            money[0] -= (14 + 5**(colors_purchased[0]*2))
            colors_purchased[0] += 1
            money_label.configure(text=f"Money: ${money[0]}")
            selected_color = color_add_options.get()
            colors.append(selected_color)
            update_probabilities()
            color_add_options.set("Select a Color!")
            color_add_options.pack_forget()
            color_add_button.configure(text=f"Add a Color \n ${14 + 5**(colors_purchased[0]*2)}")
            continue_button.configure(state="normal")
            buy_mult_button.configure(state="normal")
            color_remove_button.configure(state="normal")
    else:
        color_add_button.configure(text="Not enough money!", state="disabled")
        win.after(1000, lambda: color_add_button.configure(text=f"Add a Color \n ${14 + 5**(colors_purchased[0]*2)}", state="normal"))
        
def hideshow_tutorial():
    if tutorial_hideshow.cget("text") == "Hide Tutorial":
        tutorial_text.pack_forget()
        tutorial_hideshow.configure(text="Show Tutorial")
    elif tutorial_hideshow.cget("text") == "Show Tutorial":
        tutorial_text.pack(pady=10)
        tutorial_hideshow.configure(text="Hide Tutorial")

def show_paylines_info():
    payline_info_hideshow.configure(state="disabled")
    payline_info_frame.place(relx=0.5, rely=0.5, anchor="center")
    
def close_paylines_info():
    payline_info_hideshow.configure(state="normal")
    payline_info_frame.place_forget()
    
def create_spinner(): 
    # Reels
    color_heights = (600/(len(colors)-1))*SF
    for i in range(1, 4):
        for count, j in enumerate(colors):
            canvas.create_rectangle(0 + 100*(i-1)*SF, (count)*color_heights-200*SF, 100*i*SF, (count+1)*color_heights-200*SF, fill=j, tags=f"reel{i}")
    for i in range(1, 3): # Horizontal Lines
        canvas.create_line(0, 100*SF*i, 300*SF, 100*SF*i, width=10, fill="lightsteelblue2")
    canvas.create_line(0, 5, 300*SF, 5, width=10, fill="lightsteelblue2")
    canvas.create_line(0, 300*SF-5, 300 * SF, 300*SF-5, width=10, fill="lightsteelblue2")
    for i in range(1, 3): # Vertical Lines
        canvas.create_line(100*SF*i, 0, 100*SF*i, 300*SF, width=10, fill="lightsteelblue2")
    canvas.create_line(5, 0, 5, 300*SF, width=10, fill="lightsteelblue2")
    canvas.create_line(300*SF - 5, 0, 300*SF - 5, 300 * SF, width=10, fill="lightsteelblue2")
    
def create_start_screen():
    # Tries to read records file to find best run
    try:
        with open("records.txt") as records:
            best_run_text = records.readline()
    except FileNotFoundError:
        best_run_text = "Best Run: 0 Rounds Survived"
        
    start_frame = ctk.CTkFrame(win)
    start_frame.pack(expand=True, fill="both")
    title_frame = ctk.CTkFrame(start_frame, fg_color="transparent")
    title_text = ctk.CTkLabel(title_frame, text="Slot Machine Simulator", font=("Arial", 75, "bold"))
    subtitle_text = ctk.CTkLabel(title_frame, text="gambling is bad, but not if you aren't spending real money!", font=("Arial", 30))
    best_run_label = ctk.CTkLabel(title_frame, text=best_run_text, font=("Arial", 20), text_color="red")
    start_button = ctk.CTkButton(title_frame, text="Press to play", command=lambda: start_button_click(start_frame))
    title_frame.pack(expand=True)
    title_text.pack(pady=10)
    subtitle_text.pack()
    best_run_label.pack(pady=20)
    start_button.pack()
    
def create_spin_map():
    spin_map = []
    spin_column = []
    for i in range(3):
        for j in range(7):
            spin_column.append(((j+1)+(i*7), colors[j])) # Tuple of the rectangle's id (needed to configure the rectangle) and its color
        spin_map.append(spin_column)
        spin_column = []
    return spin_map
    
def update_spin_map(spinning_reels, chosen_colors, count):
    spinning_reels = len(spinning_reels) // 7 # Will give a value of 3 2 or 1 depending on how many reels are still spinning
    NUM_COLORS = 3
    spinning_column = NUM_COLORS - spinning_reels
    count -= EXTRA_SPINS # Once count is >=0, that means we are on the last spin for the current column -> must match colors with the predetermined ones rather than randomizing
    distance_travelled = count*100*SF
    
    if distance_travelled >= 0: # If on last spin, start changing the colors of spinning column to what they should be
        # We do this by deleting the last rectangle in the currently spinning column off the spin map
        last_rectangle = spin_map[spinning_column].pop()
        # Then changing the color of the first rectangle (which is off-screen) in the currently spinning column to match the chosen colors list back to front
        new_color = chosen_colors[spinning_column][6-count]
        if new_color != "BOMB":
            canvas.itemconfig(spin_map[spinning_column][-1][0], fill=new_color)
        else:
            canvas.itemconfig(spin_map[spinning_column][-1][0], fill="lightsteelblue2")
        # And finally refreshing the spin map to be accurate for what is displayed
        spin_map[spinning_column][-1] = (spin_map[spinning_column][-1][0], new_color)
        spin_map[spinning_column].insert(0, last_rectangle)
        # After repeating this for all the rectangles on the last spin, the color of the rectangles will match the predetermined colors
        
        # This is so the colors aren't randomized for the currently spinning column
        spinning_column += 1

    # Randomly change the colors for every column that isn't the spinning column
    for column in range(2, spinning_column - 1, -1):
        last_rectangle = spin_map[column].pop()
        random_color = colors[random.randint(0,len(colors)-1)]
        canvas.itemconfig(spin_map[column][-1][0], fill=random_color)
        spin_map[column][-1] = (spin_map[column][-1][0], random_color)
        spin_map[column].insert(0, last_rectangle)
    
    return spin_map

def restart_game():
    game_over_frame.place(relx=-0.5, rely=0.5, anchor="center")
    game_over_frame.place_forget()
    game_frame.pack_forget()
    create_start_screen()
    colors.clear()
    colors.extend(["purple", "green", "pink", "yellow", "red", "blue", "black"])
    mults.clear()
    mults.extend([[1, 1, 1],
                  [1, 1, 1],
                  [1, 1, 1]
                ])
    money[0] = 10
    remaining_spins[0] = 1
    current_round[0] = 1
    colors_purchased[0] = 0
    colors_removed[0] = 0
    purchased_mults[0] = 0
    bomb_hit_chance[0] = 0
    buy_mult_button.configure(text="Buy Mult \n $5")
    color_add_button.configure(text="Add a Color \n $15")
    color_remove_button.configure(text="Remove a Color \n $50")
    money_label.configure(text=f"Money: ${money[0]}")
    spins_remaining_label.configure(text=f"Spins remaining: {remaining_spins[0]}")
    rounds_label.configure(text=f"Round {current_round[0]}")
    cost_to_spin_label.configure(text="Cost per spin: $0")
    bomb_hit_chance_label.configure(text=f"Bomb Hit Chance: {int(bomb_hit_chance[0]*100)}%")
    shop_frame.pack_forget()
    continue_button.configure(state="normal")
    continue_button.pack_forget()
    spin_button.configure(state="normal")
    spin_button.pack()
    tutorial_hideshow.configure(state="normal")
    payline_info_hideshow.configure(state="normal")
    for mult_label in mult_labels.values():
        mult_label[0].destroy()
    mult_labels.clear()
    update_probabilities()

def animate_game_over(start_time, last_time, x=-0.5):
    current_time = time.perf_counter()
    elapsed = (current_time-start_time)/1.5
    dt = current_time - last_time
    if elapsed > 1:
        elapsed = 1
        game_over_button.configure(state="normal")
    ease_velocity = ease_in_out_derivative(elapsed)
    move_amount = (ease_velocity*dt)/1.5
    
    game_over_frame.place(relx=x+move_amount, rely=0.5, anchor="center")
    
    if elapsed < 1:
        win.after(10, animate_game_over, start_time, current_time, x+move_amount)

def game_over():
    game_over_rounds_survived.configure(text=f"Rounds Survived: {current_round[0]}")
    tutorial_hideshow.configure(state="disabled")
    payline_info_hideshow.configure(state="disabled")
    try:
        best_run_file = open("records.txt", "r")
        best_run_file.readline()
        best_run = int(best_run_file.read(1))
    except FileNotFoundError:
        best_run = 0

    if best_run < current_round[0]:
        with open("records.txt", "w") as record:
            record.write(f"Best Run: {current_round[0]} Rounds Survived \n") # 1st line will be duplicated on title screen
            record.write(str(current_round[0])) # 2nd line is read by code to determine best_run
    animate_game_over(time.perf_counter(), time.perf_counter())

def spin(chosen_colors, start_time, last_time, reel = 1, count = 0, total_moved = 0): 
    deltaT = 4 # (in milliseconds) Time between spin recursive function calls
    duration_of_spin = 0.05 * (reel-3) * (reel-3) + 1 # (in seconds) -> speeds up reel by reel
    
    # Puts all the currently spinning reels (determined by the reel parameter) in a list
    reels = [canvas.find_withtag("reel1"), canvas.find_withtag("reel2"), canvas.find_withtag("reel3")]
    spinning_reels = []
    for i in range(4 - reel):
        spinning_reels += reels[2-i]
    
    # This is to figure out how much to move the rectangles such that it animated in a non-linear way
    # We start by finding dt which depends on how fast the spin function is called (ideally dt is infinitesimal)
    # Then we find the velocity of the rectangle and integrate that velocity with respect to time
    current_time = time.perf_counter()
    elapsed = (current_time-start_time)/duration_of_spin
    dt = current_time - last_time
    if elapsed > 1:
        total_moved = 100*SF
        elapsed = 1
    ease_velocity = ease_in_out_derivative(elapsed) * MOVE_AMOUNT
    move_amount = (ease_velocity*dt)/duration_of_spin
    
    # Moves all rectangles in spinning_reels. Moves rectangles back up to the top if reaching the edge of the canvas
    for rectangle in spinning_reels:
        x1, y1, x2, y2 = canvas.coords(rectangle)
        canvas.move(rectangle, 0, move_amount)
        if y2 >= 700*SF:
            canvas.move(rectangle, 0, -700*SF)
    
    total_moved += move_amount
    if total_moved >= 100*SF: # The width of a rectangle
        update_spin_map(spinning_reels, chosen_colors, count)
            
        if count != 7+EXTRA_SPINS: # Keep recursively calling the spin function until the reel has spun at least once (7 rectangles) plus some additional rectangles specified with the EXTRA_SPINS variable
            win.after(deltaT, spin, chosen_colors, start_time, current_time, reel, count + 1)
        else:
            for rectangle in reels[reel - 1]: # Nudges all rectangles in current reel to exact position
                x1, y1, x2, y2 = canvas.coords(rectangle)
                canvas.coords(rectangle, x1, (round(y1 / (100*SF)) * 100*SF), x2, (round(y2 / (100*SF)) * 100*SF))
            if(reel < 3): # Continues spinning excluding the current column if not all reels finished spinning
                win.after(deltaT, spin, chosen_colors, current_time, current_time, reel+1)
            else:
                bomb_hit(chosen_colors) # Will change mult on square if bomb was hit
                animate_paylines()
    else:
        win.after(deltaT, spin, chosen_colors, start_time, current_time, reel, count, total_moved)

# Opens the images
try:
    # Using .copy() keeps the image saved in memory so I don't have to keep opening the images to access them
    with Image.open(
            "Images/bomb.png").copy() as bomb_image, Image.open("Images/Le Slot.png").copy() as le_slot_image, Image.open("Images/paylines.png").copy() as payline_info_image:
        scaled_bomb_image = ctk.CTkImage(bomb_image, size=(50*SF,45*SF)) # For spinner
        info_scaled_bomb_image = ctk.CTkImage(bomb_image, size=(50, 50)) # For bomb hit chance
        scaled_le_slot_image = ctk.CTkImage(le_slot_image, size=(125*SF, 21*SF))
        scaled_payline_info_image = ctk.CTkImage(payline_info_image, size=(800, 600))
except FileNotFoundError as e:
    print(f"Cannot access all image dependencies: {e}")
    raise SystemExit

# All the UI elements
# I wish I could put these in a function :\ (I regret not making this with OOP)

create_start_screen()

game_frame = ctk.CTkFrame(win)
#game_frame.pack(expand=True, fill="both")

# Left UI
slot_frame = ctk.CTkFrame(game_frame, fg_color="transparent")
canvas = tk.Canvas(slot_frame, width=300*SF, height=300*SF, bg="black", highlightthickness=0)
slot_title = ctk.CTkLabel(slot_frame, image=scaled_le_slot_image, text="")
slot_frame.pack(side="left", padx=100, expand=True)
control_frame = ctk.CTkFrame(game_frame, width=50*SF, height=300*SF)
control_frame.pack_propagate(False)
control_frame.pack(side="right", fill="both", expand=True)
slot_title.pack(pady=10)
canvas.pack(pady=20)
create_spinner()
spin_map = create_spin_map()

# Right UI
money_label = ctk.CTkLabel(control_frame, width = 100, height=50, text=f"Money: ${money[0]}", wraplength=200)
cost_to_spin_label = ctk.CTkLabel(control_frame, width=100, height=50, text="Cost per spin: $0")
rounds_label = ctk.CTkLabel(control_frame, width = 100, height=50, text="Round 1")
spins_remaining_label = ctk.CTkLabel(control_frame, width=100, height=50, text=f"Spins remaining: {remaining_spins[0]}")
min_next_round_label = ctk.CTkLabel(control_frame, width=100, height=50, text="Minimum for next round: $0")
rounds_label.pack(side="top", anchor="nw")
spins_remaining_label.pack(side="top", anchor="nw", padx=25)
spin_button = ctk.CTkButton(control_frame, text="Spin", command=spin_button_click)
continue_button = ctk.CTkButton(control_frame, text="Continue", state="disabled", command=continue_button_click)
shop_frame = ctk.CTkScrollableFrame(control_frame, height=500)
items_frame1_title = ctk.CTkLabel(shop_frame, text="Multipliers")
items_frame1 = ctk.CTkFrame(shop_frame, height=100, fg_color="#A9A9A9")
items_frame2_title = ctk.CTkLabel(shop_frame, text="Chance modifiers")
items_frame2 = ctk.CTkFrame(shop_frame, height=100, fg_color="#A9A9A9")
color_remove_frame = ctk.CTkFrame(items_frame2, fg_color="transparent")
color_add_frame = ctk.CTkFrame(items_frame2, fg_color="transparent")
probability_labels_frame = ctk.CTkFrame(control_frame, fg_color="#A9A9A9")
buy_mult_button = ctk.CTkButton(items_frame1, width=100, height=50, text="Buy Mult \n $5", command=buy_mult_click)
color_remove_button = ctk.CTkButton(color_remove_frame, width=100, height=50, text="Remove a Color \n $50", command=color_remove_click)
color_remove_options = ctk.CTkComboBox(color_remove_frame, width=100, height=25, values=[color for color in colors], state="readonly")
color_remove_options.set("Select a Color")
color_add_button = ctk.CTkButton(color_add_frame, width=100, height=50, text="Add a Color \n $15", command=color_add_click)
color_add_options = ctk.CTkComboBox(color_add_frame, width=100, height=25, values=["purple", "green", "pink", "yellow", "red", "blue", "black"], state="readonly")
color_add_options.set("Select a Color")
tutorial_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
tutorial_text = ctk.CTkLabel(tutorial_frame, wraplength=400, text="How to Play: \n\n "
                                                  "The goal is to last as many rounds as possible. \n\n"
                                                  "You spend money on spins that cost more and more each round. \n\n"
                                                  "After enough spins, you will move on to the next round. \n\n"
                                                  "You get a payout for surviving each round. \n\n"
                                                  "Prepare for the next round by purchasing upgrades in the shop. \n\n"
                                                  "You can only buy upgrades in between rounds. \n\n"
                                                  "The percentages below are the chances of each color showing up. \n\n"                
                                                  "The game ends if you cannot afford another spin. \n\n"
                                                  "Good luck!")
help_buttons_frame = ctk.CTkFrame(tutorial_frame, fg_color="transparent")
tutorial_hideshow = ctk.CTkButton(help_buttons_frame, text="Show Tutorial", command=hideshow_tutorial)
payline_info_hideshow = ctk.CTkButton(help_buttons_frame, text="Show Paylines", command=show_paylines_info)
bomb_hit_chance_frame = ctk.CTkFrame(control_frame, fg_color="#A9A9A9")
bomb_hit_chance_image = ctk.CTkLabel(bomb_hit_chance_frame, image=info_scaled_bomb_image, text="")
bomb_hit_chance_label = ctk.CTkLabel(bomb_hit_chance_frame, text="Bomb Hit Chance: 0%", text_color="black")

money_label.pack()
cost_to_spin_label.pack()
spin_button.pack(pady=20, padx=10)
shop_frame.pack(fill="both", pady=10)
items_frame1_title.pack()
items_frame1.pack_propagate(False)
items_frame1.pack(fill="x", padx=10)
separation_frame1 = ctk.CTkFrame(shop_frame, height=20, fg_color="transparent")
separation_frame1.pack()
items_frame2_title.pack()
items_frame2.pack_propagate(False)
items_frame2.pack(fill="x", padx=10)
buy_mult_button.pack(side="left", padx=10)
color_remove_frame.pack(side="left", padx=10)
color_remove_button.pack(padx=10)
color_add_frame.pack(side="left", padx=10)
color_add_button.pack(padx=10)
tutorial_frame.pack(fill="both", expand=True)
help_buttons_frame.pack(pady=20, fill="x", side="bottom")
tutorial_hideshow.pack(padx=20, side="left", fill="x", expand=True)
payline_info_hideshow.pack(padx=20, side="left", fill="x", expand=True)
hideshow_tutorial()
probability_labels_frame.pack(side="bottom", fill="x", pady=10)
bomb_hit_chance_frame.pack(side="bottom")
bomb_hit_chance_image.pack(side="left", padx=10)
bomb_hit_chance_label.pack(side="right", padx=10)

for color in colors:
    probability_labels[f"{color}"] = ctk.CTkLabel(probability_labels_frame, text=f"{color} \n 14.3%", text_color=f"{color}")
    probability_labels[f"{color}"].pack(side="left", fill="x", expand=True)

payline_info_frame = ctk.CTkFrame(game_frame, width=800, height=600)
payline_info_label = ctk.CTkLabel(payline_info_frame, image=scaled_payline_info_image, text="")
payline_info_label.pack()
payline_info_close = ctk.CTkButton(payline_info_frame, width=50, height=50, text="X", fg_color="red", command=close_paylines_info)
payline_info_close.place(relx=1,rely=0, anchor="ne")

game_over_font = ctk.CTkFont(family="Arial", size=100, weight="bold")
game_over_frame = ctk.CTkFrame(win)
game_over_label = ctk.CTkLabel(game_over_frame, text="GAME OVER", font=game_over_font, text_color="red")
game_over_rounds_survived = ctk.CTkLabel(game_over_frame, text=f"Rounds Survived: {current_round[0]}", font=("Arial", 50))
game_over_button = ctk.CTkButton(game_over_frame, text="Return to start screen", command=restart_game, state="disabled")
game_over_label.pack(padx=2000) # It makes it look cooler (trust)
game_over_rounds_survived.pack()
game_over_button.pack(pady=10)

# -> Can buy perma free spins per round to a max of 5(?) out of total 10 spins
# -> Maybe also increase value of line pay (rn its $10 can upgrade to $20+)

shop_frame.pack_forget()
win.mainloop()