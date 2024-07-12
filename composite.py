#!/usr/bin/python
# coding=utf8


import cairo
import aosd
import osdpython
import os
import time

def render(context, data):
    osdpython.set_cairo_ctx(context)

    # scale for TV resolution
    context.scale( 0.70323488, 1.0)
    osdpython.osd_on_draw()


# entry point
def main():
    os.chdir(os.getenv("HOME")+'/livetv/osd')

    alpha = 0.5

    osdpython.main()

    osd = aosd.Aosd()
    osd.set_transparency(aosd.TRANSPARENCY_COMPOSITE)
    osd.set_hide_upon_mouse_event(False)
    osd.set_geometry(0, 0, 1024, 576)
    osd.set_renderer(render, osdpython.twi_line)

    osd.show()

    osd.loop_once()

    dalpha = 0.05


# Main cycle
    while True:
        osd.render()
        time.sleep (1.0 / 20.0)
        osd.loop_once()

if __name__ == "__main__":
    main()

