#!/usr/bin/env python3
import random, hashlib, io
from PIL import Image, ImageDraw

ZODIAC_EN = ["Rat","Ox","Tiger","Rabbit","Dragon","Snake","Horse","Goat","Monkey","Rooster","Dog","Pig"]
ZODIAC_CN = ["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"]
ELEMENTS = ["Wood","Fire","Earth","Metal","Water"]

COLORS = {"bg_dark":(139,0,0),"bg_light":(255,240,245),"gold":(218,165,32),"red":(178,34,34),"white":(255,255,255),"text_dark":(30,30,30),"card_bg":(255,250,250),"divider":(205,92,92)}

def get_zodiac(y): return ZODIAC_EN[(y-1900)%12], ZODIAC_CN[(y-1900)%12]
def get_element(y): return ELEMENTS[(y-1900)%10//2] if (y-1900)%10<5 else ELEMENTS[(y-1900-5)%10//2+2]
def get_western(m,d):
    s=[("Capricorn",(12,22),(1,19)),("Aquarius",(1,20),(2,18)),("Pisces",(2,19),(3,20)),("Aries",(3,21),(4,19)),("Taurus",(4,20),(5,20)),("Gemini",(5,21),(6,20)),("Cancer",(6,21),(7,22)),("Leo",(7,23),(8,22)),("Virgo",(8,23),(9,22)),("Libra",(9,23),(10,22)),("Scorpio",(10,23),(11,21)),("Sagittarius",(11,22),(12,21))]
    for sgn,(sm,sd),(em,ed) in s:
        if(m==sm and d>=sd)or(m==em and d<=ed)or(sm<m<em): return sgn
    return "Unknown"

def get_time(h): return ["子时","丑时","寅时","卯时","辰时","巳时","午时","未时","申时","酉时","戌时","亥时"][(h+1)//2%12]
def seed(y,m,d,h): return int(hashlib.md5(f"{y}{m}{d}{h}".encode()).hexdigest()[:8],16)
def pred(s,o): random.seed(s); return random.choice(o)
def luck(s): random.seed(s); return sorted(random.sample(range(1,100),5))

def gen(y,m,d,h):
    s=seed(y,m,d,h); z=get_zodiac(y); e=get_element(y); w=get_western(m,d); t=get_time(h); ln=luck(s)
    W,H=800,1200; img=Image.new("RGB",(W,H),COLORS["bg_light"]); dr=ImageDraw.Draw(img)
    dr.rectangle([0,0,W,150],fill=COLORS["bg_dark"]); dr.line([(0,145),(W,145)],fill=COLORS["gold"],width=3)
    dr.text((W//2,40),"CHINESE FORTUNE READING",fill=COLORS["gold"]); dr.text((W//2,80),"Your Life Path & 2026 Forecast",fill=COLORS["white"])
    dr.rectangle([30,180,W-30,300],fill=COLORS["card_bg"]); dr.text((50,195),"Birth Information",fill=COLORS["red"]); dr.text((50,230),f"Year: {y} | {z[0]} ({z[1]})",fill=COLORS["text_dark"]); dr.text((50,255),f"Date: {y}-{m:02d}-{d:02d} | Time: {h:02d}:00 ({t})",fill=COLORS["text_dark"]); dr.text((50,280),f"Western: {w} | Element: {e}",fill=COLORS["text_dark"])
    dr.text((30,330),"YOUR LIFE PATH",fill=COLORS["bg_dark"]); dr.line([(30,360),(W-30,360)],fill=COLORS["gold"],width=2)
    aspects=[("Personality",pred(s,["Creative","Wise","Courageous","Compassionate","Leader","Diplomatic","Analytical","Spiritual"])),("Career",pred(s+1,["Creative","Leadership","Technical","Helping","Business","Academic"])),("Wealth",pred(s+2,["Steady","Investment","Profit","Advancement","Opportunity","Wisdom"])),("Love",pred(s+3,["Adventure","Stable","Self-love","New","Deep","Travel"]))]
    cw=(W-80)//2; ch=100
    for i,(l,v) in enumerate(aspects):
        r,c=i//2,i%2; x=30+c*(cw+20); y=380+r*(ch+15)
        dr.rectangle([x,y,x+cw,y+ch],fill=COLORS["white"]); dr.text((x+15,y+15),l,fill=COLORS["red"]); dr.text((x+15,y+50),v,fill=COLORS["text_dark"])
    fy=380+2*(ch+15)+30; dr.text((30,fy),"2026 YEAR FORECAST",fill=COLORS["bg_dark"]); dr.line([(30,fy+30),(W-30,fy+30)],fill=COLORS["gold"],width=2); random.seed(2026); theme=pred(s+5,["Transformation","Growth","Opportunities","Relationships","Advancement","Reflection"])
    dr.rectangle([30,fy+50,W-30,fy+150],fill=COLORS["white"]); dr.text((50,fy+65),f"Theme: {theme}",fill=COLORS["bg_dark"]); dr.text((50,fy+90),"Key: New opportunities, Personal growth",fill=COLORS["text_dark"]); dr.text((50,fy+110),"Stronger relationships, Trust instincts",fill=COLORS["text_dark"])
    dr.rectangle([30,fy+170,W-30,fy+220],fill=COLORS["bg_dark"]); dr.text((W//2,fy+185),f"Lucky Numbers: {' - '.join(map(str,ln))}",fill=COLORS["gold"])dr.text((W//2,H-40),"For Entertainment Only",fill=COLORS["text_dark"]); return img

def handler(req):
    if req.method=='POST':
        try:
            import json
            d=json.loads(req.body); y=int(d.get('year',1990)); m=int(d.get('month',1)); d=int(d.get('day',1)); h=int(d.get('hour',12))
            img=gen(y,m,d,h); b=io.BytesIO(); img.save(b,'PNG'); b.seek(0)
            from flask import Response
            return Response(b.getvalue(), mimetype='image/png')
        except Exception as e: return {'statusCode':500,'body':str(e)}
    return {'statusCode':200,'body':'Chinese Fortune Reader API - POST to this endpoint with year,month,day,hour'}
