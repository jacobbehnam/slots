import tkinter as tk
import customtkinter as ctk
import random
import time
from PIL import Image, ImageTk

win = ctk.CTk()
win.title("Gamba")
win.geometry("1000x1000")

#Variables
SF = 4
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

def ease_in_out_derivative(t):
    # Derivative of ease_in_out function t^2(3-2t)
    return 6*t*(1-t)

def start_button_click():
    start_frame.pack_forget()
    game_frame.pack(expand=True, fill="both")

def animate_paylines():
    if money[0] <= 0:
        game_over(time.perf_counter(), time.perf_counter())
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
                canvas.itemconfig(line, state="normal", tag="flashing_payline")
            win.after(1000, animate_paylines)
        else:
            money_label.configure(text=f"Money: ${money[0]}")
            remaining_spins[0] -= 1
            spins_remaining_label.configure(text=f"Spins remaining: {remaining_spins[0]}")
            spin_button.configure(state="normal")
            if remaining_spins[0] == 0:
                bonus_payout = ctk.CTkLabel(canvas, text=f"Round \n Complete \n Bonus: \n ${current_round[0]*5}", font=("Arial", 100, "bold"))
                bonus_payout.place(x=55, y=45)
                money[0] += current_round[0]*5
                money_label.configure(text=f"Money: ${money[0]}")
                win.after(2000, lambda: bonus_payout.destroy())
                win.after(2000, lambda: continue_button.configure(state="normal"))
                spin_button.pack_forget()
                continue_button.pack(pady=20, padx=10)
                shop_frame.pack(fill="both", pady=10)

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
            canvas.create_line(50*SF, ((payline[0][1]-2)*100+50)*SF, 150*SF, ((payline[1][1]-2)*100+50)*SF, width=3, state="hidden", fill="grey", tags="payline")
            canvas.create_line(150 * SF, ((payline[1][1] - 2) * 100 + 50) * SF, 250 * SF, ((payline[2][1] - 2) * 100 + 50) * SF, width=3, state="hidden", fill="grey", tags="payline")
            hits += 1
            mult = mults[0][payline[0][1]-2] * mults[1][payline[1][1]-2] * mults[2][payline[2][1]-2]
            line_pays += 10*mult
    if hits != 0:
        money[0] += (line_pays/hits)*hits*hits
    
def spin_button_click():   
    spin_button.configure(state="disabled")
    chosen_colors = []
    for j in range(3):
        column = []
        for i in range(7):
            #column.append(colors[2])
            column.append(colors[random.randint(0,len(colors)-1)])
        chosen_colors.append(column)
        
    start_time = time.perf_counter()
    money[0] -= current_round[0]-1 # Price per spin
    money_label.configure(text=f"Money: ${money[0]}")
    spin(chosen_colors, start_time, start_time)
    calculate_paylines(chosen_colors)
    print(chosen_colors)
    
def continue_button_click():
    current_round[0] += 1
    if money[0] < current_round[0]-1:
        game_over(time.perf_counter(), time.perf_counter())
    else:
        continue_button.configure(state="disabled")
        continue_button.pack_forget()
        shop_frame.pack_forget()
        spin_button.pack(pady=20, padx=10)
        cost_to_spin_label.configure(text=f"Cost per spin: ${current_round[0]-1}")
        remaining_spins[0] = 10
        spins_remaining_label.configure(text=f"Spins remaining: {remaining_spins[0]}")
        rounds_label.configure(text=f"Round {current_round[0]}")

def mult_purchase(row_frames, row, column):
    continue_button.configure(state="normal")
    for frame in row_frames:
        frame.destroy()
    new_mult = mults[row][column] + 1
    mults[row][column] = new_mult
    print(mults)
    
    if new_mult > 2:
        old_label = mult_labels[(row, column)][0]
        old_label.destroy()
    
    custom_font = ctk.CTkFont(family="Arial", size=20, weight="bold")
    label = ctk.CTkLabel(canvas, width=50 * SF, height=10 * SF, text=f"❌ {new_mult}", font=custom_font, fg_color="lightsteelblue2", text_color="white")
    mult_labels[(row,column)] = [label, new_mult] 
    label.place(x=0 + column*50*SF, y=20 * SF + row*50*SF)
        
