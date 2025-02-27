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
animation = None

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

def parse_color(script):
    global color
    if script[0][0] == '#':
        if len(script[0]) - 1 not in [3, 4, 6, 8]:
            raise Exception('Bad color hex: ' + script[0])
        color = script[0]
        return 1
    if script[0].lower() == 'rgb':
        r = parse_int([script[1]])
        g = parse_int([script[2]])
        b = parse_int([script[3]])
        color = 'rgb(' + ','.join(list(map(str, [r, g, b]))) + ')'
        return 4
    if script[0].lower() == 'rgba':
        r = parse_int([script[1]])
        g = parse_int([script[2]])
        b = parse_int([script[3]])
        a = parse_int([script[4]])
        color = 'rgba(' + ','.join(list(map(str, [r, g, b, a]))) + ')'
        return 5
    try:
        ImageColor.getcolor(script[0], 'RGBA')
        color = script[0]
        return 1
    except:
        raise Exception('Expected color, got: ' + script[0])

def parse_int(script):
    text = script[0]
    if text[0] == '$':
        if len(stack) > 0:
            n = 1
            if len(script[0]) > 1:
                n = int(script[0][1:])
            text = stack[len(stack) - n]
        else:
            text = '0'
    try:
        v = int(text)
        return v
    except:
        raise Exception('Excepted int, but got: ' + text)

def parse_vec2(script):
    x = parse_int([script[0]])
    y = parse_int([script[1]])
    return (x, y)

def parse_string(script):
    if script[0][0] == '"':
        i = 0
        out = []
        while i < len(script) and not script[i].endswith('"'):
            out.append(script[i])
            i +=  1
        if i >= len(script):
            raise Exception('Tried to parse string, but did not found end...')
        out.append(script[i])
        out[0] = out[0][slice(1, len(out[0]))]
        if out[len(out) - 1].endswith('"'):
            out[len(out) - 1] = out[len(out) - 1][slice(0, -1)]
        return out
    elif script[0][0] == '$':
        if len(stack) > 0:
            n = 1
            if len(script[0]) > 1:
                n = int(script[0][1:])
            return [str(stack[len(stack) - n])]
        else:
            return ['NULL']
    else:
        return [script[0]]

