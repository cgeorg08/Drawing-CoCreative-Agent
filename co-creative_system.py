import tkinter as tk
from tkinter import ttk
from agent import *
import helper

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white", bd=2, relief=tk.SUNKEN)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # self.canvas.pack(side=tk.LEFT)
        self.setup_navbar()
        self.setup_tools()
        self.setup_events()
        self.prev_x = None
        self.prev_y = None
        self.items_previous_round = tuple()
        self.canvas.update()
        self.agent = Agent(width=self.canvas.winfo_width(),height=self.canvas.winfo_height())

        # episodes: rounds of drawings by agent and then the user
        self.userEpSteps = 0

    def setup_navbar(self):
        self.navbar = tk.Menu(self.root)
        self.root.config(menu=self.navbar)

        # File menu
        self.file_menu = tk.Menu(self.navbar, tearoff=False)
        self.navbar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save Snapshot", command=self.take_snapshot)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        self.edit_menu = tk.Menu(self.navbar, tearoff=False)
        self.navbar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=self.undo)

    def setup_tools(self):
        self.selected_tool = "pen"
        self.colors = ["black", "red", "green", "blue", "yellow", "orange", "purple"]
        self.selected_color = self.colors[0]
        self.brush_sizes = [2, 4, 6, 8]
        self.selected_size = self.brush_sizes[0]
        self.pen_types = ["line", "round", "square", "arrow", "diamond"]
        self.selected_pen_type = self.pen_types[0]

        self.tool_frame = ttk.LabelFrame(self.root, text="Co-creative Agent")
        self.tool_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

        self.agent_gen_button = ttk.Button(self.tool_frame, text="Similar Pattern", command=self.agent_generate_eps)
        self.agent_gen_button.pack(side=tk.TOP, padx=5, pady=5)

        self.agent_rep_button = ttk.Button(self.tool_frame, text="Replicate Drawing", command=self.agent_replicate)
        self.agent_rep_button.pack(side=tk.TOP, padx=5, pady=5)

        self.agent_mirhor_button = ttk.Button(self.tool_frame, text="Horizotal Mirror", command=self.agent_mirror_hor)
        self.agent_mirhor_button.pack(side=tk.TOP, padx=5, pady=5)

        self.agent_mirver_button = ttk.Button(self.tool_frame, text="Vertical Mirror", command=self.agent_mirror_ver)
        self.agent_mirver_button.pack(side=tk.TOP, padx=5, pady=5)

        self.agent_mer_button = ttk.Button(self.tool_frame, text="Merge Drawings", command=self.agent_merge)
        self.agent_mer_button.pack(side=tk.TOP, padx=5, pady=5)

        self.agent_genrand_button = ttk.Button(self.tool_frame, text="Random Pattern", command=self.agent_generate)
        self.agent_genrand_button.pack(side=tk.TOP, padx=5, pady=5)

        self.agent_bal_button = ttk.Button(self.tool_frame, text="Balance Canvas", command=self.agent_balance)
        self.agent_bal_button.pack(side=tk.TOP, padx=5, pady=5)

        self.tool_frame = ttk.LabelFrame(self.root, text="Tools")
        self.tool_frame.pack(side=tk.RIGHT, padx=5, pady=5)

        self.pen_button = ttk.Button(self.tool_frame, text="Pen", command=self.select_pen_tool)
        self.pen_button.pack(side=tk.TOP, padx=5, pady=5)

        self.eraser_button = ttk.Button(self.tool_frame, text="Eraser", command=self.select_eraser_tool)
        self.eraser_button.pack(side=tk.TOP, padx=5, pady=5)

        self.brush_size_label = ttk.Label(self.tool_frame, text="Brush Size:")
        self.brush_size_label.pack(side=tk.TOP, padx=5, pady=5)

        self.brush_size_combobox = ttk.Combobox(self.tool_frame, values=self.brush_sizes, state="readonly")
        self.brush_size_combobox.current(0)
        self.brush_size_combobox.pack(side=tk.TOP, padx=5, pady=5)
        self.brush_size_combobox.bind("<<ComboboxSelected>>", lambda event: self.select_size(int(self.brush_size_combobox.get())))

        self.color_label = ttk.Label(self.tool_frame, text="Color:")
        self.color_label.pack(side=tk.TOP, padx=5, pady=5)

        self.color_combobox = ttk.Combobox(self.tool_frame, values=self.colors, state="readonly")
        self.color_combobox.current(0)
        self.color_combobox.pack(side=tk.TOP, padx=5, pady=5)
        self.color_combobox.bind("<<ComboboxSelected>>", lambda event: self.select_color(self.color_combobox.get()))

        self.pen_type_label = ttk.Label(self.tool_frame, text="Pen Type:")
        self.pen_type_label.pack(side=tk.TOP, padx=5, pady=5)

        self.pen_type_combobox = ttk.Combobox(self.tool_frame, values=self.pen_types, state="readonly")
        self.pen_type_combobox.current(0)
        self.pen_type_combobox.pack(side=tk.TOP, padx=5, pady=5)
        self.pen_type_combobox.bind("<<ComboboxSelected>>", lambda event: self.select_pen_type(self.pen_type_combobox.get()))

        self.clear_button = ttk.Button(self.tool_frame, text="Clear Canvas", command=self.clear_canvas)
        self.clear_button.pack(side=tk.TOP, padx=5, pady=5)

    def setup_events(self):
        self.canvas.bind("<B1-Motion>", self.userDraw)
        self.canvas.bind("<ButtonRelease-1>", self.release)


    #----------------------------------------------------------------------------------------------------------------------------
    # Functionalities for the keys, labels and comboboxes

    def select_pen_tool(self):
        self.selected_tool = "pen"

    def select_eraser_tool(self):
        self.selected_tool = "eraser"

    def select_size(self, size):
        self.selected_size = size

    def select_color(self, color):
        self.selected_color = color

    def select_pen_type(self, pen_type):
        self.selected_pen_type = pen_type

    def clear_canvas(self):
        self.canvas.delete("all")

    def take_snapshot(self):
        self.canvas.postscript(file="snapshot.png")

    def undo(self):
        items = self.canvas.find_all()
        if items:
            self.canvas.delete(items[-1])

    def agent_generate_eps(self):
        self.updateCounters()
        self.agent.agentGenerate(self.canvas, None, self.canvas.winfo_width(), self.canvas.winfo_height(), 'local')

    def agent_replicate(self):
        self.updateCounters()
        self.agent.agentReplicate(self.canvas, None, self.canvas.winfo_width(), self.canvas.winfo_height())

    def agent_mirror_hor(self):
        self.updateCounters()
        self.agent.agentMirror(self.canvas, None, self.canvas.winfo_width(), self.canvas.winfo_height(), 'hor')

    def agent_mirror_ver(self):
        self.updateCounters()
        self.agent.agentMirror(self.canvas, None, self.canvas.winfo_width(), self.canvas.winfo_height(), 'ver')

    def agent_merge(self):
        self.updateCounters()
        self.agent.agentMerge(self.canvas)

    def agent_generate(self):
        self.updateCounters()
        self.agent.agentGenerate(self.canvas, None, self.canvas.winfo_width(), self.canvas.winfo_height(), 'global')

    def agent_balance(self):
        self.updateCounters()
        self.agent.agentBalance(self.canvas, self.canvas.winfo_width(), self.canvas.winfo_height())

    #----------------------------------------------------------------------------------------------------------------------------
    # Events


    # left mouse button motion event
    def userDraw(self, event):
        if self.selected_tool == "pen":
            if self.prev_x is not None and self.prev_y is not None:
                # print(f'USER: from ({self.prev_x},{self.prev_y}) to ({event.x},{event.y})')
                self.agent.storeDrawing(self.prev_x, self.prev_y, event.x, event.y)
                helper.draw(
                    canvas=self.canvas,
                    selected_pen_type=self.selected_pen_type,
                    selected_color=self.selected_color,
                    selected_size=self.selected_size,
                    prev_x=self.prev_x,
                    prev_y=self.prev_y,
                    x=event.x,
                    y=event.y
                )
            self.prev_x = event.x
            self.prev_y = event.y
            self.agent.storeCanvasPoints([(event.x, event.y)])
        elif self.selected_tool == "eraser":
            self.canvas.create_rectangle(event.x - 3, event.y - 3, event.x + 3, event.y + 3, fill="white", outline="white")

    # left mouse button release event
    def release(self, event):
        if self.selected_tool == "pen":
            self.userEpSteps += 1
            self.agent.preproDrawing(self.selected_size, self.selected_color, self.selected_pen_type, self.userEpSteps)
            # self.agent.adjustGridsize(self.canvas.winfo_width(), self.canvas.winfo_height())
            # self.agent.printAgentInfo()
            self.prev_x = None
            self.prev_y = None

    def updateCounters(self):
        self.userEpSteps = 0

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Paint Application")
    app = PaintApp(root)
    root.mainloop()