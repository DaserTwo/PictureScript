# TKinter should be installed out of the box with python3
# However, you need pillow package to load images diferent than .gif
# $ pip install pillow

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import ImageTk, Image, ImageDraw, ImageColor, ImageFont

input_file = None
output_file = None

image = None
color = 'black'
width = 1
anchor = 'la'
align = 'left'
font = 'comic.ttf'
mode = 'fill'
cursor = (0, 0)

stack = []
variables = {}
animation = None
labels = {}

class Animation:
    def __init__(self, image, i, duration, n):
        self.base = image
        self.i = i
        self.duration = duration
        self.n = n
        self.iota = 0
        self.frames = []
    def next(self, frame):
        self.frames.append(frame)
        self.iota += 1
        return self.base.copy()

class Token:
    def __init__(self, type, text):
        self.type = type
        self.text = text
    def __str__(self):
        return 'Token{' + self.type + ': ' + self.text + '}'

def load_script():
    global input_file
    
    file_types = (
        ('Image Script', '*.picturescript'),
        ('Text file', '*.txt'),
        ('All files', '*.*')
    )
    input_file = fd.askopenfilename(title='Load image script', filetypes=file_types)
    label_text_var.set(input_file)
    render_img()
    show_img()

def save_as():
    global output_file

    file_types = (
        ('PNG', '*.png'),
        ('JPG', '*.jpg'),
        ('GIF', '*.gif'),
        ('All files', '*.*')
    )
    output_file = fd.asksaveasfilename(defaultextension='.png', filetypes=file_types)
    save_render()

def save_render():
    global output_file
    
    if output_file is None:
        save_as()
        return
    
    if animation is not None:
        animation.frames[0].save(output_file, save_all=True, append_images=animation.frames[1:], optimize=False, duration=animation.duration, loop=0)
    elif image is not None:
        with open(output_file, 'wb') as of:
            image.save(of)

def fit_image(width, height, max_width, max_height):
    if width > max_width:
        ratio = height / width
        width = max_width
        height = round(ratio * max_width)
    if height > max_height:
        ratio = width / height
        width = round(ratio * max_height)
        height = max_height
    #if width < max_width and height < max_height:
    #    if width > height:
    #        ratio = height / width
    #        width = max_width
    #        height = round(ratio * max_width)
    #    else:
    #        ratio = width / height
    #        width = round(ratio * max_height)
    #        height = max_height
    return (width, height)

def show_img():
    global image
    global image_photo
    global image_id
    
    try:
        canvas.delete(image_id)
        del image_id
    except:
        pass
    
    render_img()
    if image is not None:
        image_photo = ImageTk.PhotoImage(image.resize(fit_image(image.width, image.height, canvas.winfo_width(), canvas.winfo_height())))
        image_id = canvas.create_image(0, 0, anchor=tk.NW, image=image_photo)

def get_stack(text):
    n = 1
    if len(text) > 1:
        n = int(text[1:])
    if len(stack) < n:
        return 'NULL'
    return stack[len(stack) - n]

def parse_int(i, script):
    if script[i].type == 'NUM':
        return int(script[i].text)
    elif script[i].type == '$':
        text = get_stack(script[i].text)
        if text == 'NULL':
            return 0
        try:
            return int(text)
        except:
            raise Exception('Excepted int, but got (stack): ' + text)
    else:
        raise Exception('Excepted int, but got: ' + str(script[i]))

def parse_vec2(i, script):
    x = parse_int(i, script)
    y = parse_int(i + 1, script)
    return (x, y)

def parse_vec3(i, script):
    x = parse_int(i, script)
    y = parse_int(i + 1, script)
    z = parse_int(i + 2, script)
    return (x, y, z)

def parse_vec4(i, script):
    x = parse_int(i, script)
    y = parse_int(i + 1, script)
    z = parse_int(i + 2, script)
    w = parse_int(i + 3, script)
    return (x, y, z, w)

def parse_color(i, script):
    if i >= len(script):
        raise Exception('Excepted color, but reach EOF.')

    if script[i].type == 'COL':
        color = script[i].text
        return (1, color)
    if script[i].type == 'ID':
        if script[i].text.lower() == 'rgb':
            (r, g, b) = parse_vec3(i + 1, script)
            color = 'rgb(' + ','.join(list(map(str, [r, g, b]))) + ')'
            return (4, color)
        if script[i].text.lower() == 'rgba':
            (r, g, b, a) = parse_vec4(i + 1, script)
            color = 'rgba(' + ','.join(list(map(str, [r, g, b, a]))) + ')'
            return (5, color)
    try:
        text = script[i].text
        if script[i].type == '$':
            text = get_stack(text)
        ImageColor.getcolor(text, 'RGBA')
        color = text
        return (1, color)
    except:
        raise Exception('Expected color, got: ' + text)

