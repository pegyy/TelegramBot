#بسم الله الرحمن الرحیم
# ربات مترجم  

from config import*
import telebot
import mysql.connector
from telebot.types import InlineKeyboardButton , InlineKeyboardMarkup , ReplyKeyboardMarkup , KeyboardButton

db_config={
    'host': 'LOC',
    'user': 'root',
    'password':'****************',
    'database':'DB'
}

bot = telebot.TeleBot("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

# دکمه پنل کاربر برای گرفتن ترجمه متنش 
trans_markup = ReplyKeyboardMarkup(resize_keyboard=True)
trans_markup.add("دریافت ترجمه")

# دکمه پنل کاربر برای وقتی که متنش ترجمه شده و ترجمه رو دریافت کرده و میخواد متن جدیدی برای ترجمه بده
new_text_markup = ReplyKeyboardMarkup(resize_keyboard=True)
new_text_markup.add("متن جدید")

# دکمه پنل مترجم برای وقتی که یک متن رو ترجمه کرده وفرستاده و میخواد متن جدیدی برای ترجمه بگیره 
translate_markup = ReplyKeyboardMarkup(resize_keyboard=True)
translate_markup.add("ترجمه")


start_markup = ReplyKeyboardMarkup(resize_keyboard=True)
start_markup.add("شروع")

# شروع و چک کردن رمز ورود
@bot.message_handler(commands=['start' , 'شروع'])
def send_wellcome(message):
    msg = bot.send_message(message.chat.id,"سلام علیکم!\n به ربات مترجم خوش آمدید؛\n لطفا رمز خود را وارد کنید")
    bot.register_next_step_handler(msg , check_password)
print("START")

#########################################    چک کردن پسورد    ######################################
def check_password(message):
    print("start checking password ...................... user OR admin ???")
    if message.text == "12345":
        admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
        admin_panel.add("ترجمه" , "جزئیات")
        bot.send_message(message.chat.id , "به پنل مترجم وارد شدید" , reply_markup=admin_panel)
        print("you are admin ")

    elif message.text =="123":
        print("you are user ")
        userid = message.from_user.id
        check_user(userid)
     
    else:
        print("wrong password ... try again !")
        msg = bot.send_message(message.chat.id , "پسورد اشتباه بود ... دوباره تلاش کنید")
        bot.register_next_step_handler(msg , check_password)

######################################## چک کردن کاربر : جدید یا قدیمی  ################################
def check_user(userid):
    print(" checking user ---------------------------- old OR new ????")
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor(buffered=True) as cursor:
            sql = f"SELECT * FROM text WHERE uid={userid}"
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result)
            if result is None:
                print("new user ")
                msg = bot.send_message(userid , "متنی که میخوای ترجمه کنی رو بفرست")
                bot.register_next_step_handler(msg , get_user_text)
            else: 
                print("old user ")
                check_state(userid)

######################################      چک کردن وضعیت متن ارسالی کاربر       #####################################
def check_state(userid):
    print("checking state -------------- 0 or not ??")
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor(buffered=True) as cursor:
            sql =f"SELECT * FROM text WHERE uid={userid}"
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result)
            if result[3] == 0 :
                global unique
                unique = result[0]
                print("old user with state = 0")
                bot.send_message(userid , "متن شما در صف ترجمه قرار دارد : هنوز برای مترجم ارسال نشده است" , reply_markup=start_markup)

            elif result[3] == 1:
                print("old user with state = 1")
                bot.send_message(userid , "متن شما در صف ترجمه قرار دارد : برای مترجم ارسال شده است" , reply_markup=start_markup)
            
            elif result[3] ==2:
                old_user(userid)


######################################    گرفتن متن از کاربر و ذخیره در دیتابیس      ######################################
def get_user_text(message):
    print("start get user text !!!")
    uid = message.from_user.id    
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor() as cursor:
            sql = "INSERT INTO text( id , fa_text , u_name , uid) VALUES( %d , '%s' ,'%s', %d)" % ( message.id , message.text , message.from_user.username, uid)
            cursor.execute(sql) 
            connection.commit()
            print("end saving text")
    bot.send_message(uid , "متن شما در صف ترجمه قرار گرفت\n لطفا ۳۰ دقیقه دیگر برای دریافت ترجمه اقدام کنید" , reply_markup=start_markup)

 
#########################################                 کاربر قدیمی                ##########################################
def old_user(userid):
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor(buffered=True) as cursor:
            sql = f"SELECT * FROM text WHERE uid={userid} AND state=2 AND send =0"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                bot.send_message(userid , "ترجمه همه متن هایی که تا کنون فرستادید برای شما ارسال شده است \n برای سفارش ترجمه جدید از دکمه زیر استفاده کنید" ,reply_markup=new_text_markup)
            else:
                bot.send_message(userid , "متن شما ترجمه شده است. \n  متن ارسالی شما : \n" + result[1] + "\n ترجمه : \n " +result[2])
                ID=result[0]
                sql2 = f"UPDATE text SET send = 1 WHERE id{ID}"
                cursor.execute(sql2)
                connection.commit()
                send_archive(ID)





