import tkinter as tk
from sage.all import *

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Editor")
        self.root.geometry("800x600")

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

        self.adjacency_matrix = []

        self.default_name = "V"
        self.default_counter = 0

        self.sidebar = tk.Frame(root, width=200, bg="lightgray")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.add_vertex_btn = tk.Button(self.sidebar, text="V - Add Vertex", command=self.add_vertex)
        self.root.bind("v", self.add_vertex)
        self.add_vertex_btn.pack(pady=5)

        self.add_edge_btn = tk.Button(self.sidebar, text="E - Add Edge", command=self.add_edge)
        self.root.bind("e", self.add_edge)
        self.add_edge_btn.pack(pady=5)

        self.clear_btn = tk.Button(self.sidebar, text="C - Clear Selected", command=self.clear_selection)
        self.root.bind("c", self.clear_selection)
        self.clear_btn.pack(pady=5)


        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_vertex)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

    def add_vertex(self, event=None):
        name = self.default_name + str(self.default_counter)
        if name and name not in self.vertices:
            x, y = 50 + (len(self.vertices) % 5) * 100, 50 + (len(self.vertices) // 5) * 100
            self.vertices[name] = (x, y)
            print(self.vertices)
            oval = self.canvas.create_oval(x-15, y-15, x+15, y+15, fill="yellow", outline="black", tags=name)
            text = self.canvas.create_text(x, y, text=name, fill="black", tags=name)
            
            self.vertex_objects[name] = (oval, text)
            self.default_counter += 1

            for i in self.adjacency_matrix:
                i.append(0)
            self.adjacency_matrix.append([0]*len(self.vertices))
            self.calculate_eigens()

    def add_edge(self, event=None):
        for i in range(len(self.selected_vertex)):
            for j in range(len(self.selected_vertex)):
                if i <= j:
                    continue

                namev1 =self.selected_vertex[i]
                namev2 =self.selected_vertex[j]
                v1 = list(self.vertices.keys()).index(self.selected_vertex[i])
                v2 = list(self.vertices.keys()).index(self.selected_vertex[j])
                if namev1 in self.vertices and namev2 in self.vertices:
                    edge = (min(namev1,namev2), max(namev1,namev2))
                    print("Edge: ", edge)
                    if edge not in self.edges:
                        self.edges.append(edge)
                        self.adjacency_matrix[v1][v2] = 1
                        self.adjacency_matrix[v2][v1] = 1
                    elif edge in self.edges:
                        self.edges.remove(edge)
                        self.adjacency_matrix[v1][v2] = 0
                        self.adjacency_matrix[v2][v1] = 0
        self.update_edges()
        self.calculate_eigens()

    def clear_selection(self, event=None):
        for name in self.selected_vertex:
            oval, text = self.vertex_objects[name]
            self.canvas.itemconfig(oval, fill="yellow")
        self.selected_vertex = []

    def start_drag(self, event):
        overlap = self.canvas.find_overlapping(event.x-5, event.y-5,event.x+5, event.y+5)
        if(len(overlap) == 0):
            return
        item = overlap[0]
        for name, (oval, text) in self.vertex_objects.items():
            if item in (oval, text):
                #print ("Before",self.selected_vertex)
                if name in self.selected_vertex:
                    self.selected_vertex.remove(name)
                    self.canvas.itemconfig(oval, fill="yellow")
                else:
                    self.selected_vertex.append(name)
                    self.canvas.itemconfig(oval, fill="red")
                    self.dragging_vertex = name
                #print ("After",self.selected_vertex)
                break
            
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

    def update_edges(self):
        self.canvas.delete("edge")  # Remove all edges
        for v1, v2 in self.edges:
            x1, y1 = self.vertices[v1]
            x2, y2 = self.vertices[v2]
            self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2, tags="edge")

    def calculate_eigens(self):
        printmatrix(self.adjacency_matrix)
        ADJ = Matrix(self.adjacency_matrix)
        ADJeigenvalues = ADJ.eigenvalues()
        print("ADJ eigenvalues: ", ADJeigenvalues)
        ADJcharpoly = ADJ.charpoly()
        print("ADJ Characteristic Poly: ", ADJcharpoly)
        '''
        ADJeigenvectors = ADJ.eigenvectors()
        print("ADJ eigenvectors: ", ADJeigenvectors)
        '''
        print("---------\n")
# Run the app

def printmatrix(matrix):
    for i in matrix:
        print(i)
    print("---------\n")
root = tk.Tk()
app = GraphApp(root)
root.mainloop()
