# ImageScript

ImageScript is a simple scripting language written for images' descripting. It can also describe animations, but it's experimental feature.
To generate actual picture use pnggen.py, it is a GUI application that depends on tkinter and pillow, but proper CLI tool will come in its own time.

## Syntax

One important think is that this language is token-based and has no AST. A token is separated by white-characters like space, tab or new-line, except from strings that are parsed from double-quote to double-quote including escaping.
The first token must be in a form WxH where W and H are integers and x is literal 'x', this describes width (W) and height (H) of the output.
Next tokens may be commands or values. A value must be an argument for a command, stand-alone values are considered syntax errors.
The basic syntax is a command as the first token and its arguments as following ones.

## State

A state is a set of variables, a stack, an image and animation. Some commands modify the state, some operate on the stack and some are using the state to draw on image or initialize an animation.
There are also special commands that work as coments or changes the control-flow. The following are the state vaiables and defaults:
- color = 'black'
- width = 1
- anchor = 'la'
- align = 'left'
- font = 'comic.ttf'
- mode = 'fill'
- cursor = (0, 0)

## Values

A value in ImageScript may be one of the following:
- literal integer (may be nagative), f.e. 1, 100, -55
- literal string, an not-formated id or a formated string surrounded with double-quotes. There are simple escape sequences: \n (new-line), \r (carriage-return), \t (tab), \w (space) and \\ (slash). Examples: HelloWorld, Hello-World, "Hello World", "Hello\wWorld"
- literal color, may be one token with a name, any valid CSS hex (like #333, also with aplha #1234) or rgb with three folowing integers (0-255 each), or rgba with four following integers.
- stack variables, a dollar ($) is considered the top-most value on the stack or 0 (when expected integer) or NULL (when expected string), when after a dollar there is an integer ($N), it will become Nth element on the stack or 0 or NULL.

## Commands

There are several types of commands: coments, state, drawing, stack, variables, match, string, logic, control-flow and animation commands.
The command arguments will be given in a form [NAME:TYPE] there NAME will be used later in description and TYPE is one of these: INT, STRING, COLOR, ANY or a keyword-list separated by '|'.

### The coment command (# [s:ANY])

A hash (#) is a comment command, it takes one token tat will be ignored. The s is printed on the console output.

``` ImageScript
# comment
# "This'll be printed"
```

### State commands

#### reset

This comand resets all the state variables to defaults.

``` ImageScript
# "Change cursor position"
cursor 10 10
# "Reset it back to (0, 0)"
reset
```

#### color [c:COLOR]

Sets the color state variable to c.

``` ImageScript
# "Change the color"
color red
# "Draw a red rectangle"
rectangle 20 10
```

#### width [w:INT]

Sets the width state variable to w. It affects both the font-size and the stroke width.

``` ImageScript
# "Change the width"
width 20
# "Change mode to outline"
mode outline
# "Draw a square"
rectangle 50 50
# "Draw a text"
text "My font-size is 20px, cool!"
```

#### anchor [v:left|middle|right|l|m|r] [h:ascender|top|middle|baseline|bottom|descender|a|t|m|s|b|d]

Sets the anchor state variable to v translated to a single letter and concatinated with h, also translated. It affects only text.

``` ImageScript
# "Change cursor position"
cursor 100 100
# "Draw text"
text Hello
# "Change anchor"
anchor left middle
# "Now the text will be printed with cursor on the horizontal center"
text World
```

#### align [a:left|center|right]

Sets the aligment state variable to a. It affects only how multiline text is printed.

``` ImageScript
# "Change aligment ro center"
align center
# "Print some cool text"
text "Now,\nI'll only use\nImageScript\nto create my images!"
```

#### font [f:STRING]

Sets the font state variable to f. Please be vary that f must be a path or a filename, not a font name!

``` ImageScript
# "Set font and print something"
font arial.ttf
text "Arial is OK, but I prefer Comic Sans!"
```

#### mode [m:fill|outline]

Sets the mode state variable to m.

``` ImageScript
# "Draw a red filled rectangle"
color red
mode fill
rectangle 100 80
# "Draw its blue outline"
color blue
mode outline
rectangle 100 80
```

#### cursor [x:INT] [y:INT]

Sets the cursor positin to (x, y). The cursor is where the drawing begins.

``` ImageScript
# "Set cursor to (10, 10)
cursor 10 10
# "Draw a gray rectangle"
color gray
rectangle 50 50
# "Set cursor to (20, 20)
cursor 20 20
# "Draw rectangle again, white this time"
color white
rectangle 50 50
```

#### move [x:INT] [y:INT]

Moves the cursor by (x, y). 

``` ImageScript
# "This is the same example that with the cursor, but we'll use move"
# "Because cursor is (0, 0) by default, we move gets the same args that cursor"
move 10 10
color gray
rectangle 50 50
# "10 + 10 = 20, so:"
move 10 10
color white
rectangle 50 50
```

### Drawing commands

#### line [x:INT] [y:INT]

Draws a line from the cursor to (x, y) with thickness equal to width.

``` ImageScript
# "Draw a blue line from (10, 10) to (50, 50) with thickness 10"
cursor 10 10
color blue
width 10
line 50 50
```

#### rectangle [w:INT] [h:INT]

Draws a rectangle with its left-top corner at cursor and the width and height equal to w and h.

``` ImageScript
# "Draw a red outline of a rectangle at point (15, 15), width = 100 and height = 60"
mode outline
cursor 15 15
color red
rectangle 100 60
```

#### ellipse [w:INT] [h:INT]

Draws an ellipse inside a box which top left corner is the cursor and width and height are w and h. The box is not drawn.

``` ImageScript
# "Draw three circles with opacity with different colors."
color #ff00007f
ellipse 100 100

cursor 50 0
color #00ff007f
ellipse 100 100

cursor 25 50
color #0000ff7f
ellipse 100 100
```

#### arc [w:INT] [h:INT] [start:INT] [end:INT]

Draws an arc inside a box which top left corner is the cursor and width and height are w and h (the box is not drawn) and with an angle (counting from 3 o'clock) from start to end (in degrees).

``` ImageScript
# "Draw a PacMan"
color yellow
arc 100 100 30 -30

color black
cursor 60 25
ellipse 5 5
```

#### text [t:STRING]

Prints text s begining from the cursor. The text's format depends on anchor, slign, width and font state variables.

``` ImageScript
# "Draw Hello World"
width 12
color white
text "Hello World"
move 0 20
align center
text "Hello\nMy\nDear World"
```

#### image [p:STRING]

Draws an image (found under p path) at cursor position.

``` ImageScript
# "Draw an image found at path './image.png' relative to interpreter CWD"
image image.png
```

### Stack commands

#### push [v:ANY]

Pushes value v on top of the stack.

``` ImageScript
# "Draw a shadowed text"
push "Hello World!"

width 20

color gray
move 5 5
text $

color white
move -5 -5
text $

pop
```

#### pop

Pops from the stack (removes top-most element).

#### dup

Duplicates top-most element. It expects stack to contain at leas one element.

``` ImageScript
# "Draw two squares with width 10 and 100 of space between them (both width and height)."
push 10
dup
addv 110
swap

color red

cursor $ $
rectangle 10 10

pop

cursor $ $
rectangle 10 10

pop
```

#### swap

Swaps (flips) two top-most elements on the stack. For example: {1 2 3} after swap becomes {1 3 2}.

#### rot

Rotates three top-most elements on the stack. For example: {1 2 3} after rot becomes {2 3 1}.

``` ImageScript
# "Draw tree circles with opacity with different colors."

push 255
push 0
dup

color rgba $1 $2 $3 127
ellipse 100 100

rot

cursor 50 0
color rgba $1 $2 $3 127
ellipse 100 100

rot

cursor 25 50
color rgba $1 $2 $3 127
ellipse 100 100

pop pop pop
```

### Setting and getting variables

#### set [n:STRING] [v:ANY]

Associates name n with value v.

#### get [n:STRING]

Pushes value associated with name n to the stack.

### Math commands

Before we start... There are always two kinds of commands, fully stack based (all arguments are taken and POPED from the stack, then the result is pushed) and the ...v variants that accepts one argument that always is of type INT. The ...v variants pops and pushes exacly one element from/to the stack. In this section, both stack-based and ...v variant will be described together.

#### add, addv [v:INT]

Adds two integers and pushes result to the stack. Operands will be consumed.

#### sub subv [v:INT]

Substracts $2 from $1 or v from $ and pushes result to the stack. Operands will be consumed.

#### mul, mulv [v:INT]

Multiplies two integers and pushes result to the stack. Operands will be consumed.

#### div, divv [v:INT]

Divides $ by $2 or v and pushes result to the stack. Operands will be consumed.

#### mod, modv [v:INT]

Takes the modulo of $ and $2 or v and pushes result to the stack. Operands will be consumed.

### String commands

#### cat, catv [v:STRING]

Concatinates two strings.

### Logic commands

There is the same situation as with math commands... Also the results of the folowing commands are always 0 or 1 (false or true) and are pushed to teh stack. Operants are always of type INT.

#### eq, eqv [v:ANY]

Pushes 1 if operants are equal, 0 otherwise.

#### gt, gtv [v:INT]

Pushes 1 if the first operant is greater than the last, 0 otherwise.

#### lt, ltv [v:INT]

Pushes 1 if the first operant is less than the last, 0 otherwise.

### Control-flow commands

#### Scope { ... }

Stand-alone curly-brackets have no inpact on the code execution, however every closing must have an opening.

#### Label @N

A label is an abstract token (that means it is deleted by tokenizer) that marks a place is the script. You can make a label anywhere you want.

#### if [a:INT] [b:INT]

If a is equal to b, it does nothing, else it skips next token or entire scope and if it encouners else it lets its scope to execute.

``` ImageScript
# "Draw a square which is green if 40 > 10 and red otherwise"
push 40
gtv 10
if $ 1 {
	color green
} else {
	color red
}
rectangle 10 10
```

#### else

Normally a token or a scope after else is skipped, however if may execute else's scope.

``` ImageScript
# "This will not draw anything"
else {
	color red
	rectangle 10 10
}
```

#### goto [l:STRING]

Jumps to the place marked by label l.

``` ImageScript
# "Gray-scale"

push 0

@L1

color rgb $ $ $
rectangle 10 10
move 10 0

dup

ltv 255
if $ 1 {
	pop
	addv 10
	goto L1
}
```

#### jump [i:INT]

Jumps to the token i. You should not use that unless you are using label command.

``` ImageScript
# "Gray-scale"

push 0
dup

@L1

pop

color rgb $ $ $
rectangle 10 10
move 10 0

dup

ltv 255
if $ 1 {
	pop
	addv 10
	label L1
	jump $
}
```

#### label [l:STRING]

Pushes the index of token marked by label l.

### Animation commands

#### animation [n:INT] [d:INT]

Starts an animation context, can be used only onse. n tells how many frames does our animation have and d how long (in miliseconds) it will last. Everything below this command will be used to generate folowing scenes and will have animation context. Everything up is a common background.

#### iota

Pushes current frame number to the stack, this is posible only in animation context.

#### n

Pushes the n value given to the animation command, this is possible only in animation context.

#### An example of an animation:

``` ImageScript
# "Rally common animation frquently used as an example of 'how to create an animation in pillow'"

animation 100 50

reset

# "Swap colors when we reach half of the frames"
n
divv 2
dup
iota
gt
if $ 1 {
	color red
	rectangle 100 100
	color orange
} else {
	color orange
	rectangle 100 100
	color red
}
pop

# "We need to corect iota"
dup
iota
gt
if $ 1 {
	pop
	n
	divv 2
	iota
	sub
} else {
	pop
	iota
}

# "Calculate width of our square"
push 150
swap
addv 1
mul
div

# "Calculate where to put the cursor so the square is in the center"
dup
push 100
else swap
sub
divv 2

cursor $ $
pop

ellipse $ $
pop
```
