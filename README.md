## Test Solution for Junior Software Developer  

### I used Python version 3.13.1  

#### Libraries Used  
---  
**NumPy** – Generation of the 200x200 matrix with random values.  
**Itertools** – Generate multiple tuple combinations.  
**Operator** – To sum tuples with other tuples.  

I also included a *requirements.txt* file with the NumPy version, while the other libraries are built into Python by default.  

## How to Run the Program  
By default, **I set the matrix size to 10x10** (Graphviz starts to slow down a lot on my machine for values above 50). However, if you need to modify it for testing, **line 176**, after *size*, is where you can change it.  

The **main file is `main.py`**, just run it, and everything should work as expected.  

**At the end of execution, a `result.dot` file will be generated with the Graphviz code.**  

> I also included two additional files: **`result.dot`**, which contains the Graphviz DOT code for a graph I previously generated in a 10x10 matrix, and **`image.png`**, which is the graphical representation of this graph in PNG format.  

To convert the Graphviz code into a PNG file, I used this command (Linux):  
> `dot -Tpng result.dot -o image.png`