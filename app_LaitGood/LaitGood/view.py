# 執行並渲染網頁的view

import datetime
from werkzeug.urls import url_parse # 使用Werkzeug的url_parse()函式解析網址來源及安全性
from app_LaitGood import app, db, babel # 從__init__.py 引入初始化的app和db
from flask import request, render_template,url_for,redirect, flash
from app_LaitGood.LaitGood.model import UserRegister, send_mail, Post # 從model.py引入資料表
from app_LaitGood.LaitGood.form import  FormRegister, FormLogin, FormChangePWD, FormResetPasswordMail, FormResetPassword # 從form.py引入表格
from flask_login import current_user, login_user, logout_user, login_required # 登入功能
from flask_babel import refresh
import flask_whooshalchemyplus # 站內搜索

# @app.route('/LaitGoodmember') # preHTML測試用的
# def LaitGoodHomepage():
#     return render_template('LaitGoodHomepage.html') 

# 資料庫操作
@app.route('/dbtable', methods=['GET', 'POST'])
def dbtable():   
    db.create_all() # 建置table
    return '建置資料庫註冊表'

# 管理者登入頁面 (測試用)
@app.route('/', methods=['GET', 'POST'])
def manager_login():
    if (request.method == 'POST'):
        username=request.form.get('username')
        if (username == 'CEO'):
            return redirect(url_for('LaitGood'))
        else:
            flash("帳號錯誤，請重新輸入！")  # 閃現訊息   
            return redirect(url_for('manager_login'))

    return render_template('LaitGood/manager_login.html') #  將HTML5的程式碼放在另一個檔案裡，藉由flask提供的函式render_template()去讀取

# 日果首頁
@app.route('/LaitGood', methods=['GET', 'POST']) # 利用利用jinja模板語法直接繼承基礎模板做出的首頁例子
def LaitGood():
    refresh()
    # if (request.method == 'POST'):
    #     username=request.form.get('username')
    #     if (username == 'CEO'):
    #         return render_template('LaitGood/LaitGood.html') 
    #     else:
    #         flash("帳號錯誤，請重新輸入！")  # 閃現訊息   
    #         return redirect(url_for('LaitGood'))
    # return render_template('LaitGood/manager_login.html')        
    return render_template('LaitGood/LaitGood.html') 

# 中文語系設置    
@app.route('/LaitGood_zh', methods=['GET', 'POST'])
def LaitGood_zh():
    y = lambda: 'zh_TW'
    babel.localeselector(y)     
    return redirect(url_for('LaitGood'))
# 英文語系設置    
@app.route('/LaitGood_en', methods=['GET', 'POST'])
def LaitGood_en():
    y = lambda: 'en'
    babel.localeselector(y)     
    return redirect(url_for('LaitGood'))


# 日果會員註冊
@app.route('/LaitGoodmember_register', methods=['GET', 'POST']) 
def LaitGoodmember_register():
    form = FormRegister()
    
    if form.validate_on_submit():
        user = UserRegister( # 實作使用者類別並且賦值
            username = form.username.data,
            email = form.email.data,
            password = form.password.data,
            registered_on = datetime.datetime.now()
            )
        db.session.add(user)
        db.session.commit()

        #  產生用戶認證信的token
        token = UserRegister.create_confirm_token(user)

        #  寄出帳號啟動信件
        send_mail(recipients=[user.email],
                  subject='日果新朋友您好，請驗證註冊帳號',
                  template='LaitGood/mail/welcomemember_mail',
                  mailtype='html',
                  user=user,
                  token=token)
        flash('請確認您的信箱以完成註冊。')              
        return render_template('LaitGood/flashmessage.html')

    return render_template('LaitGood/member_register.html', form=form) 


# 驗證token的路由
@app.route('/user_confirm/<token>')
def user_confirm(token):         
    print('開始驗證')
    user = UserRegister()
    email = user.confirm_token(token)    
    user = UserRegister.query.filter_by(email=email).first_or_404()   

    if user.confirm == True:        
        print('重複驗證')
        flash('此帳號重複驗證，請直接登入帳號。')
        return redirect(url_for('LaitGoodmember_login'))
    else:
        user.confirm = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        print('成功驗證')
        flash('此帳號已成功驗證，感謝您的註冊！') # 不太確定這裡會不會直接登入

    return render_template('LaitGood/flashmessage.html') 


# 日果會員登入
@app.route('/LaitGoodmember_login', methods=['GET', 'POST'])
def LaitGoodmember_login():
    form = FormLogin()
    if form.validate_on_submit():
        user = UserRegister.query.filter_by(email=form.email.data).first() # 檢核帳號是否存在
        if user: # 使用者存在資料庫
            if user.check_password(form.password.data): # 核對密碼
                login_user(user, remember=form.remember_me.data) # flask-login內建的登入函式，第二個參數是記得我的參數 (使用cookie來記錄在使用者端)
                next_page = request.args.get('next') # 登入後導回來源url，利用request來取得參數next
                '''
                # 如果登入URL沒有next引數，則將頁面重定向到/LaitGood頁面。
                # 如果登入URL包含next設定為包含域名的完整URL的引數，則送出警告訊息。
                # 如果登入URL包含next設定為相對路徑的引數（即沒有域部分的URL），則將使用者重定向到該URL。
                # 渲染用的HTML中form的action不能導向登入頁，不然next就會變成get到登入頁
                '''
                if not next_page:   # 確認使用者是否有該url的權限
                    next_page = url_for('LaitGood')
                elif url_parse(next_page).netloc != '':
                    flash('您沒有造訪此網頁之權限！')
                    return render_template('LaitGood/flashmessage.html')
                return redirect(next_page)
            else:
                flash('輸入密碼有誤，請重新確認。')
        else:
            flash('註冊信箱有誤，請重新確認。')
    return render_template('LaitGood/member_login.html', form=form) 