def buy_mult_click():
    if money[0] >= 5:
        money[0] -= 5
        money_label.configure(text=f"Money: ${money[0]}")
        continue_button.configure(state="disabled")
        row_frames = []
        for i in range(3):
            row_frame = ctk.CTkFrame(canvas, width=150*SF)
            row_frames.append(row_frame)
            row_frame.pack_propagate(False)
            row_frame.pack()
            for j in range(3):
                button = ctk.CTkButton(row_frame, width=50*SF, height=100*SF, command=lambda i=i, j=j: mult_purchase(row_frames, i, j))
                button.pack(side="left", anchor="nw")
    else:
        buy_mult_button.configure(text="Not enough money!", state="disabled")
        win.after(1000, lambda: buy_mult_button.configure(text="Buy Mult \n $5", state="normal"))

def update_probabilities():
    for color, label in probability_labels.items():
        num_colors = colors.count(color)
        label.configure(text=f"{color} \n {num_colors/len(colors)*100:.1f}%")

def color_remove_click():
    if money[0] >= 50:
        if color_remove_button.cget("text") != "Remove":
            continue_button.configure(state="disabled")
            color_remove_options.pack(side="bottom", pady=5)
            color_remove_button.configure(text="Remove")
        elif color_remove_options.get() == "Select a Color":
            color_remove_button.configure(text="Select Color!", state="disabled")
            win.after(1000, lambda: color_remove_button.configure(text="Remove", state="normal"))
        else:
            money[0] -= 50
            money_label.configure(text=f"Money: ${money[0]}")
            selected_color = color_remove_options.get()
            colors.remove(selected_color)
            update_probabilities()
            color_remove_options.configure(values = [color for color in colors])
            color_remove_options.set("Select a Color")
            color_remove_options.pack_forget()
            color_remove_button.configure(text="Remove a Color")
            continue_button.configure(state="normal")
            print(colors)
    else:
        color_remove_button.configure(text="Not enough money!", state="disabled")
        win.after(1000, lambda: color_remove_button.configure(text="Remove a Color \n $50", state="normal"))

def color_add_click():
    if money[0] >= 15:
        if color_add_button.cget("text") != "Add":
            continue_button.configure(state="disabled")
            color_add_options.pack(side="bottom", pady=5)
            color_add_button.configure(text="Add")
        elif color_add_options.get() == "Select a Color":
            color_add_button.configure(text="Select Color!", state="disabled")
            win.after(1000, lambda: color_add_button.configure(text="Add", state="normal"))
        else:
            money[0] -= 15
            money_label.configure(text=f"Money: ${money[0]}")
            selected_color = color_add_options.get()
            colors.append(selected_color)
            update_probabilities()
            color_add_options.set("Select a Color!")
            color_add_options.pack_forget()
            color_add_button.configure(text="Add a Color \n $15")
            continue_button.configure(state="normal")
            print(colors)
    else:
        color_add_button.configure(text="Not enough money!", state="disabled")
        win.after(1000, lambda: color_add_button.configure(text="Add a Color \n $15", state="normal"))
        
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
    title_frame = ctk.CTkFrame(start_frame, fg_color="transparent")
    title_text = ctk.CTkLabel(title_frame, text="Slot Machine Simulator", font=("Arial", 75, "bold"))
    subtitle_text = ctk.CTkLabel(title_frame, text="gambling is bad, but not if you aren't spending real money!", font=("Arial", 30))
    start_button = ctk.CTkButton(title_frame, text="Press to play", command=start_button_click)
    title_frame.pack(expand=True)
    title_text.pack(pady=10)
    subtitle_text.pack()
    start_button.pack(pady=40)
    

