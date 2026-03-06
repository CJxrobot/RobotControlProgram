import tkinter as tk
from tkinter import ttk
import subprocess
import os

class RoboCupTacticalBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("RoboCup Junior - Pro Tactical Builder")
        self.root.geometry("1200x600")
        self.step_count = 0
        self.steps = [] 
        self.last_x, self.last_y = 0.0, 0.0
        self.blue_on_top = True

        # --- LEFT SIDE: FIELD MAP ---
        self.field_frame = tk.Frame(root, bg="#222")
        self.field_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.pos_label = tk.Label(self.field_frame, text="X=0.0, Y=0.0", fg="#00FF00", bg="#222", font=("Courier", 12, "bold"))
        self.pos_label.pack(pady=5)

        # Canvas matching your 364x486 resolution
        self.canvas = tk.Canvas(self.field_frame, width=364, height=486, bg="#006400", highlightthickness=2, highlightbackground="white")
        self.canvas.pack(pady=5)
        self.draw_field_markings()
        self.canvas.bind("<Button-1>", self.on_field_click)

        tk.Button(self.field_frame, text="SWAP GOALS ⇄", command=self.swap_goals, bg="#444", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=5)

        # --- RIGHT SIDE: STEP LIST ---
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        self.control_bar = tk.Frame(self.right_frame)
        self.control_bar.pack(fill=tk.X, pady=5)
        
        tk.Button(self.control_bar, text="+ ADD TASK", command=self.add_sentence, bg="#28a745", fg="white", font=("Arial", 11, "bold"), padx=20).pack(side=tk.LEFT)
        tk.Button(self.control_bar, text="FLASH", command=self.flash_robot, bg="#ff00aa", fg="white", font=("Arial", 11, "bold"), padx=20).pack(side=tk.RIGHT)
        tk.Button(self.control_bar, text="BUILD", command=self.build_robot, bg="#007bff", fg="white", font=("Arial", 11, "bold"), padx=20).pack(side=tk.RIGHT)

        # Scrollable container for steps
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
        # Field Boundary
        self.canvas.create_rectangle(24, 24, 340, 462, outline="white", width=2, tags="field_base") 
        
        top_c = "blue" if self.blue_on_top else "yellow"
        bot_c = "yellow" if self.blue_on_top else "blue"
        
        # Goals (Solid Fill)
        self.canvas.create_rectangle(122, 0, 242, 24, fill=top_c, outline="white", tags="field_base")
        self.canvas.create_rectangle(122, 462, 242, 486, fill=bot_c, outline="white", tags="field_base")
        # Midline
        self.canvas.create_line(24, 243, 340, 243, fill="white", dash=(5,5), tags="field_base")

    def swap_goals(self):
        self.blue_on_top = not self.blue_on_top
        self.draw_field_markings()

    def on_field_click(self, event):
        # Coordinates: Center is (182, 243). Scaled by 0.5.
        self.last_x = round((event.x - 182) * 0.5, 1)
        self.last_y = round((243 - event.y) * 0.5, 1)
        self.draw_target_visuals(event.x, event.y)
        self.pos_label.config(text=f"X={self.last_x}, Y={self.last_y}")

    def draw_target_visuals(self, cx, cy):
        self.canvas.delete("pt")
        self.canvas.create_line(cx-100, cy, cx+100, cy, fill="yellow", tags="pt")
        self.canvas.create_line(cx, cy-100, cx, cy+100, fill="yellow", tags="pt")
        self.canvas.create_oval(cx-8, cy-8, cx+8, cy+8, outline="red", width=2, tags="pt")

    def create_multi_cond_section(self, parent, title):
        section_frame = tk.LabelFrame(parent, text=title, font=("Arial", 9, "bold"))
        section_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        cond_rows = []
        rows_container = tk.Frame(section_frame)
        rows_container.pack(fill=tk.BOTH)

        def add_row():
            row = tk.Frame(rows_container)
            row.pack(fill=tk.X, pady=1)
            
            logic = ttk.Combobox(row, values=["&&", "||"], width=3)
            if len(cond_rows) > 0:
                logic.set("&&")
                logic.pack(side=tk.LEFT)
            else:
                logic.set("") # First condition row has no operator
            
            var = ttk.Combobox(row, values=["Ball.Dist", "Blue.Dist", "Yellow.Dist", "Timer", "Line.Exist", "None"], width=10)
            var.set("None"); var.pack(side=tk.LEFT, padx=2)
            
            op = ttk.Combobox(row, values=[">", "<", "==", "!="], width=3)
            op.set(">"); op.pack(side=tk.LEFT)
            
            val = tk.Entry(row, width=5); val.insert(0, "0"); val.pack(side=tk.LEFT, padx=2)
            cond_rows.append({'logic': logic, 'var': var, 'op': op, 'val': val})

        tk.Button(section_frame, text="+", command=add_row, width=2, bg="#eee").pack(anchor="ne")
        add_row()
        return cond_rows

    def add_sentence(self):
        self.step_count += 1
        step_id = self.step_count
        row_frame = tk.Frame(self.scroll_frame, pady=10, highlightbackground="#555", highlightthickness=1)
        row_frame.pack(fill=tk.X, pady=5, padx=5)

        # --- Top Row: Movement & Rotation Settings ---
        top = tk.Frame(row_frame)
        top.pack(fill=tk.X, padx=5)
        
        tk.Label(top, text=f"STEP {step_id}", font=("Arial", 10, "bold"), fg="#007bff").pack(side=tk.LEFT)
        
        tk.Label(top, text=" Style:").pack(side=tk.LEFT)
        move_style = ttk.Combobox(top, values=["Linear", "Curved", "Stay"], width=8)
        move_style.set("Linear"); move_style.pack(side=tk.LEFT, padx=2)

        tk.Label(top, text=" Target:").pack(side=tk.LEFT)
        target = ttk.Combobox(top, values=["Position(X,Y)", "Axis X", "Axis Y", "Ball", "Blue Goal", "Yellow Goal", "Stay"], width=12)
        target.set("Position(X,Y)"); target.pack(side=tk.LEFT, padx=2)
        
        # Coordinate entries (Managed by update_vis)
        x_ent = tk.Entry(top, width=6, fg="red", font=("Arial", 9, "bold"))
        y_ent = tk.Entry(top, width=6, fg="red", font=("Arial", 9, "bold"))
        
        # Rest of basic parameters
        tk.Label(top, text=" Spd:").pack(side=tk.LEFT)
        speed = tk.Entry(top, width=4); speed.insert(0, "10"); speed.pack(side=tk.LEFT)
        
        tk.Label(top, text=" Rot:").pack(side=tk.LEFT)
        rot_m = ttk.Combobox(top, values=["Degree", "Face Ball", "Face Blue", "Face Yellow", "Spin"], width=10)
        rot_m.set("Face Ball"); rot_m.pack(side=tk.LEFT)
        rot_v = tk.Entry(top, width=4); rot_v.insert(0, "90"); rot_v.pack(side=tk.LEFT)

        def update_vis(e=None):
            """Restores Dynamic Visibility for X/Y coordinates."""
            # Clear them from view first
            x_ent.pack_forget()
            y_ent.pack_forget()
            
            mode = target.get()
            # Repack between 'Target' and 'Spd'
            if mode == "Position(X,Y)":
                x_ent.pack(after=target, side=tk.LEFT, padx=1)
                y_ent.pack(after=x_ent, side=tk.LEFT, padx=1)
                x_ent.delete(0, tk.END); x_ent.insert(0, str(self.last_x))
                y_ent.delete(0, tk.END); y_ent.insert(0, str(self.last_y))
            elif mode == "Axis X":
                x_ent.pack(after=target, side=tk.LEFT, padx=1)
                x_ent.delete(0, tk.END); x_ent.insert(0, str(self.last_x))
            elif mode == "Axis Y":
                y_ent.pack(after=target, side=tk.LEFT, padx=1)
                y_ent.delete(0, tk.END); y_ent.insert(0, str(self.last_y))

        target.bind("<<ComboboxSelected>>", update_vis)
        update_vis() # Initial run

        tk.Button(top, text="✖", bg="#dc3545", fg="white", font=("Arial", 8, "bold"), command=lambda: row_frame.destroy()).pack(side=tk.RIGHT)

        # --- Bottom Row: Complex Logic Sections ---
        bot = tk.Frame(row_frame)
        bot.pack(fill=tk.X, pady=5)
        w_conds = self.create_multi_cond_section(bot, "WHILE (Stay in loop if...)")
        u_conds = self.create_multi_cond_section(bot, "UNTIL (Break loop if...)")

        self.steps.append({
            'id': step_id, 'move': move_style, 'target': target, 'x_ent': x_ent, 'y_ent': y_ent,
            'speed': speed, 'rot_m': rot_m, 'rot_v': rot_v,
            'w_conds': w_conds, 'u_conds': u_conds, 'frame': row_frame
        })

    def generate_logic(self):
        # Enum Mappings
        s_map = {"None": "S_NONE", "Ball.Dist": "S_BALL_DIST", "Blue.Dist": "S_BLUE_DIST", "Yellow.Dist": "S_YELLOW_DIST", "Timer": "S_TIMER", "Line.Exist": "S_LINE_EXIST"}
        m_map = {"Position(X,Y)": "M_POS_XY", "Axis X": "M_AXIS_X", "Axis Y": "M_AXIS_Y", "Ball": "M_BALL", "Blue Goal": "M_BLUE_GOAL", "Yellow Goal": "M_YELLOW_GOAL", "Stay": "M_STAY"}
        style_map = {"Linear": "STYLE_LINEAR", "Curved": "STYLE_CURVED", "Stay": "STYLE_STAY"}
        rot_map = {"Face Ball": "R_FACE_BALL", "Face Blue": "R_FACE_BLUE", "Face Yellow": "R_FACE_YELLOW", "Degree": "R_DEGREE", "Spin": "R_SPIN"}
        file_path = r"Teensy4.1-RCJ2026\src\main.cpp"

        def build_expr(conds):
            parts = []
            for i, c in enumerate(conds):
                var = s_map.get(c['var'].get(), "S_NONE")
                if var == "S_NONE" and i == 0: return "true"
                logic = f" {c['logic'].get()} " if i > 0 and c['logic'].get() else ""
                parts.append(f"{logic}Check({var}, '{c['op'].get()}', {c['val'].get()})")
            return "".join(parts) if parts else "true"

        with open(file_path, "w") as f:
            f.write("#include <Robot.h>\n#include \"RobotConstants.h\"\n\nvoid setup() {\n  Robot_Init();\n}\n\nvoid loop() {\n")
            for s in self.steps:
                if not s['frame'].winfo_exists(): continue
                while_expr = build_expr(s['w_conds'])
                until_expr = build_expr(s['u_conds'])
                
                f.write(f"  // STEP {s['id']}\n")
                f.write(f"  while({while_expr}){{\n")
                f.write("    UpdateSensors();\n")
                # Ensure coordinate values are safe
                x_val = s['x_ent'].get() if s['x_ent'].winfo_ismapped() else "0"
                y_val = s['y_ent'].get() if s['y_ent'].winfo_ismapped() else "0"
                
                f.write(f"    ExecuteMove({style_map[s['move'].get()]}, {m_map[s['target'].get()]}, {s['speed'].get()}, {x_val}, {y_val});\n")
                f.write(f"    UpdateRotation({rot_map[s['rot_m'].get()]}, {s['rot_v'].get()});\n")
                f.write(f"    if({until_expr}) break;\n")
                f.write("  }\n\n")
            f.write("  Stop_Robot();\n  while(1);\n}\n")
        print("Mission code generated successfully!")


    def build_robot(self):
        """Runs the PlatformIO build command using the specific environment path."""
        self.generate_logic() # First, create the main.cpp
        print("Starting Build...")
        
        # 1. Get the user profile path safely
        user_profile = os.environ.get('USERPROFILE')
        # 2. Build the full path to the pio.exe
        pio_exe = os.path.join(user_profile, r".platformio\penv\Scripts\platformio.exe")
        
        # 3. Format the command: & "C:\Users\Name\...\platformio.exe" run
        # Note the double quotes around the executable path to handle spaces in usernames
        ps_command = f'& "{pio_exe}" run'
        
        try:
            # We call powershell and pass the command string
            # cwd="Teensy4.1-RCJ2026" ensures we are in the project folder
            subprocess.run(["powershell", "-Command", ps_command], 
                           cwd="Teensy4.1-RCJ2026", 
                           check=True)
            print("--- BUILD SUCCESSFUL ---")
        except subprocess.CalledProcessError as e:
            print(f"--- BUILD FAILED ---\nExit Code: {e.returncode}")
        except Exception as e:
            print(f"--- SYSTEM ERROR ---\n{e}")

    def flash_robot(self):
        """Runs the PlatformIO upload command."""
        self.generate_logic()
        print("Starting Flash (Upload)...")
        
        user_profile = os.environ.get('USERPROFILE')
        pio_exe = os.path.join(user_profile, r".platformio\penv\Scripts\platformio.exe")
        
        # Added --target upload
        ps_command = f'& "{pio_exe}" run --target upload'
        
        try:
            subprocess.run(["powershell", "-Command", ps_command], 
                           cwd="Teensy4.1-RCJ2026", 
                           check=True)
            print("--- FLASH SUCCESSFUL ---")
        except subprocess.CalledProcessError as e:
            print(f"--- FLASH FAILED ---\nExit Code: {e.returncode}")
if __name__ == "__main__":
    root = tk.Tk()
    app = RoboCupTacticalBoard(root)
    root.mainloop()