import random
from time import time, localtime
from requests import get, post
from datetime import datetime, date
import sys
import os
import bs4
import requests
import json
 
 
def get_color():
    # 往list中填喜欢的颜色即可
    color_list = ['#6495ED','#3CB371']
 
    return random.choice(color_list)
 
 
def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token
 
 
def get_weather():
    city_name = config["province"]+config["city"]
 
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Cookie':'HttpOnly; userNewsPort0=1; Hm_lvt_080dabacb001ad3dc8b9b9049b36d43b=1660634957; f_city=%E9%87%91%E5%8D%8E%7C101210901%7C; defaultCty=101210901; defaultCtyName=%u91D1%u534E; Hm_lpvt_080dabacb001ad3dc8b9b9049b36d43b=1660639816',
        'Host':'www.weather.com.cn',
        'Referer':'http://www.weather.com.cn/weather1d/101320101.shtml',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54'
 
    }
    url = "http://www.weather.com.cn/weather/101320101.shtml"
    response = get(url = url, headers=headers)
 
    text = response.content.decode('utf-8')
    soup = bs4.BeautifulSoup(text,'html.parser')
    #存放日期
    list_day = []
    i = 0
    day_list = soup.find_all('h1')
    for each in day_list:
        if i <= 1: #今明两天的数据
            list_day.append(each.text.strip())
            i += 1
 
    #天气情况
    list_weather = []
    weather_list = soup.find_all('p',class_ = 'wea') #之前报错是因为写了class 改为class_就好了
    for i in weather_list:
        list_weather.append(i.text)
    list_weather = list_weather[0:2] #只取今明两天
 
 
    #存放当前温度，和明天的最高温度和最低温度
    tem_list = soup.find_all('p', class_='tem')
 
    i = 0
    list_tem = []
    for each in tem_list:
        if i == 0:
            list_tem.append(each.i.text)
            i += 1
        elif i > 0 and i < 2:
            list_tem.append([each.span.text, each.i.text])
            i += 1
 
    #风力
    list_wind = []
    wind_list = soup.find_all('p', class_='win')
    for each in wind_list:
        list_wind.append(each.i.text.strip())
    list_wind = list_wind[0:2] #同只取今明两天
 
    today_date = list_day[0]
    today_weather = list_weather[0]
    now = list_tem[0]
    today_wind = list_wind[0]
    tomorrow = list_day[1]
    tomorrow_weather = list_weather[1]
    tomorrow_max = list_tem[1][0]
    tomorrow_min = list_tem[1][1]
    tomorrow_wind = list_wind[1]
 
 
    return city_name,today_date,today_weather,now,today_wind,tomorrow,tomorrow_weather,tomorrow_max,tomorrow_min,tomorrow_wind
 
 
 
def get_birthday(birthday, year, today):
    # 获取生日的月和日
    birthday_month = int(birthday.split("-")[1])
    birthday_day = int(birthday.split("-")[2])
    # 今年生日
    year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day
 
def get_daily_love():
    #每日一句情话
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    all_dict = json.loads(r.text)
    sentence = all_dict['returnObj'][0]
    daily_love = sentence
    return daily_love
 
def get_ciba():
    #每日一句英语（来自爱词霸）
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en
 
 
 
def send_message(to_user, access_token, city_name,today_date,today_weather,now,today_wind,tomorrow,tomorrow_weather,tomorrow_max,tomorrow_min,tomorrow_wind,daily_love,note_ch, note_en):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # 获取在一起的日子的日期格式
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 获取所有生日数据
    birthdays = {}
    for k, v in config.items():
        if k[0:5] == "birth":
            birthdays[k] = v
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": get_color()
            },
            "city": {
                "value": city_name,
                "color": get_color()
            },
            "today": {
                "value": today_date,
                "color": get_color()
            },
            "today_weather": {
                "value": today_weather,
                "color": get_color()
            },
            "now": {
                "value": now,
                "color": get_color()
            },
            "today_wind": {
                "value": today_wind,
                "color": get_color()
            },
            "tomorrow": {
                "value": tomorrow,
                "color": get_color()
            },
            "tomorrow_weather": {
                "value": tomorrow_weather,
                "color": get_color()
            },
            "tomorrow_max": {
                "value": tomorrow_max,
                "color": get_color()
            },
            "tomorrow_min": {
                "value": tomorrow_min,
                "color": get_color()
            },
            "tomorrow_wind": {
                "value": tomorrow_wind,
                "color": get_color()
            },
            "daily_love": {
                "value": daily_love,
                "color": get_color()
            },
            "birthday": {
                "value": birthdays,
                "color": get_color()
            },
            "note_en": {
                "value": note_en,
                "color": get_color()
            },
            "note_ch": {
                "value": note_ch,
                "color": get_color()
            },
            "love_day": {
                "value": love_days,
                "color": get_color()
            }
        }
    }
    for key, value in birthdays.items():
        # 获取距离下次生日的时间
        birth_day = get_birthday(value, year, today)
        # 将生日数据插入data
        data["data"][key] = {"value": birth_day, "color": get_color()}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)
 
 
if __name__ == "__main__":
    try:
        file = sys.path[0]+"/config.txt"
        print("---"+file)
        with open(file, encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)
 
    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入省份和市获取天气信息
    city_name,today_date,today_weather,now,today_wind,tomorrow,tomorrow_weather,tomorrow_max,tomorrow_min,tomorrow_wind = get_weather()
    # 获取每日情话
    daily_love = get_daily_love()
    #获取每日一句英语
    note_ch, note_en = get_ciba()
    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, city_name,today_date,today_weather,now,today_wind,tomorrow,tomorrow_weather,tomorrow_max,tomorrow_min,tomorrow_wind,daily_love,note_ch, note_en)
    os.system("pause")