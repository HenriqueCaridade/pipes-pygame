# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 16:23:51 2021

@author: Henrique Caridade

Pygame implementation of the game pipes.
https://www.puzzle-pipes.com
"""

import pygame
import numpy as np

pygame.init()

# --- Nodes Management --- #
# Node Type:
# "Receiving_Node / One_Way" -> 0
# "Straight" -> 1
# "Two_Way" -> 2
# "Three_Way" -> 3
# "Four_Way" -> 4
#
# Node Rotation:
# 0º -> 0
# 90º -> 1
# 180º -> 2
# 270º -> 3

POS = ((0, -1), (1, 0), (0, 1), (-1, 0))
NODE_ACCESS = ((), (2,), (1,), (1, 2), (1, 2, 3))

class BlankNode:
    def __init__(self, pos):
        self.pos = pos
        self.rot = 0
        self.type = 0
        self.with_water = False
        self.up = False
        self.down = False
        self.right = False
        self.left = False
        
    def check_connection(mat):
        pass

def clear_water(mat):
    for _ in mat:
        for i in _:
            i.with_water = False
            i.update_image()
    aux = len(mat) // 2
    mat[aux][aux].with_water = True
    mat[aux][aux].update_image()

def def_surrounding_nodes(node, mat):
    aux = []
    for i in POS:
        pos = (node.pos[0] + i[0], node.pos[1] + i[1])
        if in_canvas_matrix(pos, mat):
            aux.append(mat[pos[1]][pos[0]])
        else:
            aux.append(BlankNode(pos))
    node.node_up, node.node_right, node.node_down, node.node_left = aux

class Node:
    def __init__(self, pos, rot, n_type, with_water):
        self.pos = pos
        self.rot = rot 
        self.type = n_type
        self.with_water = with_water
        self.checked = False
        self.image = image_getter(self.type, self.with_water, images_resized)
        aux1 = [True]
        aux2 = list(NODE_ACCESS[self.type % 5])
        for i in range(1, 4):
            if aux2:
                if i == aux2[0]:
                    aux1.append(True)
                    del aux2[0]
                else:
                    aux1.append(False)
            else:
                aux1.append(False)
        aux1 = aux1[4 - self.rot:] + aux1[:4 - self.rot]
        self.up, self.right, self.down, self.left = aux1
        
    def update_image(self):
        self.image = image_getter(self.type, self.with_water, images_resized)
    
    def click(self, mat):
        self.up, self.right, self.down, self.left = self.left, self.up, self.right, self.down
        self.rot = (self.rot + 1) % 4
        clear_water(mat)
        x = len(mat) // 2
        mat[x][x].check_connection(mat)
        
    def check_connection(self, mat):
        self.checked = True
        # Conections
        connections = [self.up and self.node_up.down,
                       self.right and self.node_right.left,
                       self.down and self.node_down.up,
                       self.left and self.node_left.right]
        water_connections = [connections[0] and self.node_up.with_water,
                             connections[1] and self.node_right.with_water,
                             connections[2] and self.node_down.with_water,
                             connections[3] and self.node_left.with_water]
        temp = self.with_water
        if self.type < 5:
            self.with_water = False
            if any(water_connections):
                self.with_water = True
        if self.with_water:
            if connections[0] and not self.node_up.checked:
                self.node_up.check_connection(mat)
            if connections[1] and not self.node_right.checked:
                self.node_right.check_connection(mat)
            if connections[2] and not self.node_down.checked:
                self.node_down.check_connection(mat)
            if connections[3] and not self.node_left.checked:
                self.node_left.check_connection(mat)
        if temp != self.with_water:
            self.image = image_getter(self.type, self.with_water, images_resized)
        self.checked = False

# --- Image Management Functions --- #
def get_images():
    start = ["Receiver_Node", "Straight_Tube", "Two_Way_Tube", "Three_Way_Tube", "Four_Way_Tube"]
    end = ["Without_Water", "With_Water"]
    aux_dict = {}
    for st in start:
        for ed in end:
            aux_dict[st] = aux_dict.get(st, ()) + (pygame.image.load("Images\\" + st + "_" + ed + ".png"),)
    start = ["One_Way", "Straight", "Two_Way", "Three_Way", "Four_Way"]
    for st in start:
        aux_dict[st + "_Source_Node"] = pygame.image.load("Images\\" + st + "_Source_Node.png")
    return aux_dict

def image_getter(n, water, images):
    # 15 images
    # 10 pieces
    # 5 variants
    n %= 10
    
    start1 = ["Receiver_Node", "Straight_Tube", "Two_Way_Tube", "Three_Way_Tube", "Four_Way_Tube"]
    start2 = ["One_Way", "Straight", "Two_Way", "Three_Way", "Four_Way"]
    if n < 5:
        image_i = n
        image_j = int(water)
        image = images[start1[image_i]][image_j]
    else:
        image_i = n - 5
        image = images[start2[image_i] + "_Source_Node"]
    return image

def resize_images(side, images):
    image_size = (side, side)
    start = ["Receiver_Node", "Straight_Tube", "Two_Way_Tube", "Three_Way_Tube", "Four_Way_Tube"]
    # end = ["Without_Water", "With_Water"]
    aux_dict = {}
    for st in start:
        aux_dict[st] = (pygame.transform.scale(images[st][0], image_size),
                        pygame.transform.scale(images[st][1], image_size))
    start = ["One_Way", "Straight", "Two_Way", "Three_Way", "Four_Way"]
    for st in start:
        aux_dict[st + "_Source_Node"] = pygame.transform.scale(images[st + "_Source_Node"], image_size)
    return aux_dict

# Grid Test
def get_default_matrix(side_length):
    center_node_pos = (side_length // 2, side_length // 2)
    matrix = [[Node((i, j), 1, 3, False) if (i,j) != center_node_pos else Node((i,j), 0, 9, True) for i in range(side_length)] for j in range(side_length)]
    for _ in matrix:
        for i in _:
            def_surrounding_nodes(i, matrix)
    return matrix

def get_tubulation(side_length):
    np.random.seed(123456)
    
    matrix = [[None for i in range(side_length)] for j in range(side_length)]
    center_node_pos = (side_length // 2, side_length // 2)
    center_node_type = int(np.random.random() * 4)
    center_node_rot = int(np.random.random() * 4)
    matrix[center_node_pos[0]][center_node_pos[1]] = Node(center_node_pos, center_node_rot, center_node_type)
    stack = [center_node_pos]
    for i in range(1, side_length ** 2):
        curr_pos = stack.pop(0)
        
        available = []
        for i in POS:
            x, y = curr_pos[0] + i[0], curr_pos[1] + i[1]
            if 0 <= x < side_length and 0 <= y < side_length:
                if matrix[y][x] == None:
                    stack.append((x, y))
                    available.append(i)
        
        if available == []:
            node_type = 4
        else:
            node_type = int(np.random.random() * 4)
        node_rot = int(np.random.random() * 4)
        matrix[curr_pos[0]][curr_pos[1]] = Node(curr_pos, node_rot, node_type)
    return matrix

# --- Helper Functions --- #
def input_is_valid(given_input, bounds):
    if given_input:
        num = int(given_input)
        if bounds[0] <= num <= bounds[1]:
            return "Clear"
        else:
            return "OutOfRange"
    return "Length"

def in_canvas_matrix(pos, mat):
    mat_len = len(mat)
    return 0 <= pos[0] < mat_len and 0 <= pos[1] < mat_len

def in_canvas_pixels(ipt):
    left_bounds = grid_origin[0]
    right_bounds = grid_origin[0] + grid_size
    up_bounds = grid_origin[1]
    down_bounds = grid_origin[1] + grid_size
    return left_bounds <= ipt[0] < right_bounds and up_bounds <= ipt[1] < down_bounds

# --- Constants & Variables --- #
SCREEN_SIZE = (1280, 720) # Scalable
COLORS = {"passive": pygame.Color((102, 102, 102)),
          "active": pygame.Color((99, 182, 230)),
          "error": pygame.Color((180, 30, 30)),
          "grid_back": pygame.Color((140, 140, 140)),
          "grid_lines": pygame.Color((200, 200, 200))}
BACKGROUND_COLOR = (64, 64, 64)

grid_size = min(SCREEN_SIZE)
if SCREEN_SIZE[0] <= SCREEN_SIZE[1]:
    grid_origin = (0, (SCREEN_SIZE[1] - SCREEN_SIZE[0]) // 2)
else:
    grid_origin = ((SCREEN_SIZE[0] - SCREEN_SIZE[1]) // 2, 0)
IMAGES = get_images()
images_side_length = 360
grid_size_BOUNDS = (4, 30)

screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SRCALPHA)
pygame.display.set_caption("Pygame Pipes")

TEXTBOX_SIZE = (SCREEN_SIZE[0] // 8, SCREEN_SIZE[1] // 8)
TEXTBOX_POS = (SCREEN_SIZE[0] // 2 - TEXTBOX_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
TEXTBOX_PADDING = TEXTBOX_SIZE[1] // 10
textbox_rect = pygame.Rect(TEXTBOX_POS, TEXTBOX_SIZE)
textbox_color = COLORS["passive"]
textbox_text = ""
textbox_text_color = (255, 255, 255)
textbox_font = pygame.font.Font(None, TEXTBOX_SIZE[1])
textbox_is_active = False

title_text = "PIPES"
title_color = COLORS["passive"]
title_font = pygame.font.Font(None, SCREEN_SIZE[1] // 3)

ERRORS = {"OutOfRange": "[ERROR] The number you typed isn't in the permited range.",
          "Length": "[ERROR] You gave no input.",
          "Clear": ""}
ERROR_MARGIN = SCREEN_SIZE[1] // 120
error_text = ERRORS["Clear"]
error_color = COLORS["error"]
error_font = pygame.font.Font(None, SCREEN_SIZE[1] // 16)

INFO_MARGIN = SCREEN_SIZE[1] // 120
info_text = f"Size must be between {grid_size_BOUNDS[0]} and {grid_size_BOUNDS[1]}."
info_color = COLORS["passive"]
info_font = pygame.font.Font(None, SCREEN_SIZE[1] //12)

credits_text =  "Made by Henrique Caridade"
credits_color = COLORS["passive"]
credits_font = pygame.font.Font(None, SCREEN_SIZE[1] // 8)

grid_back_text = "PIPES"
grid_back_color = COLORS["passive"]
grid_back_font = pygame.font.Font(None, SCREEN_SIZE[1] // 3 * 2)

antialias = True

in_starting_screen = True
running = True

# --- Game Loop --- #
while running:
    # --- Input Management --- #
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
            continue
        if in_starting_screen:
            # --- Starting Screen Inputs --- #
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if textbox_rect.collidepoint(ev.pos):
                    textbox_is_active = True
                else:
                    textbox_is_active = False
            if ev.type == pygame.KEYDOWN:
                if textbox_is_active:
                    if ev.key == pygame.K_BACKSPACE:
                        textbox_text = textbox_text[:-1]
                    elif ev.key == pygame.K_RETURN:
                        input_check = input_is_valid(textbox_text, grid_size_BOUNDS)
                        if input_check == "Clear":
                            ipt = int(textbox_text)
                            in_starting_screen = False
                            error_text = ERRORS["Clear"]
                            
                            images_side_length = grid_size // ipt
                            difference = grid_size % ipt
                            grid_size -= difference
                            grid_origin = (grid_origin[0] + difference // 2, grid_origin[1] + difference // 2)
                            grid_back_rect_screen = pygame.Surface((grid_size, grid_size))
                            grid_back_rect_screen.set_alpha(180)
                            grid_back_rect_screen.fill(COLORS["grid_back"])
                            
                            images_resized = resize_images(images_side_length, IMAGES)
                            game_matrix = get_default_matrix(ipt)
                            x = len(game_matrix) // 2
                            game_matrix[x][x].check_connection(game_matrix)
                        else:
                            error_text = ERRORS[input_check]
                            textbox_text = ""
                    else:
                        char = ev.unicode
                        if char.isnumeric():
                            textbox_text += char
        else:
            # --- Game Screen Inputs --- #
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = ev.pos
                if in_canvas_pixels(mouse_click):    
                    mat_coords = ((mouse_click[0] - grid_origin[0]) // images_side_length,
                                  (mouse_click[1] - grid_origin[1]) // images_side_length,)
                    curr_node = game_matrix[mat_coords[1]][mat_coords[0]]
                    curr_node.click(game_matrix)
                    # for _ in game_matrix:
                    #     for i in _:
                    #         print(int(i.up), int(i.right), int(i.down), int(i.left), int(i.with_water), end = "\t")
                    #     print()
                    # print("--------")
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    in_starting_screen = True
                    grid_size = min(SCREEN_SIZE)
                    if SCREEN_SIZE[0] <= SCREEN_SIZE[1]:
                        grid_origin = (0, (SCREEN_SIZE[1] - SCREEN_SIZE[0]) // 2)
                    else:
                        grid_origin = ((SCREEN_SIZE[0] - SCREEN_SIZE[1]) // 2, 0)
    
    # --- Display Screen --- #
    screen.fill(BACKGROUND_COLOR)
    
    if in_starting_screen:
        # --- Starting Screen --- #
        
        # Text Box Color
        if textbox_is_active:
            textbox_color = COLORS["active"]
        else:
            textbox_color = COLORS["passive"]
        
        # Title
        title_surface = title_font.render(title_text, antialias, title_color)
        screen.blit(title_surface, ((SCREEN_SIZE[0] - title_surface.get_width()) // 2,
                                    SCREEN_SIZE[1] // 8))
        
        # Text Box
        pygame.draw.rect(screen, textbox_color, textbox_rect)
        textbox_surface = textbox_font.render("Size: " + textbox_text, antialias, textbox_text_color)
        textbox_rect.w = max(TEXTBOX_SIZE[0], textbox_surface.get_width() + TEXTBOX_PADDING * 2)
        textbox_rect.left = (SCREEN_SIZE[0] - textbox_rect.width) // 2
        textbox_surface_pos = (textbox_rect.left + TEXTBOX_PADDING, textbox_rect.bottom - textbox_surface.get_height() - TEXTBOX_PADDING)
        screen.blit(textbox_surface, textbox_surface_pos)
        
        # Info
        info_surface = info_font.render(info_text, antialias, info_color)
        screen.blit(info_surface, ((SCREEN_SIZE [0] - info_surface.get_width()) // 2,
                                    textbox_rect.top - info_surface.get_height() - INFO_MARGIN))
        
        # Error Message
        error_surface = error_font.render(error_text, antialias, error_color)
        screen.blit(error_surface, ((SCREEN_SIZE [0] - error_surface.get_width()) // 2,
                                    textbox_rect.bottom + ERROR_MARGIN))
        
        # Credits
        credits_surface = credits_font.render(credits_text, antialias, credits_color)
        screen.blit(credits_surface, ((SCREEN_SIZE[0] - credits_surface.get_width()) // 2,
                                    SCREEN_SIZE[1] // 8 * 6))
        
    else:
        # --- Game Screen --- #
        
        # PIPES Text Behind Grid
        grid_back_surface = grid_back_font.render(grid_back_text, antialias, grid_back_color)
        screen.blit(grid_back_surface, ((SCREEN_SIZE[0] - grid_back_surface.get_width()) // 2,
                                        (SCREEN_SIZE[1] - grid_back_surface.get_height()) // 2))
        
        # Grid Background
        screen.blit(grid_back_rect_screen, grid_origin)
        
        # Grid
        for x in range(grid_origin[0], grid_origin[0] + grid_size + 1, images_side_length):
            pygame.draw.line(screen, COLORS["grid_lines"], (x, grid_origin[1]), (x, grid_origin[1] + grid_size))
        for y in range(grid_origin[1], grid_origin[1] + grid_size + 1, images_side_length):
            pygame.draw.line(screen, COLORS["grid_lines"], (grid_origin[0], y), (grid_origin[0] + grid_size, y))
        
        # Display Game Matrix
        for row in game_matrix:
            for item in row:
                image = item.image
                image = pygame.transform.rotate(image, - 90 * item.rot)
                image_pos = (grid_origin[0] + item.pos[0] * images_side_length,
                             grid_origin[1] + item.pos[1] * images_side_length)
                screen.blit(image, image_pos)
        
    # Center Check
    # pygame.draw.circle(screen, (0, 0, 0), (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2), 5)
    
    # Refresh Screen
    pygame.display.flip()
    
pygame.quit()
