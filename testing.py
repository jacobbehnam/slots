import tkinter as tk
import time

# Easing function for non-linear animation (ease-in-out example)
def ease_in_out(t):
    # Derivative of Bezier curve
    return 6*t*(1-t)

# Recursive animation function
def animate(spinning_reels, canvas, start_time, last_time, duration, total_moved, last_milestone):
    current_time = time.perf_counter()
    elapsed = (current_time - start_time) / duration
    if elapsed > 1:
        elapsed = 1  # Cap at 1
    
    dt = current_time - last_time
    
    # To get displacement, we need to integrate velocity with respect to time
    # We use the derivative of the Bezier curve function to get the velocity at a point in time dt
    # Since the integral of the derivative of the Bezier curve function on [0,1] is 1,
    # multiplying by 350 makes the integral/displacement 350 which is the net pixels the rectangles are moved
    eased_progress = ease_in_out(elapsed)  # Apply derivative of easing function to get velocity
    normalized_velocity = eased_progress * 350 
    move_amount = normalized_velocity*dt  # Calculate eased movement

    # Update positions and track total distance moved
    for rectangle in spinning_reels:
        canvas.move(rectangle, 0, move_amount)
        x1, y1, x2, y2 = canvas.coords(rectangle)
        if y2 >= 350:
            canvas.move(rectangle, 0, -350)

    total_moved += move_amount
    
    print(total_moved - last_milestone)
    # Trigger events for every 50 pixels moved
    if total_moved - last_milestone >= 50:
        last_milestone += 50
        print(f"Reached {last_milestone} pixels moved!")  # Replace with your event logic

    # Continue animation if not finished
    if elapsed < 1:
        canvas.after(10, animate, spinning_reels, canvas, start_time, current_time, duration, total_moved, last_milestone)

# Example usage
root = tk.Tk()
canvas = tk.Canvas(root, width=400, height=400, bg="white")
canvas.pack()

# Create some rectangles to animate
spinning_reels = [
    canvas.create_rectangle(50, 50, 100, 100, fill="red"),
    canvas.create_rectangle(150, 50, 200, 100, fill="green"),
    canvas.create_rectangle(250, 50, 300, 100, fill="blue"),
]

MOVE_AMOUNT = 100  # Base movement amount per frame
ANIMATION_DURATION = 2  # Duration of the animation in seconds
START_TIME = time.perf_counter()

# Start the animation
animate(spinning_reels, canvas, START_TIME, START_TIME, ANIMATION_DURATION, 0, 0)

root.mainloop()