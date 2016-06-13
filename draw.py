from display import *
from matrix import *
from gmath import *
from math import cos, sin, pi

MAX_STEPS = 100
colors = [
    [255,89,94],
    [255,202,58],
    [138,201,38],
    [25,130,196],
    [137,33,186]   
]


def scanline_conversion(screen, tx, ty, tz, mx, my, mz, bx, by, bz, z_buffer, color):
    counter = 0
    while by + counter < ty:
        delta0x = float(tx - bx) / (ty - by)
        delta0z = (float(tz - bz) /
                   ((tx - bx) ** 2 + (ty - by) ** 2) ** (0.5))
        if by + counter < my:
            delta1x = float(mx - bx) / (my - by)
            delta1z = (float(mz - bz) /
                       ((mx - bx) ** 2 + (my - by) ** 2) ** (0.5))
            draw_line(screen,
                      bx + counter*delta0x, by + counter, bz + ((counter ** 2 + (counter * delta0x) ** 2) ** (0.5)) * delta0z,
                      bx + counter*delta1x, by + counter, bz + ((counter ** 2 + (counter * delta1x) ** 2) ** (0.5)) * delta1z,
                      z_buffer, color)
        else:
            delta1x = float(tx - mx) / (ty - my)
            delta1z = (float(tz - mz) /
                       ((tx - mx) ** 2 + (ty - my) ** 2) ** (0.5))
            draw_line(screen,
                      bx + counter*delta0x, by + counter, bz + (counter ** 2 + (counter * delta0x) ** 2) ** (0.5) * delta0z,
                      mx + (counter - my + by)*delta1x, by + counter, mz + ((counter - my + by) ** 2 + ((counter - my + by) * delta1x) ** 2) ** (0.5) * delta1z,
                      z_buffer, color)
        counter += 1

        
def add_polygon(points, x0, y0, z0, x1, y1, z1, x2, y2, z2):
    add_point(points, x0, y0, z0)
    add_point(points, x1, y1, z1)
    add_point(points, x2, y2, z2)


def normalization(vector):
    ax = 0
    ay = 0
    az = 0
    (ax, ay, az) = vector
    mag = (ax ** 2 + ay ** 2 + az ** 2) ** (.5)
    return [(ax/mag), (ay/mag), (az/mag)]

def calculate_light_dot(vector1, vector2):
    return (vector1[0] * vector2[0]) + (vector1[1] * vector2[1]) + (vector1[2] *  vector2[2]) 

    
def cos_alpha_calc(normal, light, view):
    ans = calculate_light_dot(normal, light)
    ans = [(2 * normal[i]  * ans - light[i]) for i in range(3)]
    ans = calculate_light_dot(ans, view)    
    return ans

def flat_shading(points, p):
    c_am = [0, 0, 255]
    k_am = .5
    i_am = [k_am * x for x in c_am]
    
    c_dif = [255, 0, 0]
    c_spec = [255, 255, 255]
    
    k_dif = .4
    k_spec = .1

    light_loc = [100, 100, 50 ]
    light_norm = normalization(light_loc)
    
    normal = normalization(calculate_normal(points[p + 1][0] - points[ p ][0],
                                            points[p + 1][1] - points[ p ][1],
                                            points[p + 1][2] - points[ p ][2],
                                            points[p + 2][0] - points[ p ][0],
                                            points[p + 2][1] - points[ p ][1],
                                            points[p + 2][2] - points[ p ][2]))

    cos_dif = calculate_light_dot(normal, light_norm)     
    i_dif = [min(max(0, int(k_dif * cos_dif * x)), 255) for x in c_dif]

    cos_spec = cos_alpha_calc(normal, light_norm, [0, 0, 5])
    i_spec = [min(max(0, int(k_spec * cos_spec * x)), 255) for x in c_spec]
            
    color = [int(i_am[i] +  i_dif[i] + i_spec[i]) for i in range(3)]
    #print color
    return color



    