@bot.message_handler(func= lambda m:m.text=="متن جدید")
def new_text(message):
    print("new text btn starting ")
    userid = message.from_user.id
    msg = bot.send_message(userid , "خیلی هم خوب! \n پس متنی که میخوای ترجمه بشه رو بفرست.")
    bot.register_next_step_handler(msg , get_user_text)




@bot.message_handler()
def panel(message):
########################################  دکمه دریافت ترجمه در پنل کاربر   #################################################
    if message.text == "دریافت ترجمه":
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor(buffered=True) as cursor:
                sql = f"SELECT * FROM text WHERE id={unique}"
                cursor.execute(sql) 
                result = cursor.fetchone()
                print(result)
                user_id = result[4]
                fr_text = result[2]
                if result[3] == 2 :
                    bot.send_message(user_id , "متن شما ترجمه شده است/n" , fr_text , reply_markup=new_text_markup) 
                else:
                    bot.send_message(user_id , "متاسفانه متن شما هنوز ترجمه نشده است!")

########################################         دکمه ترجمه در پنل مترجم        ##########################################
    elif message.text == "ترجمه":
        print("ADMIN PANEL")
        translator_id = message.from_user.id
        t_name = message.from_user.username
        print("checking translator state")
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                sql = f"SELECT * FROM text WHERE tid ={translator_id}"
                cursor.execute(sql)
                result = cursor.fetchone()
                print(result)
                if result is None:
                    print("new translator !")
                    new_tarnslator(translator_id , t_name)
                else:
                    print("old translator")
                    old_translator(translator_id , t_name)           

#########################################              شروع              ##############################################
    elif message.text =="شروع":
        send_wellcome(message)

#########################################      دکمه درخواست ترجمه جدید در پنل کاربر : ثبت متن جدید از کاربر برای ترجمه        ##############################################


#########################################  این تابع برای مترجم جدید متن ارسال می کند   ###########################################
def new_tarnslator(translator_id , t_name):
    print("starting new translator function ")
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor(buffered=True) as cursor:
            sql= f"SELECT * FROM text WHERE state ={0}"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                bot.send_message(translator_id , "متن جدیدی برای ترجمه نیست" , reply_markup=translate_markup)
            else:
                print(" result : " , result)
                ID = result[0]
                fa_text = result[1]
                print("fa_text : " , fa_text)
                sql2 = """UPDATE text SET state =%s , t_name=%s , tid =%s WHERE id =%s """
                val2 = (1 , t_name , translator_id , ID)
                cursor.execute(sql2 , val2)
                connection.commit()
                msg = bot.send_message(translator_id , "متنی که باید ترجمه کنی:\n" + fa_text )
                bot.register_next_step_handler(msg , get_translate , ID )

#########################################‌ گرفتن ترجمه متن از مترجم و ذخیره در دیتابیس   ##########################################
def get_translate(message , ID):
    print("STARTING get translate from translator and saving in DB")
    fr_text = message.text
    print(fr_text)
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor(buffered=True) as cursor:
            sql = """ UPDATE text SET fr_text=%s , state=%s WHERE id = %s """
            val = (fr_text , 2 , ID )
            cursor.execute(sql , val)
            connection.commit()
            bot.send_message(message.chat.id , "ترجمه ای که شما فرستادید با موفقیت ثبت شد" , reply_markup=translate_markup)

#########################################                مترجم قدیمی               ##########################################
def old_translator(translator_id , t_name):
    print("start OLD translator function ")
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor(buffered=True) as cursor:
            sql = f"SELECT * FROM text WHERE tid={translator_id} AND state=1"
            cursor.execute(sql)
            result = cursor.fetchone()
            print("rresult is : " , result)
            if result is None:
                new_tarnslator(translator_id , t_name)
            else:
                print(" OLD translator with state = 1 ")
                fa_text = result[1]
                ID = result[0]
                print("ID is : " , ID)
                msg = bot.send_message(translator_id , "شما هنوز متن قبلی رو ترجمه نکردی \n" + fa_text)
                bot.register_next_step_handler(msg , get_translate , ID)

#########################################       فرستادن متن و ترجمه به کانال آرشیو       ##########################################
def send_archive(ID):
    print("sending to archive channel")
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor(buffered=True) as cursor:
            sql = f"SELECT * FROM text WHERE id={ID}"
            cursor.execute(sql)
            result = cursor.fetchone()
            ID = str(result[0])
            channel_link = -1002081178817
            bot.send_message(channel_link ,   "ID : " + ID + "\nمتن :\n" + result[1] + "\n\n ترجمه : \n" +result[2] + "\n\n آیدی کاربر : " + "@"+result[4] + "\n آیدی مترجم : " + "@"+result[6] )

bot.infinity_polling(timeout=120)