def unwrap_string(text):
    return ' '.join(text).replace('\\w', ' ').replace('\\n', '\n').replace('\\\\', '\\')

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
    global animation

    image = None
    color = 'black'
    width = 1
    anchor = 'la'
    align = 'left'
    font = 'comic.ttf'
    mode = 'fill'
    cursor = (0, 0)

    stack = []
    animation = None
    scope = 0
    
    if input_file is None:
        return
    
    script = ''
    with open(input_file, 'r') as script_file:
        script = script_file.read()

    script = script.split()

    WxH = script[0].split('x')
    if not len(WxH) == 2:
        raise Exception('Excepted first token to be in format WxH to describe the image size.')

    WxH = list(map(int, WxH))
    
    image = Image.new('RGB', (WxH[0], WxH[1]))
    draw = ImageDraw.Draw(image, 'RGBA')

    i = 1
    while i < len(script):
        print(script[i])
        # Coments
        if script[i][0] == '#':
            text = parse_string(script[slice(i + 1, len(script))])
            i += len(text) + 1
            print(' '.join(text))
            continue
        match script[i]:
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
                i += parse_color(script[slice(i + 1, len(script))])
            case 'width':
                width = parse_int(script[slice(i + 1, len(script))])
                i += 1
            case 'anchor':
                vertical = script[i + 1].lower()
                horizontal = script[i + 2].lower()
                i += 2
                if vertical not in ['left', 'middle', 'right', 'l', 'm', 'r']:
                    raise Exception('Bad vertical anchor, got: ' + vertical)
                if horizontal not in ['ascender', 'top', 'middle', 'baseline', 'bottom', 'descender', 'a', 't', 'm', 's', 'b', 'd']:
                    raise Exception('Bad horizontal anchor, got: ' + horizontal)
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
                print((vertical, horizontal), anchor)
            case 'align':
                align = script[i + 1].lower()
                i += 1
                if align not in ['left', 'center', 'right']:
                    raise Exception('Bad aligment, got: ' + align)
            case 'font':
                text = parse_string(script[slice(i + 1, len(script))])
                i += len(text)
                text = unwrap_string(text)
                font = text
            case 'mode':
                script[i + 1] = script[i + 1].lower()
                if script[i + 1] in ['fill', 'outline']:
                    mode = script[i + 1]
                    i += 1
                else:
                    raise Exception('Bad mode name: ' + script[i + 1])
            case 'cursor':
                cursor = parse_vec2(script[slice(i + 1, len(script))])
                i += 2
            case 'move':
                (x, y) = parse_vec2(script[slice(i + 1, len(script))])
                i += 2
                (cx, cy) = cursor
                cursor = (cx + x, cy + y)
            # Drawing
            case 'line':
                p = parse_vec2(script[slice(i + 1, len(script))])
                i += 2
                draw.line([cursor, p], fill=color, width=width)
            case 'rectangle':
                (w, h) = parse_vec2(script[slice(i + 1, len(script))])
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
                (w, h) = parse_vec2(script[slice(i + 1, len(script))])
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
                (w, h) = parse_vec2(script[slice(i + 1, len(script))])
                i += 2
                (start, end) = parse_vec2(script[slice(i + 1, len(script))])
                i += 2
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
                text = parse_string(script[slice(i + 1, len(script))])
                i += len(text)
                text = unwrap_string(text)
                f = ImageFont.truetype(font, width)
                draw.multiline_text(cursor, text, fill=color, anchor=anchor, align=align, font=f, font_size=width)
            case 'image':
                text = parse_string(script[slice(i + 1, len(script))])
                i += len(text)
                text = unwrap_string(text)
                img = Image.open(text)
                image = image.convert('RGBA')
                image.alpha_composite(img.convert('RGBA'), dest=cursor)
                image = image.convert('RGB')
                draw = ImageDraw.Draw(image, 'RGBA')
            # Stack
            case 'push':
                text = parse_string(script[slice(i + 1, len(script))])
                i += len(text)
                text = ' '.join(text)
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
                b = parse_int([script[i + 1]])
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
                b = parse_int([script[i + 1]])
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
                b = parse_int([script[i + 1]])
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
                b = parse_int([script[i + 1]])
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
                b = parse_int([script[i + 1]])
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
                b = parse_string(script[slice(i + 1, len(script))])
                i += len(b)
                b = ' '.join(b).replace('\\w', ' ').replace('\\n', '\n').replace('\\\\', '\\')
                stack.append(a + b)
            # Logic
            case 'eq':
                if len(stack) < 2:
                    raise Exception('Not enought elements on stack to perform eq.')
                a = int(stack.pop(len(stack) - 1))
                b = int(stack.pop(len(stack) - 1))
                stack.append(1 if a == b else 0)
            case 'eqv':
                if len(stack) < 1:
                    raise Exception('Not enought elements on stack to perform eqv.')
                a = int(stack.pop(len(stack) - 1))
                b = parse_int([script[i + 1]])
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
                b = parse_int([script[i + 1]])
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
                b = parse_int([script[i + 1]])
                i += 1
                stack.append(1 if a < b else 0)
            # Control-flow
            case '{':
                scope += 1
            case '}':
                if scope <= 0:
                    raise Exception('Cannot close global scope.')
                scope -= 1
            case 'if':
                (a, b) = parse_vec2(script[slice(i + 1, len(script))])
                i += 2
                if not a == b:
                    i += 1
                    if script[i] == '{':
                        x = 1
                        i += 1
                        while i < len(script) and not x == 0:
                            print(script[i])
                            if script[i] == '}':
                                x -= 1
                                i += 1
                            elif script[i] == '{':
                                x += 1
                                i += 1
                            else:
                                i += len(parse_string(script[slice(i, len(script))]))
                        if i >= len(script) and not script[i - 1] == '}':
                            raise Exception('Found unclosed scope')
                        if script[i] == 'else':
                            i += 1
                        i -= 1
            case 'else':
                i += 1
                if script[i] == '{':
                    x = 1
                    i += 1
                    while i < len(script) and not x == 0:
                        print(script[i])
                        if script[i] == '}':
                            x -= 1
                            i += 1
                        elif script[i] == '{':
                            x += 1
                            i += 1
                        else:
                            i += len(parse_string(script[slice(i, len(script))]))
                    if i >= len(script) and not script[i - 1] == '}':
                        raise Exception('Found unclosed scope')
                    i -= 1
            # Animation
            case 'animation':
                if animation is not None:
                    raise Exception('Cannot define animation inside alrady animated image.')
                n = parse_int(script[slice(i + 1, len(script))])
                duration = parse_int(script[slice(i + 2, len(script))])
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
