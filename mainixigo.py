from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from telegram import KeyboardButton
import telegram.ext, telegram
from telegram import Bot
import requests, pickle
from bs4 import BeautifulSoup

TOKEN = "5551289948:AAHy1Cac3Opoej7U7_S4_eg9HyHuaKO7TIw"

def start(update, context):
    update.message.reply_text("Hi! I am a bot that will help you to find the cheapest train tickets.\n"
                              "You can type /help to see the list of commands. \n"
                              "You can also type /explain to see the examples of commands.\n")

def help(update, context):
    update.message.reply_text("/find - src dest date (EXAMPLE: /find YPR MAS 09072022)\n"
                              "you can get updated list of your railway station code from here: https://www.cleartrip.com/trains/stations/list \n")
    update.message.reply_text("/explain - to see the examples of commands")

def explain(update, context):
    update.message.reply_text("/find src dest date - to find the cheapest train tickets from src to dest on date\n"
                              "src - starting station code\n"
                              "dest - destination station code\n"
                              "date - date in ddmmyyyy format\n"
                              "EXAMPLE: /find YPR MAS 09072022 \n"
                              "Suppose if you want to go from Yeshwanthpur to Bhadravathi on 10th July, 2022.\n"
                              "You can type: /find YPR BDVT 10072022")

def find(update, context):
    try:
        findargs = context.args
        if len(findargs) == 3:
            src = findargs[0]
            open('src.txt', 'w').write(src)
            dest = findargs[1]
            open('dest.txt', 'w').write(dest)
            depdate = findargs[2]
            open('depdate.txt', 'w').write(depdate) 
            update.message.reply_text("Please wait...")
            options = webdriver.FirefoxOptions()
            options.log.level = "trace"
            options.add_argument("-remote-debugging-port=9224")
            options.add_argument("-headless")
	    options.add_argument("-disable-gpu")
            options.add_argument("-no-sandbox")
            binary = FirefoxBinary(os.environ.get('FIREFOX_BIN'))
            driver = webdriver.Firefox(firefox_binary=binary, executable_path=os.environ.get('GECKODRIVER_PATH'), options=options)     
            url = f"https://www.ixigo.com/search/result/train/{src}/{dest}/{depdate}//1/0/0/0/ALL"
            driver.maximize_window()
            driver.get(url)
            # time.sleep(5)
            # cookies = pickle.load(open("cookies.pkl", "rb"))
            # for cookie in cookies:
            #     driver.add_cookie(cookie)
            time.sleep(2)
            name_number = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "train-data-wrapper")))
            trainumberlist = []
            count = 0
            for i in name_number:
                trainnumber = WebDriverWait(i, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "train-number"))).text
                trainumberlist.append(trainnumber)
                trainname = WebDriverWait(i, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "train-name"))).text
                #runson = WebDriverWait(i, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "runs-on"))).text
                traintype = WebDriverWait(i, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "train-type"))).text
                # srcdesttime = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "time")))
                # datedate = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "date")))
                leftwing = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "left-wing")))
                timetime1 = WebDriverWait(leftwing[count], 10).until(EC.presence_of_element_located((By.CLASS_NAME, "time")))
                datedate1 = WebDriverWait(leftwing[count], 10).until(EC.presence_of_element_located((By.CLASS_NAME, "date")))
                rightwing = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "right-wing")))
                timetime2 = WebDriverWait(rightwing[count], 10).until(EC.presence_of_element_located((By.CLASS_NAME, "time")))
                datedate2 = WebDriverWait(rightwing[count], 10).until(EC.presence_of_element_located((By.CLASS_NAME, "date")))
                showavail = WebDriverWait(i, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "u-ripple")))
                driver.execute_script("arguments[0].click();", showavail)
                # trainfareavail = WebDriverWait(i, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "train-fare-avail")))
                # trainclass = WebDriverWait(trainfareavail, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "train-fares")))
                fareclass = WebDriverWait(i, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fare-class")))
                fareclasslist = {}
                for j in fareclass:
                    driver.execute_script("arguments[0].click();", j)
                    # fareprice = WebDriverWait(i, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "train-fareAvail"))).text
                    fareprice = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"/html/body/div[1]/div/div[3]/div[1]/div[2]/ul/li[{count+1}]/div/div[1]/div/div[1]/div[2]/div/span[2]"))).text
                    fareclasslist[j.text] = f"₹{fareprice}"
                    time.sleep(0.5)
                
                update.message.reply_text(f"""From: {src}\nTo: {dest}\nDate: {depdate}\nTrain Number: {trainnumber}\nTrain Name: {trainname}\nTrain Type:{traintype}\n Start: {timetime1.text}--{datedate1.text}\n End: {timetime2.text}--{datedate2.text}\n""")
                update.message.reply_text(f"""Fare Class: {fareclasslist}""")
                #bot: Bot = context.bot
               # bot.send_message(chat_id=update.message.chat_id, text=f"""Seat Availability: {seatavailible}""", parse_mode=telegram.ParseMode.HTML)
                count += 1

            buttons = []
            for i in trainumberlist:
                buttons.append([KeyboardButton(f"Train Number: {i}")])  
            context.bot.send_message(chat_id=update.effective_chat.id, text="Please click on the train number to check availibility of seats", reply_markup=telegram.ReplyKeyboardMarkup(buttons))

        else:
            update.message.reply_text("I guess you have misunderstood! /find src dest date")
            update.message.reply_text("use /explain for examples...")
    except Exception as e:
        print(e)
        update.message.reply_text("use /explain for examples...")

def trainumber(update, context):
    if "Train Number:" in update.message.text:
        trainumber = update.message.text.split(":")[1].strip()
      #  update.message.reply_text("Please wait...")
        src = open('src.txt', 'r').read()
        dest = open('dest.txt', 'r').read()
        depdate = open('depdate.txt', 'r').read()
        depdate = depdate[4:] + '-' + depdate[2:4] + '-' +depdate[0:2]
        url = f"https://www.ixigo.com/trains/{trainumber}?orgn={src}&dstn={dest}&departDate={depdate}&quota=GN#availability"
        # update.message.reply_text(url)
        bot: Bot = context.bot
        bot.send_message(chat_id=update.message.chat_id, text=f"Please click here: <a href='{url}'>Link</a>", parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)
    else:
        update.message.reply_text("Use /find src dest date to find the train number")

updater = telegram.ext.Updater(TOKEN, use_context=True)
disp = updater.dispatcher
disp.add_handler(telegram.ext.CommandHandler('start', start))
disp.add_handler(telegram.ext.CommandHandler('help', help))
disp.add_handler(telegram.ext.CommandHandler("find", find))
disp.add_handler(telegram.ext.CommandHandler("explain", explain))
disp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, trainumber))

updater.start_polling()
updater.idle()
