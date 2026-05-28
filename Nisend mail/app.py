from flask import Flask, render_template, request, jsonify , redirect, url_for, session, make_response
from peewee import *
import os
from datetime import timedelta, datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.debug = True
file_dir = os.path.dirname(__file__)
goal_route = os.path.join(file_dir, "app.db")
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + goal_route
db = SqliteDatabase("app.db")
app.secret_key = "sdhsdf1h2f5hthfghgf"
app.config['SESSION_COOKIE_NAME'] = 'session_app2'
is_session = False
curentUser = None
curentUserDB = None

class BaseModel(Model):
    class Meta:
        database = db
class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    mail = CharField(unique=True)
    time = DateTimeField(default=datetime.now)
class Mail(BaseModel):
    sender = ForeignKeyField(User, backref='sent_mails', on_delete='CASCADE')
    receiver = ForeignKeyField(User, backref='received_mails', on_delete='CASCADE')
    subject = CharField(max_length=25, default='(No subject)')
    body = TextField()
    sent_at = DateTimeField(default=datetime.now)
    is_read = BooleanField(default=False)

db.create_tables([User , Mail])
# ///////////////////////////////////////////////////////////////////////////////

@app.route("/")
def home():
    global curentUserDB
    m = False
    user_email = ""
    
    if "username" in session:
        username = session["username"]
        user = User.select().where(User.username == username).first()
        
        if user:
            m = True
            user_email = user.mail
            curentUserDB = user
        else:
            session.clear()
            
    return render_template("index.html", m=m, user=user_email)

# ///////////////////////////////////////////////////////////////////////////

@app.route("/Nisend-mail")
def mainApp():
    global curentUserDB
    m = False
    user_email = ""
    
    if "username" in session:
        username = session["username"]
        user = User.select().where(User.username == username).first()
        
        if user:
            m = True
            user_email = user.mail
            curentUserDB = user
        else:
            session.clear()        
        return render_template("app.html", m=m, user=user_email)
    else:
        return redirect(url_for("login"))
    
# /////////////////////////////////////////////////////////////////////////////

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    return jsonify({"success": True})
    

# /////////////////////////////////////////////////////////////////////////////