def draw_polygons(points, screen, z_buffer, color):
    if len(points) < 3:
        print 'Need at least 3 points to draw a polygon!'
        return
    p = 0
    while p < len(points) - 2:
        if calculate_dot( points, p ) < 0:
            sorted_p = sorted([points[p],points[p+1],points[p+2]], key = lambda x: (x[1], -x[2]))
            color = flat_shading(points, p)
            scanline_conversion(screen,
                                sorted_p[2][0],sorted_p[2][1],sorted_p[2][2],
                                sorted_p[1][0],sorted_p[1][1],sorted_p[1][2],
                                sorted_p[0][0],sorted_p[0][1],sorted_p[0][2],
                                z_buffer, color)
            draw_line(screen, points[p][0], points[p][1], points[p][2],
                      points[p+1][0], points[p+1][1], points[p+1][2],
                      z_buffer, color)
            draw_line(screen, points[p+1][0], points[p+1][1], points[p+1][2],
                      points[p+2][0], points[p+2][1], points[p+2][2],
                      z_buffer, color)
            draw_line(screen, points[p+2][0], points[p+2][1], points[p+2][2],
                      points[p][0], points[p][1], points[p][2],
                      z_buffer, color)
            
        p += 3


def add_box(points, x, y, z, width, height, depth):
    x1 = x + width
    y1 = y - height
    z1 = z - depth

    #front
    add_polygon( points, 
                 x, y, z, 
                 x, y1, z,
                 x1, y1, z)
    add_polygon( points, 
                 x1, y1, z, 
                 x1, y, z,
                 x, y, z)
    #back
    add_polygon( points, 
                 x1, y, z1, 
                 x1, y1, z1,
                 x, y1, z1)
    add_polygon( points, 
                 x, y1, z1, 
                 x, y, z1,
                 x1, y, z1)
    #top
    add_polygon( points, 
                 x, y, z1, 
                 x, y, z,
                 x1, y, z)
    add_polygon( points, 
                 x1, y, z, 
                 x1, y, z1,
                 x, y, z1)
    #bottom
    add_polygon( points, 
                 x1, y1, z1, 
                 x1, y1, z,
                 x, y1, z)
    add_polygon( points, 
                 x, y1, z, 
                 x, y1, z1,
	         x1, y1, z1)
    #right side
    add_polygon( points, 
                 x1, y, z, 
                 x1, y1, z,
                 x1, y1, z1)
    add_polygon( points, 
                 x1, y1, z1, 
                 x1, y, z1,
                 x1, y, z)
    #left side
    add_polygon( points, 
                 x, y, z1, 
                 x, y1, z1,
                 x, y1, z)
    add_polygon( points, 
                 x, y1, z, 
                 x, y, z,
                 x, y, z1) 


def add_sphere( points, cx, cy, cz, r, step ):
    
    num_steps = MAX_STEPS / step
    temp = []

    generate_sphere( temp, cx, cy, cz, r, step )
    num_points = len( temp )

    lat = 0
    lat_stop = num_steps
    longt = 0
    longt_stop = num_steps

    num_steps += 1

    while lat < lat_stop:
        longt = 0
        while longt < longt_stop:
            
            index = lat * num_steps + longt

            px0 = temp[ index ][0]
            py0 = temp[ index ][1]
            pz0 = temp[ index ][2]

            px1 = temp[ (index + num_steps) % num_points ][0]
            py1 = temp[ (index + num_steps) % num_points ][1]
            pz1 = temp[ (index + num_steps) % num_points ][2]
            
            if longt != longt_stop - 1:
                px2 = temp[ (index + num_steps + 1) % num_points ][0]
                py2 = temp[ (index + num_steps + 1) % num_points ][1]
                pz2 = temp[ (index + num_steps + 1) % num_points ][2]
            else:
                px2 = temp[ (index + 1) % num_points ][0]
                py2 = temp[ (index + 1) % num_points ][1]
                pz2 = temp[ (index + 1) % num_points ][2]
                
            px3 = temp[ index + 1 ][0]
            py3 = temp[ index + 1 ][1]
            pz3 = temp[ index + 1 ][2]
      
            if longt != 0:
                add_polygon( points, px0, py0, pz0, px1, py1, pz1, px2, py2, pz2 )

            if longt != longt_stop - 1:
                add_polygon( points, px2, py2, pz2, px3, py3, pz3, px0, py0, pz0 )
            
            longt+= 1
        lat+= 1