def create_spin_map():
    spin_map = []
    spin_column = []
    for i in range(3):
        for j in range(7):
            spin_column.append(((j+1)+(i*7), colors[j]))
        spin_map.append(spin_column)
        spin_column = []
    print(spin_map)
    return spin_map
    
def update_spin_map(spinning_reels, chosen_colors, count):
    spinning_reels = len(spinning_reels) // 7 # Will give a value of 3 2 or 1 depending on how many reels are still spinning
    count -= EXTRA_SPINS
    distance_travelled = count*100*SF
    
    if distance_travelled >= 0: # If on last spin, start changing the colors of stopping reel to what they should be
        last_rectangle = spin_map[3-spinning_reels].pop()
        random_color = chosen_colors[3-spinning_reels][6-count]
        canvas.itemconfig(spin_map[3-spinning_reels][-1][0], fill=random_color)
        spin_map[3-spinning_reels][-1] = (spin_map[3-spinning_reels][-1][0], random_color)
        spin_map[3-spinning_reels].insert(0, last_rectangle)
        # Randomly change the colors for every reel that's still spinning
        for column in range(2, 3-spinning_reels, -1):
            last_rectangle = spin_map[column].pop()
            random_color = colors[random.randint(0,len(colors)-1)]
            canvas.itemconfig(spin_map[column][-1][0], fill=random_color)
            spin_map[column][-1] = (spin_map[column][-1][0], random_color)
            spin_map[column].insert(0, last_rectangle)
    else: # Otherwise, randomly select colors for every spinning reel
        for column in range(2, 2-spinning_reels, -1):
            last_rectangle = spin_map[column].pop()
            random_color = colors[random.randint(0,len(colors)-1)]
            canvas.itemconfig(spin_map[column][-1][0], fill=random_color)
            spin_map[column][-1] = (spin_map[column][-1][0], random_color)
            spin_map[column].insert(0, last_rectangle)
            
    return spin_map

def restart_game():
    game_frame.pack_forget()
    start_frame.pack(expand=True, fill="both")
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
    money_label.configure(text=f"Money: ${money[0]}")
    spins_remaining_label.configure(text=f"Spins remaining: {remaining_spins[0]}")
    rounds_label.configure(text=f"Round {current_round[0]}")
    shop_frame.pack_forget()
    continue_button.configure(state="normal")
    continue_button.pack_forget()
    spin_button.pack()
    for mult_label in mult_labels.values():
        mult_label[0].destroy()
    mult_labels.clear()
    update_probabilities()

