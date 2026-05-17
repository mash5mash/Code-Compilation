import random
import cv2 as cv
import numpy as np
from math import atan2, sqrt

algorithm_bounds = 1000
points = []
colors = []
voronoi_cells = []

img = np.zeros((algorithm_bounds, algorithm_bounds, 3), np.uint8)
events = [i for i in dir(cv) if 'EVENT' in i]
id_counter = 0

class Point:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
class Segment:
    def __init__(self, p1, p2, id):

        # NOTA: aseguramonos que el punto 1 este a la "izquierda" del segundo. Esto es importante para el resto de la implementacion.
        if p1.x < p2.x or (p1.x == p2.x and p1.y < p2.y):
            self.p1 = p1
            self.p2 = p2
        else:
            self.p1 = p2
            self.p2 = p1
        self.id = id
class UnorderedSegment:
    def __init__(self, p1, p2):
            self.p1 = p1
            self.p2 = p2

class Nodo:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.izq = None  # Left child
        self.der = None  # Right child

# Math tools
def cross(a, b):
    result = a[0] * b[1] - a[1] * b[0]
    print("Cross product result:" + str(result))
    return result
def distance(p1, p2):
    return ((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2) ** 0.5
def intersect(seg1, seg2):
    p = seg1.p1
    r = (seg1.p2.x - seg1.p1.x, seg1.p2.y - seg1.p1.y)
    q = seg2.p1
    s = (seg2.p2.x - seg2.p1.x, seg2.p2.y - seg2.p1.y)

    r_cross_s = cross(r, s)
    q_minus_p = (q.x - p.x, q.y - p.y)

    if r_cross_s == 0:
        return None  # Parallel

    t = cross(q_minus_p, s) / r_cross_s
    u = cross(q_minus_p, r) / r_cross_s

    if 0 <= t <= 1 and 0 <= u <= 1:
        inter_x = int(p.x + t * r[0])
        inter_y = int(p.y + t * r[1])
        return Point(inter_x, inter_y)
    return None

# Node functions
def recorrer_pos(aux):
    """Post-order traversal."""
    if aux is not None:
        recorrer_pos(aux.izq)
        recorrer_pos(aux.der)
        print(f"({aux.x}, {aux.y}) ,", end=' ')
def recorrer_pre(aux):
    """Pre-order traversal."""
    if aux is not None:
        print(f"({aux.x}, {aux.y}) ,", end=' ')
        recorrer_pre(aux.izq)
        recorrer_pre(aux.der)
def recorrer_in(aux):
    """In-order traversal."""
    if aux is not None:
        recorrer_in(aux.izq)
        print(f"({aux.x}, {aux.y}) ,", end=' ')
        recorrer_in(aux.der)

# OpenCV tools
def draw_points(img, points, color=(0, 255, 0)):
    for point in points:
        cv.circle(img, (point.x, point.y), 5, color, -1)
def draw_lines(img, segments, color=(255, 0, 0)):
    for seg in segments:
        cv.line(img, (seg[0].x, seg[0].y), (seg[1].x, seg[1].y), color, 2)
def draw_segments(img, segments):
    for seg in segments:
        print(seg.p1.x, seg.p1.y)
        cv.line(img, (seg.p1.x, seg.p1.y), (seg.p2.x, seg.p2.y), (0,255,0), 2)
def draw_area(img, points, color):
    converted_points = []

    for point in points:
        # Extract the x and y attributes from Point objects in points[i]
        converted_points.append((point.x, point.y))
        # Convert the list of (x, y) tuples into a numpy array with the proper shape
    contour = np.array(converted_points, dtype=np.int32).reshape((-1, 1, 2))
    print(contour)
        # Draw the contour on the image
    cv.fillPoly(img, [contour], color)
def begin_program(img):
    cv.putText(img, "left click to add to the diagram", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv.putText(img, "right click to check a point for proximity", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv.putText(img, "press 'q' to quit", (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv.waitKey(0)
    cv.destroyAllWindows()
def addPoint(event, x, y, flags, param):
    global points, voronoi_cells, colors, img
    if event == cv.EVENT_LBUTTONDOWN:
        points.append(Point(x, y))
        colors.append((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        voronoi_cells = make_voronoy_graph(points)
        redraw_image()
        draw_voronoy_graph(voronoi_cells, points, img, colors)

    elif event == cv.EVENT_RBUTTONDOWN:  # Right click: Check proximity or other action
        close_point = img.copy()
        pt = Point(x, y)
        for i, cell in enumerate(voronoi_cells):
            if point_in_polygon(pt, cell):
                cv.circle(close_point, (pt.x, pt.y), 9, (255,0,0), -1)
                cv.circle(close_point, (points[i].x, points[i].y), 9, (255, 0, 0), -1)
                break
        redraw_proximity_image(close_point)
        cv.waitKey(0)
        cv.destroyAllWindows()
def redraw_image():
    global img
    img = np.zeros((algorithm_bounds, algorithm_bounds, 3), np.uint8)
    draw_voronoy_graph(voronoi_cells, points, img, colors)
    cv.imshow('VoronoyProgram', img)
def redraw_proximity_image(canvas):
    cv.imshow('VoronoyProgram', canvas)
def draw_voronoy_graph(voronoi_cells, pointList, img, colorList):
    for i, cell in enumerate(voronoi_cells):
        voronoi_points = extract_points_from_segments(cell)
        draw_area(img, voronoi_points, colorList[i])

    for pt in pointList:
        cv.circle(img, (pt.x, pt.y), 5, (0, 255, 255), -1)

# Testing tools
def print_segments(segments):
    for seg in segments:
        print(seg.p1.x, seg.p1.y, seg.p2.x, seg.p2.y)
def print_points(points):
    for pt in points:
        print(pt.x, pt.y)
def get_random_segments(n):
    segments = []
    for i in range(n):
        x1 = int(random.random() * 500)
        y1 = int(random.random() * 500)
        x2 = int(random.random() * 500)
        y2 = int(random.random() * 500)
        segments.append(Segment(Point(x1, y1), Point(x2, y2), i))
    return segments
def get_bisector_segment(seg):
    x1, y1 = seg.p1.x, seg.p1.y
    x2, y2 = seg.p2.x, seg.p2.y
    x_mid = (x1 + x2) / 2
    y_mid = (y1 + y2) / 2

    if x2 - x1 == 0:
        return UnorderedSegment(Point(-1, y_mid), Point(algorithm_bounds + 1, y_mid))

    if y2 - y1 == 0:
        return UnorderedSegment(Point(x_mid, -1), Point(x_mid, algorithm_bounds + 1))

    original_slope = (y2 - y1) / (x2 - x1)
    perpendicular_slope = -1 / original_slope

    def getline(x):
        return perpendicular_slope * (x - x_mid) + y_mid

    return UnorderedSegment(
        Point(-1, getline(-1)),
        Point(algorithm_bounds + 1, getline(algorithm_bounds + 1))
    )
def get_square_points():
    SquarePoints = []
    SquarePoints.append(Point(0, 0))
    SquarePoints.append(Point(0, algorithm_bounds))
    SquarePoints.append(Point(algorithm_bounds, algorithm_bounds))
    SquarePoints.append(Point(algorithm_bounds, 0))
    return SquarePoints

# Algorithmns
def find_intersections(segments):

    #Los segmentos evaluan con base en eventos. Estos simplemente son todos los puntos de las lineas, si son el final/inicio, y que id tienen.
    events = []
    for seg in segments:
        events.append((seg.p1.x, 0, seg.id))
        events.append((seg.p2.x, 1, seg.id))

    #Se tienen que explorar de menor a mayor (izquierda a derecha).
    events.sort()

    #La lista Active sostiene cuales son los segmentos actualmente comparados.
    active = []

    #Esta lista de intersecciones deberia ser el "final" de nuestra funcion. Se le metera conforme se encuentren intersecciones.
    intersections = []

    #Se construye un diccionario de los segmentos para que buscarlos sea mas facil, pues solo los buscamos con base en su id. Esto tambien ayuda a compararlos correctamente.
    segments_dict = {seg.id: seg for seg in segments}


    #Funcion que regresa el valor y de cualquier segmento en el determinado punto x.
    def get_y(seg, x):
        x1, y1 = seg.p1.x, seg.p1.y
        x2, y2 = seg.p2.x, seg.p2.y
        if x1 == x2:
            return y1
        t = (x - x1) / (x2 - x1)
        return y1 + t * (y2 - y1)

    #Funcion que inserta un segmento a la lista "activa" en orden descendiente tomando en cuenta donde intersecta el segmento con la linea. los acomoda de arriba hacia abajo.
    def insert(seg, x):
        y = get_y(seg, x)
        for i in range(len(active)):
            if get_y(active[i], x) > y:
                active.insert(i, seg)
                return
        active.append(seg)

    #Remueve de la lista activa si el segmento ya no se encuentra dentro de la linea.
    def remove(seg):
        for i in range(len(active)):
            if active[i].id == seg.id:
                active.pop(i)
                return

    #Para evitar errores, se tienen que comparar _todas_ las intersecciones encontradas, no detenerse a la primera. Funcion que compara todos los elementos de la lista activa y regresa todas las intersecciones de los mismos.
    def check_all_pairs(active, x):
        found = []
        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                #funcion Intersect usada con cada elemento.
                pt = intersect(active[i], active[j])
                if pt and (pt.x, pt.y) not in [(p.x, p.y) for p in found]:
                    found.append(pt)
        return found

    #esta es "la linea". eventos fue creada desde el inicio, esto solo cicla entre ella con una terna.
    for x, kind, seg_id in events:
        seg = segments_dict[seg_id]
        frame = img.copy()
        cv.line(frame, (x, 500), (x, 0), (0, 0, 255), 1)

        for pt in intersections:
            cv.circle(frame, (pt.x, pt.y), 6, (255, 0, 255), -1)

        cv.imshow("Segments", frame)
        cv.waitKey(200)  # Delay to visualize step-by-step

        #Si el punto tocado es el inicio de un segmento, inserta el segmento a la lista activa.
        if kind == 0:
            insert(seg, x)
        #Si es el final, entonces remuevelo.
        else:
            remove(seg)

        new_pts = check_all_pairs(active, x)
        for pt in new_pts:
            #inserta a Intersecciones solo si no se encuentra en las intersecciones ya encontradas.
            if (pt.x, pt.y) not in [(p.x, p.y) for p in intersections]:
                intersections.append(pt)

    return intersections
def point_in_polygon(Point, segments):

    x, y = Point.x, Point.y
    polygon_points = []

    for seg in segments:
        polygon_points.append((seg.p1.x, seg.p1.y))

    n = len(polygon_points)
    inside = False

    j = n - 1
    for i in range(n):
        if ((polygon_points[i][1] > y) != (polygon_points[j][1] > y) and
                (x < (polygon_points[j][0] - polygon_points[i][0]) * (y - polygon_points[i][1]) /
                 (polygon_points[j][1] - polygon_points[i][1]) + polygon_points[i][0])):
            inside = not inside
        j = i

    return inside
def extract_points_from_segments(segments):
    points = []
    seen_points = set()  # Use a set to track unique points
    for segment in segments:
        for point in [(segment.p1.x, segment.p1.y), (segment.p2.x, segment.p2.y)]:
            if point not in seen_points:  # Check if the point is unique
                points.append(Point(point[0], point[1]))
                seen_points.add(point)
    print("extracted points:")
    for point in points:
        print(point.x, point.y)
    return points
def graham_scan(points):
    start = min(points, key=lambda p: (p.y, p.x))
    print("graham scan was given points:")
    print_points(points)

    def polar_angle(p):
        return np.arctan2(p.y - start.y, p.x - start.x)

    def distance_from_start(p):
        return distance(start, p)

    sorted_points = [p for p in points if p != start]
    sorted_points.sort(key=lambda p: (polar_angle(p), distance_from_start(p)))

    print("graham scan sorted points:")
    print_points(points)

    hull = [start]
    for p in sorted_points:
        while len(hull) > 1 and cross(
            (hull[-1].x - hull[-2].x, hull[-1].y - hull[-2].y),
            (p.x - hull[-1].x, p.y - hull[-1].y)
        ) < 0:
            hull.pop()
        hull.append(p)

    print("graham scan results in the points:")
    print_points(hull)

    unordered_segments = [
        UnorderedSegment(hull[i], hull[(i + 1) % len(hull)])
        for i in range(len(hull))
    ]

    return unordered_segments
def graham_scan_visualization(points, canvas):
    start = min(points, key=lambda p: (p.y, p.x))

    # Draw the starting point
    cv.circle(canvas, (start.x, start.y), 7, (0, 0, 255), -1)

    # Step 1: Sort points by polar angle and distance
    def polar_angle(p):
        return atan2(p.y - start.y, p.x - start.x)

    def distance_from_start(p):
        return distance(start, p)

    sorted_points = [p for p in points if p != start]
    sorted_points.sort(key=lambda p: (polar_angle(p), distance_from_start(p)))

    # Highlight sorted points one by one in real time
    for p in sorted_points:
        draw_points(canvas, [p], color=(255, 255, 0))
        cv.imshow('Graham Scan Visualization', canvas)
        cv.waitKey(300)  # Delay to visualize the sorting process

    # Step 2: Build the convex hull
    hull = [start]
    for p in sorted_points:
        while len(hull) > 1 and cross(
            (hull[-1].x - hull[-2].x, hull[-1].y - hull[-2].y),
            (p.x - hull[-1].x, p.y - hull[-1].y)
        ) < 0:  # Right turn, not a valid point for the hull
            hull.pop()

            # Visualize point removal
            canvas_copy = canvas.copy()
            draw_lines(canvas_copy, [(hull[i], hull[i + 1]) for i in range(len(hull) - 1)])
            cv.imshow('Graham Scan Visualization', canvas_copy)
            cv.waitKey(300)

        hull.append(p)

        # Visualize the current state of the hull
        canvas_copy = canvas.copy()
        draw_lines(canvas_copy, [(hull[i], hull[i + 1]) for i in range(len(hull) - 1)])
        cv.imshow('Graham Scan Visualization', canvas_copy)
        cv.waitKey(300)

    # Close the loop to form the convex hull
    hull.append(hull[0])
    draw_lines(canvas, [(hull[i], hull[i + 1]) for i in range(len(hull) - 1)], color=(0, 255, 255))

    return hull
def split_polygon(polygon, split_segment):

    # Step 1: Find intersection points between the split segment and the polygon edges
    intersection_points = []
    intersection_indices = []
    for i, edge in enumerate(polygon):
        intersection = intersect(edge, split_segment)  # Uses the `intersect` function defined above
        if intersection:
            intersection_points.append(intersection)
            intersection_indices.append(i)  # Keep track of which edge's index was intersected

    # Check if there are exactly two intersection points
    if len(intersection_points) != 2:
        return None

    # Step 2: Extract the points from the polygon (in order) for easier processing
    points = []
    for edge in polygon:
        points.append(edge.p1)
    points.append(polygon[0].p1)  # Close the polygon by appending the first point again

    # Add intersection points inside the polygon points in-order
    # Insert the intersection points directly at the correct location
    idx1, idx2 = intersection_indices[0], intersection_indices[1]
    intersection_points_added = False  # A flag to indicate intersections have been added

    # Ensuring the first intersection point comes before the second
    if idx1 > idx2:
        idx1, idx2 = idx2, idx1
        intersection_points.reverse()

    # Insert the intersection points into polygon
    points.insert(idx1 + 1, intersection_points[0])  # Insert first intersection
    points.insert(idx2 + 2, intersection_points[1])  # Insert second intersection

    # Get the indices again after the insertion
    split_idx_1 = idx1 + 1
    split_idx_2 = idx2 + 2

    # Step 3: Divide the polygon into two parts based on the intersection points
    # Split the points into two ordered sets
    polygon1_points = points[split_idx_1:split_idx_2 + 1]
    polygon2_points = points[split_idx_2:] + points[:split_idx_1 + 1]

    # Step 4: Convert points to UnorderedSegment
    def create_polygon_segment(points):
        return [UnorderedSegment(points[i], points[(i + 1) % len(points)]) for i in range(len(points))]

    polygon1_segments = create_polygon_segment(polygon1_points)
    polygon2_segments = create_polygon_segment(polygon2_points)

    return polygon1_segments, polygon2_segments
def make_voronoy_graph(points):
    voronoi_cells = []

    for root_point in points:

        for pt in points:
            cv.circle(img, (pt.x, pt.y), 5, (0, 255, 255), -1)

        bounding_box = get_square_points()

        root_segments = graham_scan(bounding_box)

        for other_point in points:
            if root_point == other_point:
                continue

            bisector_segment = get_bisector_segment(UnorderedSegment(root_point, other_point))

            # Debug: Draw bisector and intersections
            draw_segments(img, [bisector_segment])

            cut_segments = split_polygon(root_segments, bisector_segment)
            if cut_segments is None:
                continue

            # Determine which polygon to keep
            if point_in_polygon(root_point, cut_segments[0]):
                root_segments = cut_segments[0]
            else:
                root_segments = cut_segments[1]

            # Debug: Draw resulting polygon segments
            draw_segments(img, root_segments)

        voronoi_cells.append((root_segments))

    return voronoi_cells

# Compilation functions:
def voronoi_main():
    global img
    begin_program(img)
    cv.imshow('VoronoyProgram', img)
    cv.setMouseCallback('VoronoyProgram', addPoint)
    while True:
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):  # Press 'q' to quit
            break
    cv.destroyAllWindows()
def graham_scan_main():
    # Initial canvas
    width, height = 800, 600
    canvas = np.zeros((height, width, 3), dtype=np.uint8)  # Black background

    # Generate random points for visualization
    num_points = 10
    points = [Point(random.randint(50, width - 50), random.randint(50, height - 50)) for _ in range(num_points)]

    # Draw points
    draw_points(canvas, points, color=(0, 255, 0))

    # Display before starting the Graham scan
    cv.imshow('Graham Scan Visualization', canvas)
    cv.waitKey(1000)  # Pause to visualize initial points

    # Perform the Graham scan and visualize
    hull = graham_scan_visualization(points, canvas)

    # Final Result
    print("Convex Hull Resulting Points:")
    for point in hull:
        print(f"({point.x}, {point.y})")

    # Wait for a key press
    cv.imshow('Graham Scan Visualization', canvas)
    cv.waitKey(0)
    cv.destroyAllWindows()
def line_sweep_main():
    segs = get_random_segments(10)
    draw_segments(img, segs)
    cv.imshow("Segments", img)
    cv.waitKey(1000)
    find_intersections(segs)
    cv.waitKey(0)
    cv.destroyAllWindows()
def kd_tree_main():
    raiz = None  # Root node
    op = 0

    while op != 5:  # Equivalent to the menu loop in C++
        print("\n*MENU***")
        print("1. Insertar nodo")
        print("2. Recorrer Posorden")
        print("3. Recorrer Preorden")
        print("4. Recorrer inOrden")
        print("5. Salir")
        op = int(input("Selecciona tu opción: "))

        if op == 1:
            # Create a new node
            x = int(input("Valor X? "))
            y = int(input("Valor Y? "))
            nuevo = Nodo(x, y)

            if raiz is None:
                raiz = nuevo  # Set as root if tree is empty
            else:
                aux = raiz
                count = 0
                while True:
                    count += 1
                    if count % 2 == 0:
                        # Insert based on y comparison
                        if nuevo.y < aux.y:
                            if aux.izq is None:
                                aux.izq = nuevo  # Insert directly
                                break
                            aux = aux.izq
                        else:
                            if aux.der is None:
                                aux.der = nuevo  # Insert directly
                                break
                            aux = aux.der
                    else:
                        # Insert based on x comparison
                        if nuevo.x < aux.x:
                            if aux.izq is None:
                                aux.izq = nuevo  # Insert directly
                                break
                            aux = aux.izq
                        else:
                            if aux.der is None:
                                aux.der = nuevo  # Insert directly
                                break
                            aux = aux.der

        elif op == 2:
            print("Recorrer Posorden:")
            recorrer_pos(raiz)
            print()
        elif op == 3:
            print("Recorrer Preorden:")
            recorrer_pre(raiz)
            print()
        elif op == 4:
            print("Recorrer inOrden:")
            recorrer_in(raiz)
            print()
        elif op == 5:
            print("Saliendo del programa...")
        else:
            print("Opción no válida!")

def MainMenu():

    done = False

    print("Check programs i've coded: ")
    print("1. Graham scan")
    print("2. KD-Tree")
    print("3. Line sweep")
    print("4. Voronoy Diagram")
    print("5. Exit")
    op = int(input("====> "))
    if op == 1:
        graham_scan_main()
    elif op == 2:
        kd_tree_main()
    elif op == 3:
        line_sweep_main()
    elif op == 4:
        voronoi_main()
    elif op == 5:
        done = True
    else:
        print("invalid option.")
    return done

def main():
    done = False
    while not done:
        done = MainMenu()

if __name__ == "__main__":
    main()