def generate_sphere( points, cx, cy, cz, r, step ):

    rotation = 0
    rot_stop = MAX_STEPS
    circle = 0
    circ_stop = MAX_STEPS

    while rotation < rot_stop:
        circle = 0
        rot = float(rotation) / MAX_STEPS
        while circle <= circ_stop:
            
            circ = float(circle) / MAX_STEPS
            x = r * cos( pi * circ ) + cx
            y = r * sin( pi * circ ) * cos( 2 * pi * rot ) + cy
            z = r * sin( pi * circ ) * sin( 2 * pi * rot ) + cz
            
            add_point( points, x, y, z )

            circle+= step
        rotation+= step

def add_torus( points, cx, cy, cz, r0, r1, step ):
    
    num_steps = MAX_STEPS / step
    temp = []

    generate_torus( temp, cx, cy, cz, r0, r1, step )
    num_points = len(temp)

    lat = 0
    lat_stop = num_steps
    longt_stop = num_steps
    
    while lat < lat_stop:
        longt = 0

        while longt < longt_stop:
            index = lat * num_steps + longt

            px0 = temp[ index ][0]
            py0 = temp[ index ][1]
            pz0 = temp[ index ][2]

            px1 = temp[ (index + num_steps) % num_points ][0]
            py1 = temp[ (index + num_steps) % num_points ][1]
            pz1 = temp[ (index + num_steps) % num_points ][2]

            if longt != num_steps - 1:            
                px2 = temp[ (index + num_steps + 1) % num_points ][0]
                py2 = temp[ (index + num_steps + 1) % num_points ][1]
                pz2 = temp[ (index + num_steps + 1) % num_points ][2]

                px3 = temp[ (index + 1) % num_points ][0]
                py3 = temp[ (index + 1) % num_points ][1]
                pz3 = temp[ (index + 1) % num_points ][2]
            else:
                px2 = temp[ ((lat + 1) * num_steps) % num_points ][0]
                py2 = temp[ ((lat + 1) * num_steps) % num_points ][1]
                pz2 = temp[ ((lat + 1) * num_steps) % num_points ][2]

                px3 = temp[ (lat * num_steps) % num_points ][0]
                py3 = temp[ (lat * num_steps) % num_points ][1]
                pz3 = temp[ (lat * num_steps) % num_points ][2]


            add_polygon( points, px0, py0, pz0, px1, py1, pz1, px2, py2, pz2 );
            add_polygon( points, px2, py2, pz2, px3, py3, pz3, px0, py0, pz0 );        
            
            longt+= 1
        lat+= 1


def generate_torus( points, cx, cy, cz, r0, r1, step ):

    rotation = 0
    rot_stop = MAX_STEPS
    circle = 0
    circ_stop = MAX_STEPS

    while rotation < rot_stop:
        circle = 0
        rot = float(rotation) / MAX_STEPS
        while circle < circ_stop:
            
            circ = float(circle) / MAX_STEPS
            x = (cos( 2 * pi * rot ) *
                 (r0 * cos( 2 * pi * circ) + r1 ) + cx)
            y = r0 * sin(2 * pi * circ) + cy
            z = (sin( 2 * pi * rot ) *
                 (r0 * cos(2 * pi * circ) + r1))
            
            add_point( points, x, y, z )

            circle+= step
        rotation+= step