def parse_string(i, script):
    if script[i].type in ['ID', 'STR']:
        return script[i].text
    elif script[i].type == '$':
        return str(get_stack(script[i].text))
    else:
        raise Exception('Excepted string, but got: ' + str(script[i]))

def parse_special(i, script, accept):
    if script[i].type in ['ID', 'STR', '$']:
        text = script[i].text.lower()
        if script[i].type == '$':
            text = get_stack(text)
        if text in accept:
            return text
        else:
            raise Exception('Unexpected special, got: ' + str(script[i]) + ', but expected one of: ' + str(accept))
    else:
        raise Exception('Unexpected token: ' + str(script[i]))

def parse_any(i, script):
    if script[i].type in ['ID', 'STR', 'NUM', 'COL']:
        return script[i].text
    elif script[i].type == '$':
        return get_stack(script[i].text)
    else:
        raise Exception('Excepted ANY, but got: ' + str(script[i]))

def is_valid_id(c):
    return c.isalnum() or c in ['-', '_', '+', '=', '*', '&', '^', '%', '!', '|', ':', ';', '.', ',', '?', '<', '>', '~']

def tokenize(script):
    global labels
    labels = {}

    tokens = []
    count = len(script)
    i = 0
    while i < count:
        while i < count and script[i].isspace():
            i += 1
        if i >= count:
            break
        elif is_valid_id(script[i]):
            tok = ''
            while i < count and is_valid_id(script[i]):
                tok += script[i]
                i += 1
            tokens.append(Token('NUM' if tok.isnumeric() or (tok[0] == '-' and tok[1:].isnumeric()) else 'ID', tok))
        elif script[i] == '"':
            tok = ''
            i += 1
            while i < count and not script[i] == '"':
                if script[i] == '\\' and i + 1 < count:
                    match script[i + 1]:
                        case 'w':
                            tok += ' '
                        case 't':
                            tok += '\t'
                        case '"':
                            tok += '"'
                        case 'n':
                            tok += '\n'
                        case 'r':
                            tok += '\r'
                        case '\\':
                            tok += '\\'
                        case _:
                            tok += '\\'
                            i -= 1
                    i += 1
                else:
                    tok += script[i]
                i += 1
            if not script[i] == '"':
                raise Exception('Found not ending string.')
            tokens.append(Token('STR', tok))
        elif script[i] == '$':
            tok = '$'
            i += 1
            while i < count and script[i].isnumeric():
                tok += script[i]
                i += 1
            tokens.append(Token('$', tok))
            continue
        elif script[i] == '#':
            tok = '#'
            i += 1
            while i < count and (script[i].isnumeric() or script[i].lower() in ['a', 'b', 'c', 'd', 'e', 'f']):
                tok += script[i]
                i += 1
            if len(tok) == 1:
                tokens.append(Token('#', tok))
            elif len(tok) in [4, 5, 7, 9]:
                tokens.append(Token('COL', tok))
            else:
                raise Exception('Bad token, expected COLOR or comment but got: ' + tok)
            continue
        elif script[i] == '@':
            tok = '@'
            i += 1
            while i < count and is_valid_id(script[i]):
                tok += script[i]
                i += 1
            if len(tok) == 1:
                raise Exception('Unnamed labels are not supported')
            if tok in labels:
                raise Exception('Cannot define two labels with the same name: ' + tok)
            labels[tok] = len(tokens)
            continue
        elif script[i] in ['{', '}']:
            tokens.append(Token(script[i], script[i]))
        else:
            raise Exception('Unparsable: ' + script[i])
        i += 1
    return tokens

