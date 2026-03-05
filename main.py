import tkinter as tk
from tkinter import ttk
import os

class RoboCupTacticalBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("RoboCup Junior - Symmetrical Tactical Builder")
        self.root.geometry("1600x850")
        self.step_count = 0
        self.steps = [] 
        self.last_x, self.last_y = 0, 0

        # Goal State (True = Blue Top, False = Yellow Top)
        self.blue_on_top = True
        
        # --- LEFT SIDE: FIELD MAP ---
        self.field_frame = tk.Frame(root, bg="#222")
        self.field_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.pos_label = tk.Label(self.field_frame, text="X=0, Y=0", fg="#00FF00", bg="#222", font=("Courier", 12, "bold"))
        self.pos_label.pack(pady=5)

        self.canvas = tk.Canvas(self.field_frame, width=364, height=486, bg="#006400", highlightthickness=2, highlightbackground="white")
        self.canvas.pack(pady=5)
        self.canvas.create_line(24, 24, 340, 24, fill="white")
        self.canvas.create_line(24, 462, 340, 462, fill="white")
        self.canvas.create_line(24, 24, 24, 462, fill="white")
        self.canvas.create_line(340, 24, 340, 462, fill="white")
        self.canvas.bind("<Button-1>", self.on_field_click)

        # --- RIGHT SIDE: STEP LIST ---
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        self.control_bar = tk.Frame(self.right_frame)
        self.control_bar.pack(fill=tk.X, pady=5)
        
        tk.Button(self.control_bar, text="+ ADD TASK", command=self.add_sentence, bg="#28a745", fg="white", font=("Arial", 11, "bold"), padx=20).pack(side=tk.LEFT)
        tk.Button(self.control_bar, text="FLASH TO ROBOT", command=self.generate_logic, bg="#007bff", fg="white", font=("Arial", 11, "bold"), padx=20).pack(side=tk.RIGHT)
        # SWAP BUTTON for Goals
        self.draw_field_markings()
        tk.Button(self.field_frame, text="SWAP GOALS ⇄", command=self.swap_goals, bg="#555", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=5)
        
        self.container = tk.Canvas(self.right_frame)
        self.scroll_frame = tk.Frame(self.container)
        self.scroller = tk.Scrollbar(self.right_frame, orient="vertical", command=self.container.yview)
        self.container.configure(yscrollcommand=self.scroller.set)

        self.scroller.pack(side=tk.RIGHT, fill=tk.Y)
        self.container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.container_window = self.container.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        
        self.scroll_frame.bind("<Configure>", lambda e: self.container.configure(scrollregion=self.container.bbox("all")))
        self.container.bind("<Configure>", lambda e: self.container.itemconfig(self.container_window, width=e.width))
    
    def draw_field_markings(self):
        self.canvas.delete("field_base")
        
        # Define Goal Positions based on state
        top_color = "blue" if self.blue_on_top else "yellow"
        bot_color = "yellow" if self.blue_on_top else "blue"

        # Top Goal Rectangle
        self.canvas.create_rectangle(122, 0, 242, 24, outline=top_color, fill=top_color, tags="field_base")
        # Bottom Goal Rectangle
        self.canvas.create_rectangle(122, 462, 242, 486, outline=bot_color, fill=bot_color, tags="field_base")

    def swap_goals(self):
        """Switches the positions of the blue and yellow goal rectangles."""
        self.blue_on_top = not self.blue_on_top
        self.draw_field_markings()
        # Keep the crosshair and axis lines visible after swap
        self.refresh_axis_lines()

    def on_field_click(self, event):
        self.last_x = (event.x - 182) * 0.5
        self.last_y = (243 - event.y) * 0.5
        self.draw_target_visuals(event.x, event.y)
        self.pos_label.config(text=f"X={self.last_x}, Y={self.last_y}")

    def draw_target_visuals(self, cx, cy):
        """Draws a large crosshair for better alignment."""
        self.canvas.delete("pt")
        # Universal Crosshair
        self.canvas.create_line(cx-100, cy, cx+100, cy, fill="yellow", tags="pt", width=1)
        self.canvas.create_line(cx, cy-100, cx, cy+100, fill="yellow", tags="pt", width=1)
        # Accurate Center
        self.canvas.create_oval(cx-22, cy-22, cx+22, cy+22, outline="red", width=2, tags="pt")
        self.canvas.create_oval(cx-1, cy-1, cx+1, cy+1, fill="white", tags="pt")
        self.refresh_axis_lines()

    def refresh_axis_lines(self):
        self.canvas.delete("axis_line")
        for s in self.steps:
            target_val = s['target'].get()
            try:
                if target_val == "Axis X":
                    x_pos = int(s['x_ent'].get()) + 150
                    self.canvas.create_line(x_pos, 0, x_pos, 450, fill="cyan", dash=(4, 4), tags="axis_line")
                elif target_val == "Axis Y":
                    y_pos = 225 - int(s['y_ent'].get())
                    self.canvas.create_line(0, y_pos, 300, y_pos, fill="cyan", dash=(4, 4), tags="axis_line")
            except: pass

    def create_condition_block(self, parent, label_text):
        """Standardized Variable | Op | Val block."""
        frame = tk.Frame(parent)
        frame.pack(side=tk.LEFT, padx=15)
        tk.Label(frame, text=label_text, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        var = ttk.Combobox(frame, values=["Ball.Dist", "Goal.Dist", "Timer", "Line.Value", "None"], width=12)
        var.set("None")
        var.pack(side=tk.LEFT, padx=2)
        op = ttk.Combobox(frame, values=[">", "<", "==", "!="], width=4)
        op.set(">")
        op.pack(side=tk.LEFT, padx=2)
        val = tk.Entry(frame, width=7)
        val.insert(0, "0")
        val.pack(side=tk.LEFT, padx=2)
        return var, op, val

    def add_sentence(self):
        self.step_count += 1
        step_id = self.step_count
        row_frame = tk.Frame(self.scroll_frame, pady=15, padx=10, highlightbackground="#555", highlightthickness=2)
        row_frame.pack(fill=tk.X, pady=8, padx=5)

        # --- TOP ROW: ACTION (GRID-BASED) ---
        top_row = tk.Frame(row_frame)
        top_row.pack(fill=tk.X)

        tk.Label(top_row, text=f"STEP {step_id}:", font=("Arial", 11, "bold"), fg="#007bff").grid(row=0, column=0, padx=5)
        tk.Label(top_row, text="Do").grid(row=0, column=1)
        move = ttk.Combobox(top_row, values=["Linear", "Curved", "Stay"], width=10)
        move.set("Linear"); move.grid(row=0, column=2, padx=5)

        tk.Label(top_row, text="at Speed").grid(row=0, column=3)
        speed = tk.Entry(top_row, width=5); speed.insert(0, "10"); speed.grid(row=0, column=4, padx=5)
        
        tk.Label(top_row, text="To Target").grid(row=0, column=5)
        target = ttk.Combobox(top_row, values=["Position(X,Y)", "Axis X", "Axis Y", "Ball", "Goal"], width=15)
        target.set("Position(X,Y)"); target.grid(row=0, column=6, padx=5)

        # Reserved Slots (Columns 7 and 8)
        x_ent = tk.Entry(top_row, width=6, font=("Arial", 10, "bold"), fg="red");
        y_ent = tk.Entry(top_row, width=6, font=("Arial", 10, "bold"), fg="red");

        tk.Label(top_row, text="& Rotation").grid(row=0, column=9, padx=5)
        rot_m = ttk.Combobox(top_row, values=["Degree", "Face Ball", "Face Green Goal", "Face Yellow Goal", "Spin"], width=12)
        rot_m.set("Face Ball"); rot_m.grid(row=0, column=10, padx=2)
        rot_v = tk.Entry(top_row, width=5); rot_v.insert(0, "0"); rot_v.grid(row=0, column=11, padx=2)

        def update_vis(e=None):
            # 1. Hide both first to reset the "reserved" area
            x_ent.grid_forget()
            y_ent.grid_forget()
            
            mode = target.get()
            
            # 2. Handle Position Logic
            if mode == "Position(X,Y)":
                x_ent.grid(row=0, column=7, padx=2)
                y_ent.grid(row=0, column=8, padx=2)
                # Clear and Update X
                x_ent.delete(0, tk.END)
                x_ent.insert(0, str(self.last_x))
                # Clear and Update Y
                y_ent.delete(0, tk.END)
                y_ent.insert(0, str(self.last_y))
                
            # 3. Handle Axis X Logic
            elif mode == "Axis X":
                x_ent.grid(row=0, column=7, padx=2)
                x_ent.delete(0, tk.END)
                x_ent.insert(0, str(self.last_x))
                
            # 4. Handle Axis Y Logic
            elif mode == "Axis Y":
                y_ent.grid(row=0, column=8, padx=2)
                y_ent.delete(0, tk.END)
                y_ent.insert(0, str(self.last_y))
            
            self.refresh_axis_lines()

        target.bind("<<ComboboxSelected>>", update_vis); update_vis()
        
        tk.Button(top_row, text="✖ REMOVE", bg="#dc3545", fg="white", font=("Arial", 8, "bold"), 
                  command=lambda: self.remove_step(row_frame, step_id)).grid(row=0, column=12, padx=20)

        # --- BOTTOM ROW: LOGIC ---
        bot_row = tk.Frame(row_frame, pady=5)
        bot_row.pack(fill=tk.X)

        w_var, w_op, w_val = self.create_condition_block(bot_row, "WHILE")
        u_var, u_op, u_val = self.create_condition_block(bot_row, "UNTIL")

        tk.Label(bot_row, text="THEN", font=("Arial", 10, "bold"), fg="#28a745").pack(side=tk.LEFT, padx=10)
        res = ttk.Combobox(bot_row, values=["Next Step", "End Mission"], width=12); res.set("Next Step"); res.pack(side=tk.LEFT)

        self.steps.append({
            'id': step_id, 'target': target, 'x_ent': x_ent, 'y_ent': y_ent,
            'move': move, 'speed': speed, 'rot_m': rot_m, 'rot_v': rot_v,
            'w_var': w_var, 'w_op': w_op, 'w_val': w_val,
            'u_var': u_var, 'u_op': u_op, 'u_val': u_val, 'res': res
        })

    def remove_step(self, frame, s_id):
        frame.destroy()
        self.steps = [s for s in self.steps if s['id'] != s_id]
        self.refresh_axis_lines()

    def generate_logic(self):
        with open("robot_mission.ino", "w") as f:
            f.write("#include <Robot.h>\nvoid setup(){ Robot_Init(); }\nvoid loop(){\n")
            for s in self.steps:
                f.write(f"  // Step {s['id']}\n")
                f.write(f"  while(Check('{s['w_var'].get()}', '{s['w_op'].get()}', {s['w_val'].get()}) && \n")
                f.write(f"        !Check('{s['u_var'].get()}', '{s['u_op'].get()}', {s['u_val'].get()})) {{\n")
                f.write(f"    ExecuteMove('{s['target'].get()}', {s['speed'].get()}, {s['x_ent'].get()}, {s['y_ent'].get()});\n")
                f.write(f"    UpdateRotation('{s['rot_m'].get()}', {s['rot_v'].get()});\n")
                f.write(f"  }}\n")
            f.write("  Stop(); while(1);\n}")
        print("C++ Logic Saved to robot_mission.ino")

if __name__ == "__main__":
    root = tk.Tk()
    app = RoboCupTacticalBoard(root)
    root.mainloop()