def add_circle( points, cx, cy, cz, r, step ):
    x0 = r + cx
    y0 = cy

    t = step
    while t<= 1:
        
        x = r * cos( 2 * pi * t ) + cx
        y = r * sin( 2 * pi * t ) + cy

        add_edge( points, x0, y0, cz, x, y, cz )
        x0 = x
        y0 = y
        t+= step
    add_edge( points, x0, y0, cz, cx + r, cy, cz )

def add_curve( points, x0, y0, x1, y1, x2, y2, x3, y3, step, curve_type ):
    xcoefs = generate_curve_coefs( x0, x1, x2, x3, curve_type )
    ycoefs = generate_curve_coefs( y0, y1, y2, y3, curve_type )
        
    t =  step
    while t <= 1:
        
        x = xcoefs[0][0] * t * t * t + xcoefs[0][1] * t * t + xcoefs[0][2] * t + xcoefs[0][3]
        y = ycoefs[0][0] * t * t * t + ycoefs[0][1] * t * t + ycoefs[0][2] * t + ycoefs[0][3]

        add_edge( points, x0, y0, 0, x, y, 0 )
        x0 = x
        y0 = y
        t+= step

        
def draw_lines(matrix, screen, color, z_buffer):
    if len(matrix) < 2:
        print "Need at least 2 points to draw a line"
    p = 0
    while p < len(matrix) - 1:
        draw_line(screen, matrix[p][0], matrix[p][1], matrix[p][2],
                  matrix[p+1][0], matrix[p+1][1], matrix[p+1][2],
                  z_buffer, color)
        p += 2

        
def add_edge(matrix, x0, y0, z0, x1, y1, z1):
    add_point(matrix, x0, y0, z0)
    add_point(matrix, x1, y1, z1)

    
def add_point(matrix, x, y, z=0):
    matrix.append([x, y, z, 1])


def draw_line(screen, x0, y0, z0, x1, y1, z1, z_buffer, color):
    dx = x1 - x0
    dy = y1 - y0
    dz = 0
    if (dx ** 2 + dy ** 2) != 0:
        dz = (z1 - z0) / (dx * dx + dy * dy) ** (0.5)
    z = z0

    if dx + dy < 0:
        dx = 0 - dx
        dy = 0 - dy
        tmp = x0
        x0 = x1
        x1 = tmp
        tmp = y0
        y0 = y1
        y1 = tmp
        dz = 0 - dz
        z = z1
    
    if dx == 0:
        y = y0
        while y <= y1:
            plot(screen, color, z_buffer, x0, y, z)
            y = y + 1
            z = z + dz
    elif dy == 0:
        x = x0
        while x <= x1:
            plot(screen, color, z_buffer, x, y0, z)
            x = x + 1
            z = z + dz
    elif dy < 0:
        d = 0
        x = x0
        y = y0
        while x <= x1:
            plot(screen, color, z_buffer, x, y, z)
            if d > 0:
                y = y - 1
                d = d - dx
                z = z + 0.41421356 * dz
            x = x + 1
            d = d - dy
            z = z + dz
    elif dx < 0:
        d = 0
        x = x0
        y = y0
        while y <= y1:
            plot(screen, color, z_buffer, x, y, z)
            if d > 0:
                x = x - 1
                d = d - dy
                z = z + 0.41421356 * dz
            y = y + 1
            d = d - dx
            z = z + dz
    elif dx > dy:
        d = 0
        x = x0
        y = y0
        while x <= x1:
            plot(screen, color, z_buffer, x, y, z)
            if d > 0:
                y = y + 1
                d = d - dx
                z = z + 0.41421356 * dz
            x = x + 1
            d = d + dy
            z = z + dz
    else:
        d = 0
        x = x0
        y = y0
        while y <= y1:
            plot(screen, color, z_buffer, x, y, z)
            if d > 0:
                x = x + 1
                d = d - dy
                z = z + 0.41421356 * dz
            y = y + 1
            d = d + dx
            z = z + dz