def render_img():
    global image
    global color
    global width
    global anchor
    global align
    global font
    global mode
    global cursor
    global stack
    global variables
    global animation
    global labels

    image = None
    color = 'black'
    width = 1
    anchor = 'la'
    align = 'left'
    font = 'comic.ttf'
    mode = 'fill'
    cursor = (0, 0)

    stack = []
    variables = {}
    animation = None
    scope = 0
    
    if input_file is None:
        return
    
    script = ''
    with open(input_file, 'r') as script_file:
        script = script_file.read()

    script = tokenize(script)

    WxH = script[0].text.split('x')
    if not len(WxH) == 2:
        raise Exception('Excepted first token to be in format WxH to describe the image size.')

    WxH = list(map(int, WxH))
    
    image = Image.new('RGB', (WxH[0], WxH[1]))
    draw = ImageDraw.Draw(image, 'RGBA')

    i = 1
    while i < len(script):
        print(script[i])
        
        match script[i].type:
            case '#':
                text = script[i + 1].text
                print(text)
                i += 2
                continue
            case '{':
                scope += 1
                i += 1
                continue
            case '}':
                if scope <= 0:
                    raise Exception('Cannot close global scope.')
                scope -= 1
                i += 1
                continue
            case 'ID':
                pass
            case _:
                raise Exception('Unexpected token: ' + str(script[i]))
        match script[i].text:
            # State
            case 'reset':
                color = 'black'
                width = 1
                anchor = 'la'
                align = 'left'
                font = 'comic.ttf'
                mode = 'fill'
                cursor = (0, 0)
            case 'color':
                (n, c) = parse_color(i + 1, script)
                color = c
                i += n
            case 'width':
                width = parse_int(i + 1, script)
                i += 1
            case 'anchor':
                vertical = parse_special(i + 1, script, ['left', 'middle', 'right', 'l', 'm', 'r'])
                horizontal = parse_special(i + 2, script, ['ascender', 'top', 'middle', 'baseline', 'bottom', 'descender', 'a', 't', 'm', 's', 'b', 'd'])
                i += 2
                match vertical:
                    case 'left':
                        anchor = 'l'
                    case 'middle':
                        anchor = 'm'
                    case 'right':
                        anchor = 'r'
                    case _:
                        anchor = vertical
                match horizontal:
                    case 'ascender':
                        anchor += 'a'
                    case 'top':
                        anchor += 't'
                    case 'middle':
                        anchor += 'm'
                    case 'baseline':
                        anchor += 's'
                    case 'bottom':
                        anchor += 'b'
                    case 'descender':
                        anchor += 'd'
                    case _:
                        anchor += horizontal
            case 'align':
                align = parse_special(i + 1, script, ['left', 'center', 'right'])
                i += 1
            case 'font':
                font = parse_string(i + 1, script)
                i += 1
            case 'mode':
                mode = parse_special(i + 1, script, ['fill', 'outline'])
                i += 1
            case 'cursor':
                cursor = parse_vec2(i + 1, script)
                i += 2
            case 'move':
                (x, y) = parse_vec2(i + 1, script)
                i += 2
                (cx, cy) = cursor
                cursor = (cx + x, cy + y)
            # Drawing
            case 'line':
                p = parse_vec2(i + 1, script)
                i += 2
                draw.line([cursor, p], fill=color, width=width)
            case 'rectangle':
                (w, h) = parse_vec2(i + 1, script)
                i += 2
                (x, y) = cursor
                match mode:
                    case 'fill':
                        draw.rectangle([(x, y), (x + w, y + h)], fill=color, width=width)
                    case 'outline':
                        draw.rectangle([(x, y), (x + w, y + h)], outline=color, width=width)
                    case _:
                        raise Exception('Unreachable: Bad mode: ' + mode)
            case 'ellipse':
                (w, h) = parse_vec2(i + 1, script)
                i += 2
                (x, y) = cursor
                match mode:
                    case 'fill':
                        draw.ellipse([(x, y), (x + w, y + h)], fill=color, width=width)
                    case 'outline':
                        draw.ellipse([(x, y), (x + w, y + h)], outline=color, width=width)
                    case _:
                        raise Exception('Unreachable: Bad mode: ' + mode)
            case 'arc':
                (w, h, start, end) = parse_vec4(i + 1, script)
                i += 4
                (x, y) = cursor
                match mode:
                    case 'fill':
                        draw.pieslice([(x, y), (x + w, y + h)], start, end, fill=color, width=width)
                    case 'outline':
                        #draw.pieslice([(x, y), (x + w, y + h)], start, end, outline=color, width=width)
                        draw.arc([(x, y), (x + w, y + h)], start, end, fill=color, width=width)
                    case _:
                        raise Exception('Unreachable: Bad mode: ' + mode)
            case 'text':
                text = parse_string(i + 1, script)
                i += 1
                f = ImageFont.truetype(font, width)
                draw.multiline_text(cursor, text, fill=color, anchor=anchor, align=align, font=f, font_size=width)
            case 'image':
                text = parse_string(i + 1, script)
                i += 1
                img = Image.open(text)
                image = image.convert('RGBA')
                image.alpha_composite(img.convert('RGBA'), dest=cursor)
                image = image.convert('RGB')
                draw = ImageDraw.Draw(image, 'RGBA')
            # Stack
            case 'push':
                text = parse_any(i + 1, script)
                i += 1
                stack.append(text)
            case 'pop':
                if len(stack) > 0:
                    stack.pop(len(stack) - 1)
            case 'dup':
                if len(stack) < 1:
                    raise Exception('Not enought elements on stack to perform dup.')
                stack.append(stack[len(stack) - 1])
            case 'swap':
                if len(stack) < 2:
                    raise Exception('Not enought elements on stack to perform swap.')
                a = stack.pop(len(stack) - 1)
                b = stack.pop(len(stack) - 1)
                stack.append(a)
                stack.append(b)
            case 'rot':
                if len(stack) < 3:
                    raise Exception('Not enought elements on stack to perform rot.')
                a = stack.pop(len(stack) - 1)
                b = stack.pop(len(stack) - 1)
                c = stack.pop(len(stack) - 1)
                stack.append(a)
                stack.append(c)
                stack.append(b)
            # Variables
            case 'set':
                name = parse_string(i + 1, script)
                value = parse_any(i + 2, script)
                i += 2
                variables[name] = value
            case 'get':
                name = parse_string(i + 1, script)
                i += 1
                stack.append(variables[name])
            # Math
            case 'add':
                if len(stack) < 2:
                    raise Exception('Not enought elements on stack to perform add.')
                a = int(stack.pop(len(stack) - 1))
                b = int(stack.pop(len(stack) - 1))
                stack.append(a + b)
            case 'addv':
                if len(stack) < 1:
                    raise Exception('Not enought elements on stack to perform addv.')
                a = int(stack.pop(len(stack) - 1))
                b = parse_int(i + 1, script)
                i += 1
                stack.append(a + b)
            case 'sub':
                if len(stack) < 2:
                    raise Exception('Not enought elements on stack to perform sub.')
                a = int(stack.pop(len(stack) - 1))
                b = int(stack.pop(len(stack) - 1))
                stack.append(a - b)
            case 'subv':
                if len(stack) < 1:
                    raise Exception('Not enought elements on stack to perform subv.')
                a = int(stack.pop(len(stack) - 1))
                b = parse_int(i + 1, script)
                i += 1
                stack.append(a - b)
            case 'mul':
                if len(stack) < 2:
                    raise Exception('Not enought elements on stack to perform mul.')
                a = int(stack.pop(len(stack) - 1))
                b = int(stack.pop(len(stack) - 1))
                stack.append(a * b)
            case 'mulv':
                if len(stack) < 1:
                    raise Exception('Not enought elements on stack to perform mulv.')
                a = int(stack.pop(len(stack) - 1))
                b = parse_int(i + 1, script)
                i += 1
                stack.append(a * b)
            case 'div':
                if len(stack) < 2:
                    raise Exception('Not enought elements on stack to perform div.')
                a = int(stack.pop(len(stack) - 1))
                b = int(stack.pop(len(stack) - 1))
                stack.append(a // b)
            case 'divv':
                if len(stack) < 1:
                    raise Exception('Not enought elements on stack to perform divv.')
                a = int(stack.pop(len(stack) - 1))
                b = parse_int(i + 1, script)
                i += 1
                stack.append(a // b)
            case 'mod':
                if len(stack) < 2:
                    raise Exception('Not enought elements on stack to perform mod.')
                a = int(stack.pop(len(stack) - 1))
                b = int(stack.pop(len(stack) - 1))
                stack.append(a % b)
            case 'modv':
                if len(stack) < 1:
                    raise Exception('Not enought elements on stack to perform modv.')
                a = int(stack.pop(len(stack) - 1))
                b = parse_int(i + 1, script)
                i += 1
                stack.append(a % b)
            # String
            case 'cat':
                if len(stack) < 2:
                    raise Exception('Not enought elements on stack to perform cat.')
                a = str(stack.pop(len(stack) - 1))
                b = str(stack.pop(len(stack) - 1))
                stack.append(a + b)
            case 'catv':
                if len(stack) < 1:
                    raise Exception('Not enought elements on stack to perform catv.')
                a = str(stack.pop(len(stack) - 1))
                b = parse_string(i + 1, script)
                i += 1
                stack.append(a + b)
            # Logic
            case 'eq':
                if len(stack) < 2:
                    raise Exception('Not enought elements on stack to perform eq.')
                a = str(stack.pop(len(stack) - 1))
                b = str(stack.pop(len(stack) - 1))
                stack.append(1 if a == b else 0)
            case 'eqv':
                if len(stack) < 1:
                    raise Exception('Not enought elements on stack to perform eqv.')
                a = str(stack.pop(len(stack) - 1))
                b = parse_any(i + 1, script)
                i += 1
                stack.append(1 if a == b else 0)
            case 'gt':
                if len(stack) < 2:
                    raise Exception('Not enought elements on stack to perform gt.')
                a = int(stack.pop(len(stack) - 1))
                b = int(stack.pop(len(stack) - 1))
                stack.append(1 if a > b else 0)
            case 'gtv':
                if len(stack) < 1:
                    raise Exception('Not enought elements on stack to perform gtv.')
                a = int(stack.pop(len(stack) - 1))
                b = parse_int(i + 1, script)
                i += 1
                stack.append(1 if a > b else 0)
            case 'lt':
                if len(stack) < 2:
                    raise Exception('Not enought elements on stack to perform lt.')
                a = int(stack.pop(len(stack) - 1))
                b = int(stack.pop(len(stack) - 1))
                stack.append(1 if a < b else 0)
            case 'ltv':
                if len(stack) < 1:
                    raise Exception('Not enought elements on stack to perform ltv.')
                a = int(stack.pop(len(stack) - 1))
                b = parse_int(i + 1, script)
                i += 1
                stack.append(1 if a < b else 0)
            # Control-flow
            case 'if':
                (a, b) = parse_vec2(i + 1, script)
                i += 2
                if not a == b:
                    i += 1
                    if script[i].type == '{':
                        x = 1
                        i += 1
                        while i < len(script) and not x == 0:
                            print(script[i])
                            if script[i].type == '}':
                                x -= 1
                            elif script[i].type == '{':
                                x += 1
                            i += 1
                        if i >= len(script):
                            if not script[i - 1].type == '}':
                                raise Exception('Found unclosed scope')
                            else:
                                continue
                        if script[i].type == 'ID' and script[i].text == 'else':
                            i += 1
                        continue
            case 'else':
                i += 1
                if script[i].type == '{':
                    x = 1
                    i += 1
                    while i < len(script) and not x == 0:
                        print(script[i])
                        if script[i].type == '}':
                            x -= 1
                        elif script[i].type == '{':
                            x += 1
                        i += 1
                    if i >= len(script) and not script[i - 1].type == '}':
                        raise Exception('Found unclosed scope')
                    continue
            case 'goto':
                label = parse_string(i + 1, script)
                i = labels['@' + label]
                continue
            case 'jump':
                ni = parse_int(i + 1, script)
                i = ni
                continue
            case 'label':
                label = parse_string(i + 1, script)
                i += 1
                stack.append(labels['@' + label])
            # Animation
            case 'animation':
                if animation is not None:
                    raise Exception('Cannot define animation inside alrady animated image.')
                (n, duration) = parse_vec2(i + 1, script)
                i += 2
                animation = Animation(image.copy(), i + 1, duration, n)
            case 'iota':
                if animation is None:
                    raise Exception('Cannot get iota without animation context...')
                stack.append(animation.iota)
            case 'n':
                if animation is None:
                    raise Exception('Cannot get frame count (n) without animation context...')
                stack.append(animation.n)
            case _:
                raise Exception('Unsupported command: ' + script[i])
        i += 1
        print(stack)
        if i >= len(script) and animation is not None and animation.iota < animation.n:
            i = animation.i
            image = animation.next(image)
            draw = ImageDraw.Draw(image, 'RGBA')

# Create window
root_tk = tk.Tk()
root_tk.geometry('800x600')
root = ttk.Frame(root_tk)
root.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

label_text_var = tk.StringVar(value='No script to render')
ttk.Label(root, textvariable=label_text_var).grid(row=0, column=0)

canvas = tk.Canvas(root, bg='black')
canvas.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

button_frame = ttk.Frame(root)
button_frame.grid(row=2, column=0)

ttk.Button(button_frame, text='Load', command=load_script).grid(row=0, column=0)
ttk.Button(button_frame, text='Reload', command=show_img).grid(row=0, column=1)
ttk.Button(button_frame, text='Save', command=save_render).grid(row=0, column=2)
ttk.Button(button_frame, text='Save As', command=save_as).grid(row=0, column=3)

# Configure resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

root_tk.columnconfigure(0, weight=1)
root_tk.rowconfigure(0, weight=1)

# Auto-resizing of image
canvas.bind('<Configure>', lambda event: show_img())

# Main loop
root_tk.mainloop()
