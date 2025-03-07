import tkinter as tk
import numpy as np
from sage.all import *

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Editor")
        self.root.geometry("1000x500")

        #this stores a map with the name of the vertex mapped to the location on the canvas
        self.vertices = {} 
        #stores a pair of strings of (name1,name2)
        self.edges = []  
        #this is for the canvas
        self.vertex_objects = {} 
        #selection based on clickdown
        self.selected_vertex = []
        #selection for dragging stuff
        self.dragging_vertex = None

        self.adjacency_matrix = np.zeros((0,0))

        self.default_name = "V"
        self.default_counter = 0

        #this is the left sidebar
        self.sidebar = tk.Frame(root, width=200, bg="lightgray")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # this is the right sidebar 
        self.info_panel = tk.Frame(root, width=400, bg="white")
        self.info_panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.info_text = tk.Text(self.info_panel, wrap=tk.WORD, height=30, width=50)
        self.info_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        clear_btn = tk.Button(self.info_panel,text="Clear",command=self.clearlog)
        clear_btn.pack(pady=5,side="bottom")

        options = [
            {"name": "V - Add Vertex", "command": self.add_vertex, "shortcut": "v"},
            {"name": "K - Create Complete", "command": self.create_K, "shortcut": "k"},
            {"name": "S - Create Star", "command": self.create_star, "shortcut": "s"},
            {"name": "D - Delete Edges", "command": self.clear_edges, "shortcut": "d"},
            {"name": "R - Delete Vertex", "command": self.clear_vertex, "shortcut": "r"},
            {"name": "C - Clear Selected", "command": self.clear_selection, "shortcut": "c"}
        ]

        for option in options:
            btn = tk.Button(self.sidebar, text=option["name"], command=option["command"])
            self.root.bind(option["shortcut"], option["command"])
            btn.pack(pady=5)
        note = tk.Label(
            self.sidebar,
            text="Note: Some options are wacky. Please click on the vertex to select it.",
            wraplength=120,
            bg="lightgray"
        )
        note.pack(fill="both",pady=5,side="bottom")

        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_vertex)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

    '''
    These are option functions
    '''
    def add_vertex(self, event=None):
        name = self.default_name + str(self.default_counter)
        if name and name not in self.vertices:
            col = 4
            x, y = 50 + (len(self.vertices) % col) * 100, 50 + (len(self.vertices) // col) * 100
            self.vertices[name] = (x, y)
            oval = self.canvas.create_oval(x-15, y-15, x+15, y+15, fill="yellow", outline="black", tags=name)
            text = self.canvas.create_text(x, y, text=name, fill="black", tags=name)
            
            self.vertex_objects[name] = (oval, text)
            self.default_counter += 1

            n = len(self.vertices)
            if n == 1:
                self.adjacency_matrix = np.zeros((1,1))
            else:
                new_col = np.zeros((n, 1))  
                new_row = np.zeros((1, n - 1)) 
                
                self.adjacency_matrix = np.vstack([self.adjacency_matrix, new_row])
                self.adjacency_matrix = np.hstack([self.adjacency_matrix, new_col])
            self.calculate_eigens()
    def clear_vertex(self, event=None):
        for name in self.selected_vertex:
            for vert in self.vertices:
                self.deleteEdge(name,vert)
        for name in self.selected_vertex:
            oval, text = self.vertex_objects[name]
            self.canvas.delete(oval)
            self.canvas.delete(text)
            

            location = list(self.vertices.keys()).index(name)
            self.adjacency_matrix = np.delete(self.adjacency_matrix, location, axis=0)
            self.adjacency_matrix = np.delete(self.adjacency_matrix, location, axis=1)
            del self.vertices[name]
            del self.vertex_objects[name]
        self.selected_vertex = []
        self.calculate_eigens()
        self.update_edges()


    def create_K(self, event=None):
        for i in range(len(self.selected_vertex)):
            for j in range(len(self.selected_vertex)):
                if i <= j:
                    continue
                namev1 =self.selected_vertex[i]
                namev2 =self.selected_vertex[j]
                self.updateEdge(namev1,namev2)
        self.update_edges()
        self.calculate_eigens()

    def create_star(self, event=None):
        if(len(self.selected_vertex)==0):
            return
        last_select = self.selected_vertex[len(self.selected_vertex)-1]
        for name in self.selected_vertex:
            if name == last_select:
                continue
            self.updateEdge(name, last_select)
        self.update_edges()
        self.calculate_eigens()

    def clear_edges(self,event=None):
        for vert1 in self.selected_vertex:
            for vert2 in self.selected_vertex:
                if vert1 == vert2: 
                    continue
                self.deleteEdge(vert1,vert2)
        self.update_edges()
        self.calculate_eigens()

    def clear_selection(self, event=None):
        for name in self.selected_vertex:
            oval, text = self.vertex_objects[name]
            self.canvas.itemconfig(oval, fill="yellow")
        self.selected_vertex = []

    '''
    END OF OPTION FUNCTIONS
    START OF UI FUNCTIONS
    '''
    def start_drag(self, event):
        overlap = self.canvas.find_overlapping(event.x-5, event.y-5,event.x+5, event.y+5)
        item = None
        #find vertex that overlaps with the click
        for i in overlap:
            for name,(oval,text) in self.vertex_objects.items():
                if i == oval or i == text:
                    item = name
                    break
        if item == None:
            return
        #do stuff depending on if the it selected
        if name in self.selected_vertex:
            self.selected_vertex.remove(name)
            self.canvas.itemconfig(oval, fill="yellow")
        else:
            if len(self.selected_vertex) != 0:
                last_select = self.selected_vertex[len(self.selected_vertex)-1]
                last_oval, last_text = self.vertex_objects[last_select]
                self.canvas.itemconfig(last_oval, fill="red")
            self.selected_vertex.append(name)
            self.dragging_vertex = name
            self.canvas.itemconfig(oval, fill="green")

    def drag_vertex(self, event):
        if self.dragging_vertex:
            x, y = event.x, event.y
            self.vertices[self.dragging_vertex] = (x, y)
            
            oval, text = self.vertex_objects[self.dragging_vertex]
            self.canvas.coords(oval, x-15, y-15, x+15, y+15)
            self.canvas.coords(text, x, y)
            self.update_edges()

    def stop_drag(self, event):
        self.dragging_vertex = None

    '''
    HELPER FUNCTIONS/UPDATE FUNCTIONS
    '''
    def updateEdge(self,namev1,namev2):
        v1 = list(self.vertices.keys()).index(namev1)
        v2 = list(self.vertices.keys()).index(namev2)
        if namev1 in self.vertices and namev2 in self.vertices:
            edge = (min(namev1,namev2), max(namev1,namev2))
            if edge not in self.edges:
                self.edges.append(edge)
                self.adjacency_matrix[v1][v2] = 1
                self.adjacency_matrix[v2][v1] = 1
            elif edge in self.edges:
                self.edges.remove(edge)
                self.adjacency_matrix[v1][v2] = 0
                self.adjacency_matrix[v2][v1] = 0
    def deleteEdge(self,namev1,namev2):
        v1 = list(self.vertices.keys()).index(namev1)
        v2 = list(self.vertices.keys()).index(namev2)
        if namev1 in self.vertices and namev2 in self.vertices:
            edge = (min(namev1,namev2), max(namev1,namev2))
            if edge in self.edges:
                self.edges.remove(edge)
                self.adjacency_matrix[v1][v2] = 0
                self.adjacency_matrix[v2][v1] = 0
        
    def update_edges(self):
        self.canvas.delete("edge")  # Remove all edges
        for v1, v2 in self.edges:
            x1, y1 = self.vertices[v1]
            x2, y2 = self.vertices[v2]
            self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2, tags="edge")
        for vertex in self.vertices:
            self.canvas.tag_raise(vertex)

    def calculate_eigens(self):
        ADJ = Matrix(self.adjacency_matrix)
        ADJeigenvalues = ADJ.eigenvalues()
        ADJcharpoly = ADJ.charpoly()

        laplacian = self.adjacency_matrix.copy()
        for i in range(len(self.adjacency_matrix)):
            laplacian[i][i] = sum(self.adjacency_matrix[i])
        LAPLACE = Matrix(laplacian)
        LAPeigenvalues = LAPLACE.eigenvalues()
        LAPcharpoly = LAPLACE.charpoly()

        adj_matrix_str = "\n".join([" ".join([str(int(cell)) for cell in row]) for row in ADJ])  
        laplacian_str = "\n".join([" ".join([str(int(cell)) for cell in row]) for row in LAPLACE])


        #self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, 
            "Vertices n = " + str(len(self.vertices)) + "\n"+
            "Edges e = " + str(len(self.edges)) + "\n\n"+
            "Adjacency Matrix:\n" + str(adj_matrix_str) + "\n\n"+
            "Adjacency Eigenvalues:\n" + str(ADJeigenvalues) + "\n\n"+
            "Adj. Characteristic Poly:\n" + polytounicode(str(ADJcharpoly)) + "\n\n"+
            "Laplacian Matrix:\n" + str(laplacian_str) + "\n\n"+
            "Laplacian Eigenvalues:\n" + str(LAPeigenvalues) + "\n\n"+
            "Lap. Characteristic Poly:\n" + polytounicode(str(LAPcharpoly)) + "\n\n"+
            "-"*20 + "\n\n"
        )
    def clearlog(self):
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Cleared log\n")

def polytounicode(str):
    conversion = {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
        "-": "⁻",
        "+": "⁺",
        ".": "·"
    }
    #state = 0 means has not found the ^ yet
    #state = 1 means has found the ^ and is currently converting the number

    state = 0
    ret = ""
    for it in str:
        if it == "^":
            state = 1
            continue
        if state == 1:
            if it.isdigit():
                ret += conversion[it]
            else:
                state = 0
                ret += it
        else:
            ret += it
    return ret
        
    


def printmatrix(matrix):
    for i in matrix:
        print(i)
    print("---------\n")
root = tk.Tk()
app = GraphApp(root)
root.mainloop()
