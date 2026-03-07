import tkinter as tk
from tkinter import ttk
import subprocess
import os

class RoboCupTacticalBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("RoboCup Junior - Teensy 4.1 Pro Builder")
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
        self.canvas.create_rectangle(24, 24, 340, 462, outline="white", width=2, tags="field_base") 
        top_c = "blue" if self.blue_on_top else "yellow"
        bot_c = "yellow" if self.blue_on_top else "blue"
        self.canvas.create_rectangle(122, 0, 242, 24, fill=top_c, outline="white", tags="field_base")
        self.canvas.create_rectangle(122, 462, 242, 486, fill=bot_c, outline="white", tags="field_base")
        self.canvas.create_line(24, 243, 340, 243, fill="white", dash=(5,5), tags="field_base")

    def swap_goals(self):
        self.blue_on_top = not self.blue_on_top
        self.draw_field_markings()

    def on_field_click(self, event):
        self.last_x = round((event.x - 182) * 0.5, 1)
        self.last_y = round((243 - event.y) * 0.5, 1)
        self.draw_target_visuals(event.x, event.y)
        self.pos_label.config(text=f"X={self.last_x}, Y={self.last_y}")
        for s in self.steps:
            if s['frame'].winfo_exists():
                s['update_vis_func']()

    def draw_target_visuals(self, cx, cy):
        self.canvas.delete("pt")
        self.canvas.create_line(cx-10, cy, cx+10, cy, fill="yellow", tags="pt")
        self.canvas.create_line(cx, cy-10, cx, cy+10, fill="yellow", tags="pt")
        self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, outline="red", width=2, tags="pt")

    def create_multi_cond_section(self, parent, title):
        section_frame = tk.LabelFrame(parent, text=title, font=("Arial", 8, "bold"))
        section_frame.pack(side=tk.LEFT, padx=2, fill=tk.BOTH, expand=True)
        cond_rows = []
        rows_container = tk.Frame(section_frame)
        rows_container.pack(fill=tk.BOTH)

        def add_row():
            row = tk.Frame(rows_container)
            row.pack(fill=tk.X)
            logic = ttk.Combobox(row, values=["&&", "||"], width=3)
            # Only show logic selector if it's NOT the first row
            if len(cond_rows) > 0:
                logic.set("&&")
                logic.pack(side=tk.LEFT)
            else:
                logic.set("") # Placeholder
            
            var = ttk.Combobox(row, values=["Ball.Dist", "Blue.Dist", "Yellow.Dist", "Timer", "Line.Exist", "None"], width=9)
            var.set("None"); var.pack(side=tk.LEFT, padx=1)
            op = ttk.Combobox(row, values=[">", "<", "==", "!="], width=3)
            op.set(">"); op.pack(side=tk.LEFT)
            val = tk.Entry(row, width=4); val.insert(0, "0"); val.pack(side=tk.LEFT, padx=1)
            cond_rows.append({'logic': logic, 'var': var, 'op': op, 'val': val})

        tk.Button(section_frame, text="+", command=add_row, font=("Arial", 7)).pack(anchor="ne")
        add_row()
        return cond_rows

    def add_sentence(self):
        self.step_count += 1
        step_id = self.step_count
        row_frame = tk.Frame(self.scroll_frame, pady=5, highlightbackground="#555", highlightthickness=1)
        row_frame.pack(fill=tk.X, pady=2, padx=5)

        top = tk.Frame(row_frame)
        top.pack(fill=tk.X, padx=5)
        tk.Label(top, text=f"S{step_id}", font=("Arial", 9, "bold"), fg="#007bff").pack(side=tk.LEFT)
        
        target = ttk.Combobox(top, values=["Degree Motion", "Vector Motion", "Move To(X,Y)", "Move Along X", "Move Along Y", "Stay"], width=13)
        target.set("Degree Motion"); target.pack(side=tk.LEFT, padx=2)
        
        vx_ent = tk.Entry(top, width=5, fg="blue", font=("Arial", 9, "bold"))
        vy_ent = tk.Entry(top, width=5, fg="blue", font=("Arial", 9, "bold"))
        px_ent = tk.Entry(top, width=5, fg="red", font=("Arial", 9, "bold"))
        py_ent = tk.Entry(top, width=5, fg="red", font=("Arial", 9, "bold"))
        mov_spd_lbl = tk.Label(top, text=" Spd:")
        mov_speed = tk.Entry(top, width=4); mov_speed.insert(0, "40")
        deg_lbl = tk.Label(top, text=" Deg:")
        deg_ent = tk.Entry(top, width=4); deg_ent.insert(0, "0")

        tk.Label(top, text="| Rot:").pack(side=tk.LEFT, padx=2)
        rot_m = ttk.Combobox(top, values=["Face Front", "Degree", "Face Ball", "Face Blue", "Face Yellow", "Spin"], width=10)
        rot_m.set("Face Front"); rot_m.pack(side=tk.LEFT)
        
        rot_val_lbl = tk.Label(top, text=" Deg:")
        rot_v = tk.Entry(top, width=4); rot_v.insert(0, "0")
        rot_spd_lbl = tk.Label(top, text=" R.Spd:")
        rot_spd = tk.Entry(top, width=4); rot_spd.insert(0, "30")

        def update_vis(e=None):
            for w in [vx_ent, vy_ent, px_ent, py_ent, mov_spd_lbl, mov_speed, deg_lbl, deg_ent, rot_val_lbl, rot_v, rot_spd_lbl, rot_spd]:
                w.pack_forget()

            m_mode, r_mode = target.get(), rot_m.get()

            # Movement Layouts
            if m_mode == "Vector Motion":
                vx_ent.pack(after=target, side=tk.LEFT, padx=1)
                vy_ent.pack(after=vx_ent, side=tk.LEFT, padx=1)
            elif m_mode == "Degree Motion":
                deg_lbl.pack(after=target, side=tk.LEFT); deg_ent.pack(after=deg_lbl, side=tk.LEFT)
                mov_spd_lbl.pack(after=deg_ent, side=tk.LEFT); mov_speed.pack(after=mov_spd_lbl, side=tk.LEFT)
            elif m_mode == "Move Along X":
                mov_spd_lbl.pack(after=target, side=tk.LEFT); mov_speed.pack(after=mov_spd_lbl, side=tk.LEFT)
                px_ent.pack(after=mov_speed, side=tk.LEFT, padx=1)
                px_ent.delete(0, tk.END); px_ent.insert(0, str(self.last_x))
            elif m_mode == "Move Along Y":
                mov_spd_lbl.pack(after=target, side=tk.LEFT); mov_speed.pack(after=mov_spd_lbl, side=tk.LEFT)
                py_ent.pack(after=mov_speed, side=tk.LEFT, padx=1)
                py_ent.delete(0, tk.END); py_ent.insert(0, str(self.last_y))
            elif m_mode == "Move To(X,Y)":
                px_ent.pack(after=target, side=tk.LEFT, padx=1)
                py_ent.pack(after=px_ent, side=tk.LEFT, padx=1)
                mov_spd_lbl.pack(after=py_ent, side=tk.LEFT); mov_speed.pack(after=mov_spd_lbl, side=tk.LEFT)
                px_ent.delete(0, tk.END); px_ent.insert(0, str(self.last_x))
                py_ent.delete(0, tk.END); py_ent.insert(0, str(self.last_y))

            # Rotation Layouts
            if r_mode == "Degree":
                rot_val_lbl.pack(after=rot_m, side=tk.LEFT); rot_v.pack(after=rot_val_lbl, side=tk.LEFT)
                rot_spd_lbl.pack(after=rot_v, side=tk.LEFT); rot_spd.pack(after=rot_spd_lbl, side=tk.LEFT)
            elif r_mode == "Face Front":
                rot_spd_lbl.pack(after=rot_m, side=tk.LEFT); rot_spd.pack(after=rot_spd_lbl, side=tk.LEFT)
            else: # Face modes or Spin
                rot_spd_lbl.pack(after=rot_m, side=tk.LEFT); rot_spd.pack(after=rot_spd_lbl, side=tk.LEFT)

        target.bind("<<ComboboxSelected>>", update_vis)
        rot_m.bind("<<ComboboxSelected>>", update_vis)
        update_vis()

        tk.Button(top, text="✖", bg="#dc3545", fg="white", font=("Arial", 8), command=lambda: row_frame.destroy()).pack(side=tk.RIGHT)

        bot = tk.Frame(row_frame)
        bot.pack(fill=tk.X, pady=2)
        w_conds = self.create_multi_cond_section(bot, "WHILE")
        u_conds = self.create_multi_cond_section(bot, "UNTIL")

        self.steps.append({
            'id': step_id, 'target': target, 'vx': vx_ent, 'vy': vy_ent, 
            'px': px_ent, 'py': py_ent, 'speed': mov_speed, 'deg_mov': deg_ent,
            'rot_m': rot_m, 'rot_v': rot_v, 'rot_spd': rot_spd, 
            'w_conds': w_conds, 'u_conds': u_conds, 'frame': row_frame,
            'update_vis_func': update_vis
        })

    def generate_logic(self):
        s_map = {"None": "S_NONE", "Ball.Dist": "S_BALL_DIST", "Blue.Dist": "S_BLUE_DIST", "Yellow.Dist": "S_YELLOW_DIST", "Timer": "S_TIMER", "Line.Exist": "S_LINE_EXIST"}
        rot_map = {"Face Front": "R_FACE_FRONT", "Face Ball": "R_FACE_BALL", "Face Blue": "R_FACE_BLUE", "Face Yellow": "R_FACE_YELLOW", "Degree": "R_DEGREE", "Spin": "R_SPIN"}
        file_path = r"Teensy4.1-RCJ2026\src\main.cpp"

        def build_expr(conds):
            # If logic combobox is packed (visible), use its value, otherwise it's just the first condition
            parts = []
            for i, c in enumerate(conds):
                if c['var'].get() == "None": continue
                l_op = c['logic'].get() if (c['logic'].winfo_ismapped() and i > 0) else ""
                parts.append(f"{l_op} Check({s_map.get(c['var'].get())}, '{c['op'].get()}', {c['val'].get()})")
            return " ".join(parts) if parts else "true"

        try:
            with open(file_path, "w") as f:
                f.write("#include <Arduino.h>\n#include \"RobotConstants.h\"\n\nvoid setup() { Robot_Init(); }\n\nvoid loop() {\n")
                for s in self.steps:
                    if not s['frame'].winfo_exists(): continue
                    f.write(f"  while({build_expr(s['w_conds'])}){{\n    UpdateSensors();\n")
                    t = s['target'].get()
                    if t == "Vector Motion": f.write(f"    vector_motion({s['vx'].get()}, {s['vy'].get()});\n")
                    elif t == "Degree Motion": f.write(f"    degree_motion({s['deg_mov'].get()}, {s['speed'].get()});\n")
                    elif t == "Move To(X,Y)": f.write(f"    move_to({s['px'].get()}, {s['py'].get()}, {s['speed'].get()});\n")
                    elif t == "Move Along X": f.write(f"    move_along('X', {s['px'].get()}, {s['speed'].get()});\n")
                    elif t == "Move Along Y": f.write(f"    move_along('Y', {s['py'].get()}, {s['speed'].get()});\n")
                    else: f.write("    Stop_Robot();\n")
                    
                    # Face Front logic (fixed at 90 deg in code generation)
                    rv = "90" if s['rot_m'].get() == "Face Front" else s['rot_v'].get()
                    f.write(f"    UpdateRotation({rot_map[s['rot_m'].get()]}, {rv}, {s['rot_spd'].get()});\n")
                    f.write(f"    if({build_expr(s['u_conds'])}) break;\n  }}\n\n")
                f.write("  Stop_Robot(); while(1);\n}\n")
            print("Generated main.cpp")
        except Exception as e: print(f"File Error: {e}")

    def build_robot(self):
        self.generate_logic()
        pio_exe = os.path.join(os.environ.get('USERPROFILE'), r".platformio\penv\Scripts\platformio.exe")
        try: subprocess.run(["powershell", "-Command", f'& "{pio_exe}" run'], cwd="Teensy4.1-RCJ2026", check=True)
        except Exception as e: print(f"Build Error: {e}")

    def flash_robot(self):
        self.generate_logic()
        pio_exe = os.path.join(os.environ.get('USERPROFILE'), r".platformio\penv\Scripts\platformio.exe")
        try: subprocess.run(["powershell", "-Command", f'& "{pio_exe}" run --target upload'], cwd="Teensy4.1-RCJ2026", check=True)
        except Exception as e: print(f"Flash Error: {e}")

if __name__ == "__main__":
    root = tk.Tk(); app = RoboCupTacticalBoard(root); root.mainloop()