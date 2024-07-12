class running_line:
    START_OFFSET = 1020
    font_size = 40
    SCROLL_SPEED = 5
    opacity = 1.0
    osdbgcolorr = 0.3137254901960784 
    osdbgcolorg = 0.35294117647058826
    osdbgcolorb = 0.37254901960784315
    osdspcolorr = 0.5411764705882353
    osdspcolorg = 0.5647058823529412
    osdspcolorb = 0.5764705882352941
    swidth =0
    sheight=0
    spacer = False
    text_list = None

    text_pos = START_OFFSET
    scroll_speed = 5
    r = g = b = 1

    def __init__(self, text, top_offset, spacer=False):
        if isinstance(text, list):
            self.text_list = text
            self.text_listidx = 0
            self.text = self.text_list[self.text_listidx]
        else:
            self.text = self.next_text = text

        self.text_pos = self.START_OFFSET
        self.top_offset = top_offset
        self.spacer = spacer

    def speed(self, sp):
        """ Set scrolling speed
        """
        self.scroll_speed = sp

    def size(self, si):
        """ Set font size
        """
        self.font_size = si


    def set_next_text(self, text):
        self.next_text = text

    def color(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def draw(self, ctx, opacity):
        """ Call in OSD on_draw
        """
        self.opacity =  opacity
        if self.text == '':
            if self.next_text != '':
                self.text = self.next_text
            else:
                return
        if (self.swidth == 0):
            dsurface = ctx.get_target()
            self.swidth  = dsurface.get_width()
            self.sheight = dsurface.get_height()

        ############# DRAW BACKGROUND and delimeter ##
        ctx.set_source_rgba(self.osdbgcolorr, self.osdbgcolorg, self.osdbgcolorb, 0.7 * opacity)
        ctx.rectangle(0, self.top_offset + self.font_size, self.swidth, self.font_size+4)
        ctx.fill()

        if (self.spacer != False):
            ctx.set_source_rgba(self.osdspcolorr, self.osdspcolorg, self.osdspcolorb, 0.7 * opacity)
            ctx.set_line_width(6)
            ctx.move_to(0, self.top_offset + ((self.font_size+3)*2))
            ctx.line_to(self.swidth, self.top_offset + ((self.font_size+3)*2))
            ctx.stroke()

        #################################
        ctx.set_font_size(self.font_size)
        x_bearing, y_bearing, width, height = ctx.text_extents(self.text)[:4]
        ctx.move_to(self.text_pos , height*2 + self.top_offset)
        self.text_pos -= self.scroll_speed

        #ctx.show_text(text)
        ctx.set_source_rgba(self.r, self.g, self.b, self.opacity)
        ctx.text_path(self.text)
        ctx.fill_preserve()
        ctx.set_source_rgba(0,0,0, self.opacity)
        ctx.set_line_width(1)
        ctx.stroke()



        #print ctx.
        #pass
        if -self.text_pos > width:
          self.text_pos = self.START_OFFSET

          if not self.text_list is None:
            # Rolling next message in the list
            self.text_listidx = (self.text_listidx + 1) % len(self.text_list)
            self.next_text = self.text_list[self.text_listidx]

          self.text = self.next_text