@app.route("/mail/Register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        mail = request.form.get("mail")

        try:
            with db.transaction():
                existing_user = User.get_or_none(User.username == username)
                if existing_user:
                    return jsonify({"success": False, "message": f"Username '{username}' already exists."}), 409

                user = User.create(username=username, password=password, mail=mail)
            
            return jsonify({"success": True, "message": "Registration successful! Please log in to your account."}), 201 # 201 Created مناسب است

        except IntegrityError:
            return jsonify({"success": False, "message": "A database integrity error occurred."}), 409
        except Exception as e:
            print(f"An unexpected error occurred during registration: {e}") # لاگ کردن خطا برای دیباگ
            return jsonify({"success": False, "message": "An internal server error occurred."}), 500
    else:
        return render_template("register.html")
    
# ////////////////////////////////////////////////////////////////////////////////

@app.route("/mail/login", methods=['GET', 'POST'])
def login():
    global curentUser, is_session, curentUserDB
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        curentUser = username

        user = User.select().where((User.username == username) & (User.password == password)).first()
        
        if user:
            curentUserDB = user
            session.clear()     
            session["username"] = username
            session.permanent = True
            app.permanent_session_lifetime = timedelta(days=10)
            is_session = True
            return jsonify({"success": True, "message": "Login successful"})
        else:
            return jsonify({"success": False, "message": "Incorrect username or password"}), 401 
    else:
        return render_template("login.html")
    
# /////////////////////////////////////////////////////////////////////////////////

@app.route("/sendMail", methods=['GET', 'POST'])
def sendMail():
    if request.method == 'POST':
        receiver_input = request.form.get("receiver")
        subject = request.form.get("subject")
        text = request.form.get("text")
        
        username = session["username"]
        
        try:
            # 1. پیدا کردن فرستنده
            userSender = User.select().where(User.username == username).first()
            if not userSender:
                return jsonify({"success": False, "message": "Sender not found."}), 404

            # 2. پیدا کردن گیرنده
            userReceiver = User.select().where(User.mail == receiver_input).first()
            if not userReceiver:
                return jsonify({"success": False, "message": "Receiver user not found."}), 404

            # 3. ارسال ایمیل
            with db.transaction():
                Mail.create(
                    sender=userSender, 
                    receiver=userReceiver,
                    subject=subject, 
                    body=text
                )
                
                # 4. مهم: بعد از ارسال، لیست ایمیل‌های جدید رو هم آماده کن تا به فرانت بفرستی
                # این کد دقیقاً همون کاری رو می‌کنه که توی inbox انجام دادیم
                emails_query = Mail.select().where(Mail.receiver == userReceiver).order_by(Mail.sent_at.desc())
                emails_list = list(emails_query.dicts())
                
                inbox_data = []
                for email in emails_list:
                    sender_id = email.get("sender")
                    sender_user = User.select().where(User.id == sender_id).first()
                    sender_name = sender_user.username if sender_user else "Unknown"
                    
                    inbox_data.append({
                        "id": email["id"],
                        "subject": email["subject"],
                        "body_preview": email["body"][:50] + "..." if email["body"] and len(email["body"]) > 50 else (email["body"] or ""),
                        "sender_username": sender_name,
                        "sent_at": email["sent_at"].strftime("%Y-%m-%d %H:%M") if email["sent_at"] else "",
                        "is_read": email["is_read"]
                    })
                user = User.select().where(User.username == username).first()    
                emails_query = Mail.select().where(Mail.receiver == user).order_by(Mail.sent_at.desc())
                emails = list(emails_query.dicts())   
                print(emails) 
                # 5. برگرداندن هم پیام موفقیت و هم لیست ایمیل‌ها
                return jsonify({
                    "success": True, 
                    "message": "✅ Send process was successful.",
                    "emails": inbox_data  # <-- این خط اضافه شد
                })
                
        except IntegrityError:
            return jsonify({"success": False, "message": "🟥 A database integrity error occurred."}), 409
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return jsonify({"success": False, "message": "An internal server error occurred."}), 500

# /////////////////////////////////////////////////////////////////////////////////////

@app.route("/inbox", methods=['GET', 'POST'])
def inbox():
    if request.method == 'GET':
        username = session["username"]
        
        try:
            user = User.select().where(User.username == username).first()
            if not user:
                return jsonify({"success": False, "message": "User not found."}), 404

            emails_query = Mail.select().where(Mail.receiver == user).order_by(Mail.sent_at.desc())
            
            emails = list(emails_query.dicts())

            inbox_data = []
            
            for email in emails:
                sender_id = email.get("sender")
                sender_user = User.select().where(User.id == sender_id).first()
                sender_name = sender_user.username if sender_user else "Unknown"
                sender_mail = sender_user.mail if sender_user else "Unknown"

                inbox_data.append({
                    "id": email["id"],
                    "subject": email["subject"],
                    "body_preview": email["body"][:50] + "..." if email["body"] and len(email["body"]) > 50 else (email["body"] or ""),
                    "sender_username": sender_name,
                    "sender_mail": sender_mail,
                    "sent_at": email["sent_at"].strftime("%Y-%m-%d %H:%M") if email["sent_at"] else "",
                    "is_read": email["is_read"]
                })

            return jsonify({
                "success": True,
                "emails": inbox_data
            })

        except Exception as e:
            print(f"Error in inbox: {e}")
            return jsonify({
                "success": False, 
                "message": "An error occurred while loading inbox."
            }), 500

    elif request.method == 'POST':
        pass

        
# ///////////////////////////////////////////////////////////////////////////////

@app.route("/sent")
def sent():
    if request.method == 'GET':
        username = session["username"]
        
        try:
            user = User.select().where(User.username == username).first()
            if not user:
                return jsonify({"success": False, "message": "User not found."}), 404

            emails_query = Mail.select().where(Mail.sender == user).order_by(Mail.sent_at.desc())
            
            emails = list(emails_query.dicts())

            inbox_data = []
            
            for email in emails:
                receiver_id = email.get("receiver")
                receiver_user = User.select().where(User.id == receiver_id).first()
                sender_name = "me"
                receiver_mail = receiver_user.mail if receiver_user else "Unknown"

                inbox_data.append({
                    "id": email["id"],
                    "subject": email["subject"],
                    "body_preview": email["body"][:50] + "..." if email["body"] and len(email["body"]) > 50 else (email["body"] or ""),
                    "sender_username": sender_name,
                    "receiver_mail": receiver_mail,
                    "sent_at": email["sent_at"].strftime("%Y-%m-%d %H:%M") if email["sent_at"] else "",
                    "is_read": email["is_read"]
                })

            return jsonify({
                "success": True,
                "emails": inbox_data
            })
        
        except Exception as e:
            print(f"Error in inbox: {e}")
            return jsonify({
                "success": False, 
                "message": "An error occurred while loading inbox."
            }), 500

    elif request.method == 'POST':
        pass
    
# ////////////////////////////////////////////////////////////////////////////

@app.route('/mark-as-read', methods=['POST'])
def mark_as_read():
    data = request.get_json()
    mail_id = data.get('mail_id')

    if not mail_id:
        return jsonify({"success": False, "message": "Mail ID is required"}), 400

    try:
        mail_to_update = Mail.get_by_id(mail_id)
            
        if not mail_to_update.is_read:
            mail_to_update.is_read = True
            mail_to_update.save() # ذخیره تغییرات در پایگاه داده
            return jsonify({"success": True, "message": f"Mail {mail_id} marked as read."})
        else:
                # ایمیل از قبل خوانده شده بود، هنوز هم موفقیت آمیز است
            return jsonify({"success": True, "message": f"Mail {mail_id} was already read."})

    except Mail.DoesNotExist:
        return jsonify({"success": False, "message": f"Mail with ID {mail_id} not found"}), 404
    except Exception as e:
            # مدیریت خطاهای احتمالی دیگر
        return jsonify({"success": False, "message": str(e)}), 500
    
# ///////////////////////////////////////////////////////////////////////////////////

@app.route("/getCode", methods=["POST"])
def getCode():
    mail = request.form.get("mail")
    text = request.form.get("text")
    
    if mail and text:
        try:
            user = User.select().where(User.username == "Nisend").first()
            userReceiver = User.select().where(User.mail == mail).first()
            if not userReceiver:
                return jsonify({"success": False, "message": "Receiver user not found."}), 404
            with db.transaction():
                Mail.create(
                    sender=user, 
                    receiver=userReceiver,
                    subject="Your secret code for Nisend", 
                    body=text
                )
                return jsonify({"success": True, "message": "Code is sent to your inbox"}), 200
        except IntegrityError:
            return jsonify({"success": False, "message": "🟥 A database integrity error occurred."}), 409
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return jsonify({"success": False, "message": "An internal server error occurred."}), 500
            












if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