def game_over(start_time, last_time, x=-600):
    wheight, wwidth = win.winfo_height(), win.winfo_width()
    current_time = time.perf_counter()
    elapsed = (current_time-start_time)/1.5
    dt = current_time - last_time
    if elapsed > 1:
        elapsed = 1
        win.after(500, restart_game)
        win.after(500, lambda: game_over_label.place(x=-600, y=wheight//4))
    ease_velocity = ease_in_out_derivative(elapsed) * (wwidth / 2.5)
    move_amount = (ease_velocity*dt)/1.5
    
    game_over_label.place(x=x+move_amount, y=wheight//4)
    
    if elapsed < 1:
        win.after(10, game_over, start_time, current_time, x+move_amount)

def spin(chosen_colors, start_time, last_time, reel = 1, count = 0, total_moved = 0): 
    deltaT = 4
    DURATION = 0.05 * (reel-3) * (reel-3) + 1
    
    # Puts all the currently spinning reels (determined by the reel parameter) in a list
    reels = [canvas.find_withtag("reel1"), canvas.find_withtag("reel2"), canvas.find_withtag("reel3")]
    spinning_reels = []
    for i in range(4 - reel):
        spinning_reels += reels[2-i]
    
    current_time = time.perf_counter()
    elapsed = (current_time-start_time)/DURATION # (duration)
    dt = current_time - last_time
    if elapsed > 1:
        total_moved = 100*SF
        elapsed = 1
    ease_velocity = ease_in_out_derivative(elapsed) * MOVE_AMOUNT
    move_amount = (ease_velocity*dt)/DURATION
    
    # Moves all rectangles in spinning_reels. Moves rectangles back up to the top if reaching the edge of the canvas
    for rectangle in spinning_reels:
        x1, y1, x2, y2 = canvas.coords(rectangle)
        canvas.move(rectangle, 0, move_amount)
        if y2 >= 700*SF:
            canvas.move(rectangle, 0, -700*SF)
    
    total_moved += move_amount
    if total_moved >= 100*SF: # The width of a rectangle
        update_spin_map(spinning_reels, chosen_colors, count)
        # We check if each column matches chosen_colors one by one depending on the reel parameter
        current_column = []
        for i in spin_map[reel - 1]:
            current_column.append(i[1])
        if count != 7+EXTRA_SPINS:
            win.after(deltaT, spin, chosen_colors, start_time, current_time, reel, count + 1)
        else:
            for rectangle in reels[reel - 1]: # Nudges all rectangles in current reel to exact position
                x1, y1, x2, y2 = canvas.coords(rectangle)
                canvas.coords(rectangle, x1, (round(y1 / (100*SF)) * 100*SF), x2, (round(y2 / (100*SF)) * 100*SF))
            if(reel < 3): # Continues spinning excluding the current column if not all reels finished spinning
                win.after(deltaT, spin, chosen_colors, current_time, current_time, reel+1)
            else:
                animate_paylines()
    else:
        win.after(deltaT, spin, chosen_colors, start_time, current_time, reel, count, total_moved)

# All the UI elements
# I wish I could put these in a function :\ (I regret not making this with OOP)

start_frame = ctk.CTkFrame(win)
start_frame.pack(expand=True, fill="both")
create_start_screen()

game_frame = ctk.CTkFrame(win)
#game_frame.pack(expand=True, fill="both")

# Left UI
slot_frame = ctk.CTkFrame(game_frame, fg_color="transparent")
canvas = tk.Canvas(slot_frame, width=300*SF, height=300*SF, bg="black", highlightthickness=0)
le_slot_image = Image.open("Le Slot.png")
le_slot = ctk.CTkImage(le_slot_image, size=(125*SF, 21*SF))
slot_title = ctk.CTkLabel(slot_frame, image=le_slot, text="")
slot_frame.pack(side="left", padx=100, expand=True)
control_frame = ctk.CTkFrame(game_frame, width=50*SF, height=300*SF)
control_frame.pack_propagate(False)
control_frame.pack(side="right", fill="both", expand=True)
slot_title.pack(pady=10)
canvas.pack(pady=20)
create_spinner()
spin_map = create_spin_map()

# Right UI
money_label = ctk.CTkLabel(control_frame, width = 100, height=50, text=f"Money: ${money[0]}")
cost_to_spin_label = ctk.CTkLabel(control_frame, width=100, height=50, text="Cost per spin: $0")
rounds_label = ctk.CTkLabel(control_frame, width = 100, height=50, text="Round 1")
spins_remaining_label = ctk.CTkLabel(control_frame, width=100, height=50, text=f"Spins remaining: {remaining_spins[0]}")
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
probability_labels_frame.pack(side="bottom", fill="x", pady=10)

for color in colors:
    probability_labels[f"{color}"] = ctk.CTkLabel(probability_labels_frame, text=f"{color} \n 14.3%", text_color=f"{color}")
    probability_labels[f"{color}"].pack(side="left", fill="x", expand=True)

print(probability_labels)

game_over_font = ctk.CTkFont(family="Arial", size=100, weight="bold")
game_over_label = ctk.CTkLabel(win, text="You Lost :(", font=game_over_font, text_color="red")

# Known bug: money doesn't subtract until you press add/remove a color button twice, causing issues if you press it once with enough money and don't have enough money on the second press
# -> Can buy perma free spins per round to a max of 5(?) out of total 10 spins
# -> Maybe also increase value of line pay (rn its $10 can upgrade to $20+)

shop_frame.pack_forget()
win.mainloop()