# 會員登出
@app.route('/LaitGoodmember_logout')  
def LaitGoodmember_logout():  
    logout_user() # flask-login內建的登出函式
    flash('已登出，期待再次見到您:)')
    return render_template('LaitGood/flashmessage.html')  

# 攔截所有request的function，用於攔截尚未啟動的帳號
# 使用者狀況：登入、尚未啟動、endpoint不等於static(避免靜態資源的取用異常)及相關例外清單，否則重啟信件等request也會被攔截

@app.before_request
def before_request():
    if (current_user.is_authenticated and
            not current_user.confirm and
            request.endpoint not in ['re_userconfirm','LaitGoodmember_login', 'LaitGoodmember_logout', 'user_confirm', 'change_password','reset_password','reset_password_recive'] and
            request.endpoint != 'static'):       

        return render_template('LaitGood/member_unactivate.html') 

# 重發驗證信
@app.route('/re_usreconfirm')
@login_required # 必需為登入狀態
def re_userconfirm():   
    token = current_user.create_confirm_token()  #  產生用戶認證令牌
    #  寄出帳號啟動信件
    send_mail(recipients=[current_user.email],
            subject='日果新朋友您好，請驗證註冊帳號',
            template='LaitGood/mail/welcomemember_mail',
            mailtype='html',
            user=current_user,
            token=token)
    flash('請確認您的信箱以啟動帳號。')
    return render_template('LaitGood/flashmessage.html')

# 變更密碼
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = FormChangePWD()
    if form.validate_on_submit():
        #  透過current_user來使用密碼認證，確認是否與現在的密碼相同
        if current_user.check_password(form.password_old.data):
            current_user.password = form.password_new.data
            db.session.add(current_user)
            db.session.commit()
            flash('密碼已變更，請重新登入！')
            return redirect(url_for('LaitGoodmember_logout'))
        else:
            flash('密碼輸入錯誤，請重新輸入')
    return render_template('LaitGood/member_changepassword.html', form = form)


# 忘記密碼
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    #  只允許未登入的匿名帳號可以申請遺失密碼
    if not current_user.is_anonymous:
        return redirect(url_for('LaitGood'))
    
    form = FormResetPasswordMail()
    if form.validate_on_submit():            
            user = UserRegister.query.filter_by(email=form.email.data).first() #  取得使用者資料
            if user:   
                token = user.create_confirm_token() # 產生token
                #  寄出通知信
                send_mail(recipients=[user.email],
                        subject='日果會員您好，請驗證並重設密碼',
                        template='LaitGood/mail/resetpassword_mail', 
                        mailtype='html',
                        user=current_user,
                        token=token)
                flash('請確認您的信箱並點選該網址以重設密碼')
                return  render_template('LaitGood/flashmessage.html')
    return render_template('LaitGood/member_forgetpassword.html', form=form) 

# 重設密碼的驗證token路由
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_recive(token):
    if not current_user.is_anonymous:
        return redirect(url_for('LaitGood'))

    form = FormResetPassword()
    if form.validate_on_submit():
        user = UserRegister()
        data = user.confirm_token(token)
        if data:
            user = UserRegister.query.filter_by(email=data).first()
            #  再驗證一次是否確實的取得使用者資料
            if user:
                user.password = form.password.data
                db.session.commit()
                flash('您的密碼已重置，請重新登入！')
                return redirect(url_for('LaitGoodmember_login'))
            else:
                flash('您的帳號密碼錯誤，請重新確認！')
                return redirect(url_for('LaitGoodmember_login'))
        else:
            flash('帳號驗證錯誤，請重新進行驗證動作。')
            return redirect(url_for('LaitGoodmember_login'))
    
    return render_template('LaitGood/member_resetpassword.html', form=form)

# 日果線上購物頁，待改
@app.route('/LaitGoodmember_shop') # 利用利用jinja模板語法直接繼承基礎模板做出的首頁例子
@login_required
def LaitGoodmember_shop():

    return render_template('LaitGood/member_shop.html') 

# 站內搜尋區，施工中
@app.route('/search', methods = ['POST', 'GET'])
def search():
    if not request.form['search']:
        return redirect(url_for('LaitGood'))
    return redirect(url_for('.search_results', query = request.form['search']))

 
@app.route('/search_results/<query>')
def search_results(query):
    flask_whooshalchemyplus.whoosh_index(app, Post) 
    results = Post.query.whoosh_search(query).all()
    return render_template('LaitGood/search_results.html', query = query, results = results)