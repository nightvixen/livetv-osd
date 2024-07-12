#!/usr/bin/env python

import sys
import signal
from time import sleep
import threading
from time import localtime, strftime
import telnet
from selenium import webdriver


import twitter_timeline
from running_line import running_line as osd_running_line
import cairo

def scheduleShow():
    global driver, showosd, osdopacity

    driver.get('http://localhost/schedule/schedule.html');
    for x in range(1, 11):
        osdopacity = (1.0 - (float(x) / 10.0))
        driver.set_window_position(800-80*x,0)

    sleep(8) # Let the user actually see something!
    driver.get('http://localhost/schedule/schedule.html#ru');
    sleep(8) # Let the user actually see something!

    for x in range(1, 11):
        osdopacity = (float(x) / 10.0)
        driver.set_window_position(80*x,0)



def main():
    global twitter_str, time_str, shutdown_flag,ctelnet,livelogo,roffsetx,roffsety,options,driver
    global showosd,osdopacity

    showosd= True
    osdopacity=1.0
    roffsetx=300
    roffsety=-10
    twitter_str = '';
    time_str = '36:69';
    shutdown_flag=False;
    livelogo=False
    ctelnet = telnet.telnet()

    options = webdriver.ChromeOptions()
    options.add_argument("--window-position=800,0")
    options.add_argument("--window-size=720,576")
    options.add_argument("--app=http://localhost/schedule/schedule.html")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',  chrome_options=options)  # Optional argument, if not specified will search path.
    driver.set_window_size(720,637)


    def twitter_thread():
        global shutdown_flag, twi_line,ctelnet
        while not shutdown_flag:
            twi_line.set_next_text(twitter_timeline.go())
            for i in range(60):
                sleep(1)
                if(ctelnet.schedule == True):
                    ctelnet.schedule=False
                    ctelnet.scheduletimer = 0
                    scheduleShow()
                if shutdown_flag:
                    return

    def socket_thread():
        global ctelnet
        while not shutdown_flag:
                ctelnet.do_work()
                if shutdown_flag:
                    return



    text = ["** HaVe FuN! **"]
    global logo, logo_index, logo_max_index, twi_line, info_line

    #  440
    twi_line = osd_running_line("", 454, spacer=True)
    twi_line.speed(7)
    twi_line.size(36)
    twi_line.color(0.7, 0.7, 1)

    # 480
    info_line = osd_running_line(text, 498)
    info_line.speed(6)
    info_line.size(36)

    logo = []
    logo_max_index = 500
    logo_index = 0
    for i in range(logo_max_index):
        logo.append(cairo.ImageSurface.create_from_png ("./logo_2016/resized/2_1_%05d.png" % i))

    threading.Thread(target=twitter_thread).start()
    threading.Thread(target=socket_thread).start()

    signal.signal(signal.SIGINT, sighandler)

    #13 is ok
    return 13

def set_cairo_ctx(cctx):
    global ctx
    ctx = cctx
    return 13

def osd_on_draw():
    global text_pos, logo, logo_max_index, logo_index, twi_line,roffsetx,roffsety
    global watchdog_timer, ctx, ctelnet, showosd, osdopacity

    livelogo= ctelnet.livelogo

    if(livelogo == False):
        ctelnet.scheduletimer += 1
        if(ctelnet.scheduletimer > 22500):
            ctelnet.schedule=True



    # Show logo frame ----- 
    ctx.set_source_surface(logo[logo_index], 610+roffsetx, 40+roffsety)
    ctx.paint()

    logo_index =  logo_index  + 1 if logo_index < logo_max_index - 1 else 0;


    if (showosd == False):
        return 13

    # ---- Show time
    global str_time
    time_str = strftime("%H:%M", localtime())
    ctx.set_font_size(40)
    ctx.move_to(40, 80)
    ctx.set_source_rgba(1,1,1, osdopacity)
    ctx.text_path(time_str)
    ctx.fill_preserve()
    ctx.set_source_rgba(0,0,0, osdopacity)
    ctx.set_line_width(1)
    ctx.stroke()

    # show twi line
    twi_line.draw(ctx, osdopacity)
    info_line.draw(ctx, osdopacity)

    # Draw "LIVE !" text and logo
    if (livelogo == True):
        ctx.set_font_size(40)
        ctx.move_to(590+roffsetx, 140+roffsety)
        ctx.set_source_rgb(1,1,1)
        ctx.text_path("LIVE")
        ctx.fill_preserve()
        ctx.set_source_rgb(0,0,0)
        ctx.stroke()

        ctx.set_font_size(70)
        ctx.move_to(675+roffsetx, 150+roffsety)
        ctx.set_source_rgb(1,0,0)
        ctx.text_path(u"\u2022")
        ctx.fill_preserve()
        ctx.set_source_rgb(0,0,0)

        ctx.set_line_width(1)
        ctx.stroke()


    return 13

def kill_api():
    sighandler(0,0)

def sighandler(signal, frame):
    print 'signal handler called'
    global shutdown_flag, ctelnet
    shutdown_flag = True
    sys.exit() # make sure you add this so the main thread exits as well.


#if __name__ == '__main__':
#  main(sys.argv)
