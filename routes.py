from __main__ import app, roles_required, login_required, db, user_manager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import *
from flask import request, flash, render_template, url_for, redirect
from flask_login import login_user, logout_user, current_user
from datetime import datetime
import threading
import time

engine = create_engine('sqlite:///Airway.sqlite')
connection = engine.connect()
Base = declarative_base()
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
# boş sepetin tanımlanması
user_sepet = []

it = 0


def sil():
    global it
    it = 666
    global timer
    timer.cancel()


@app.route('/')
def index():
    global check
    check = 0
    if current_user.is_active == 1:
        if current_user.has_roles('Admin'):
            return render_template("admin-index.html")
        else:
            return render_template("logged-in-index.html")

    else:
        return render_template("index.html")


ali = Yolcu(None, None)


@app.route('/booking-page', methods=['POST', 'GET'])
def booking_page():
    global check
    check = 0
    connection = engine.connect()
    metadata = db.MetaData()
    query = db.select([Flight]).where(Flight.status == 'aktif')
    result = connection.execute(query)
    data = result.fetchall()
    print(data)
    datal = len(data)
    fromlocation = ['İstanbul']
    tolocation = ['İstanbul']
    fid = request.form.get('passenger')
    sort = request.form.get('sort')
    if not fid == None:
        fix = fid.replace("(", " ")
        fix = fix.replace(")", " ")
        fix = fix.replace("'", " ")
        fix = fix.strip()
        fix = fix.split(",")
        yolcusayısı = int(fix[1])
        fixid = str(fix[0])
        print(yolcusayısı)
        print(fixid)
        ali.kolcu = yolcusayısı
        ali.id = fixid
        print(ali.kolcu)
        if current_user.is_active == 1:
            return redirect(url_for('passenger'))

    for i in range(datal):
        count = 0
        fl = len(fromlocation)
        for j in range(fl):
            if fromlocation[j] == data[i][2]:
                count = count + 1
        if count == 0:
            fromlocation = fromlocation + [data[i][2]]
            print(fromlocation)
    for i in range(datal):
        count = 0
        tl = len(tolocation)
        for j in range(tl):
            if tolocation[j] == data[i][3]:
                count = count + 1
        if count == 0:
            tolocation = tolocation + [data[i][3]]
            print(tolocation)
    tl = len(tolocation)
    fl = len(fromlocation)
    from_location = request.form.get('froml')
    to_location = request.form.get('tol')
    departure_date = request.form.get('departureDate')
    adult = request.form.get('adult')
    child = request.form.get('children')
    if current_user.is_active == 1:
        if from_location and tolocation:
            print(departure_date)
            return flights(from_location, to_location, departure_date, adult, child, sort)
        return render_template("logged-in-booking-page.html", tolocation=tolocation, fromlocation=fromlocation, tl=tl,
                               fl=fl)
    else:
        if from_location and tolocation:
            print('yey')
            return general_flights(from_location, to_location, departure_date, adult, child, sort)
        return render_template('booking-page.html', tolocation=tolocation, fromlocation=fromlocation, tl=tl, fl=fl)


veli = Yolcu(None, None)


@app.route('/flights', methods=['POST', 'GET'])
@login_required
def flights(from_location, to_location, departure_date, adult, child, sort):
    global check
    print(sort)
    check = 0
    connection = engine.connect()
    metadata = db.MetaData()
    fid = request.form.get('fid')
    print(fid)
    if departure_date == '':
        if sort == 'sorted':
            query = db.select([Flight, Flight_Details]).order_by(db.desc(Flight_Details.available_seats)).where(
                db.and_(Flight.from_location == from_location, Flight.to_location == to_location,
                        Flight.flight_id == Flight_Details.flight_id))
            result = connection.execute(query)
            ucuslar = result.fetchall()
        else:
            query = db.select([Flight, Flight_Details]).where(
                db.and_(Flight.from_location == from_location, Flight.to_location == to_location,
                        Flight.flight_id == Flight_Details.flight_id))
            result = connection.execute(query)
            ucuslar = result.fetchall()
    else:
        if sort == 'sorted':
            query = db.select([Flight]).order_by(db.desc(Flight_Details.available_seats)).where(
                db.and_(Flight.from_location == from_location, Flight.to_location == to_location,
                        Flight.depart_date == departure_date))
            result = connection.execute(query)
            ucuslar = result.fetchall()
        else:
            query = db.select([Flight]).where(
                db.and_(Flight.from_location == from_location, Flight.to_location == to_location,
                        Flight.depart_date == departure_date))
            result = connection.execute(query)
            ucuslar = result.fetchall()

    yolcu = child + adult
    print(ucuslar)
    ucret = [""]
    ucuslarl = len(ucuslar)
    for i in range(ucuslarl):
        if i == 0:
            ucret[0] = int(yolcu) * int(ucuslar[i][11])
        else:
            aratoplam = int(yolcu) * int(ucuslar[i][11])
            aratoplam = str(aratoplam)
            ucret = ucret + [aratoplam]
    detay = []
    detay = ucuslar + [yolcu]
    print(ucret)
    return render_template("flights.html", ucuslar=ucuslar, ucuslarl=ucuslarl, yolcu=yolcu, ucret=ucret, detay=detay)


@app.route('/general-flights')
def general_flights(from_location, to_location, departure_date, adult, child, sort):
    connection = engine.connect()
    metadata = db.MetaData()
    fid = request.form.get('fid')
    print(fid)
    if departure_date == '':
        if sort == 'sorted':
            query = db.select([Flight, Flight_Details]).order_by(db.desc(Flight_Details.available_seats)).where(
                db.and_(Flight.from_location == from_location, Flight.to_location == to_location,
                        Flight.flight_id == Flight_Details.flight_id))
            result = connection.execute(query)
            ucuslar = result.fetchall()
        else:
            query = db.select([Flight, Flight_Details]).where(
                db.and_(Flight.from_location == from_location, Flight.to_location == to_location,
                        Flight.flight_id == Flight_Details.flight_id))
            result = connection.execute(query)
            ucuslar = result.fetchall()
    else:
        if sort == 'sorted':
            query = db.select([Flight]).order_by(db.desc(Flight_Details.available_seats)).where(
                db.and_(Flight.from_location == from_location, Flight.to_location == to_location,
                        Flight.depart_date == departure_date))
            result = connection.execute(query)
            ucuslar = result.fetchall()
        else:
            query = db.select([Flight]).where(
                db.and_(Flight.from_location == from_location, Flight.to_location == to_location,
                        Flight.depart_date == departure_date))
            result = connection.execute(query)
            ucuslar = result.fetchall()
    yolcu = child + adult
    print(ucuslar)
    ucret = [""]
    ucuslarl = len(ucuslar)
    for i in range(ucuslarl):
        if i == 0:
            ucret[0] = int(yolcu) * int(ucuslar[i][11])
        else:
            aratoplam = int(yolcu) * int(ucuslar[i][11])
            aratoplam = str(aratoplam)
            ucret = ucret + [aratoplam]
    detay = []
    detay = ucuslar + [yolcu]
    print(ucret)
    veli.id = ucret
    return render_template("general-flights.html", ucuslar=ucuslar, ucuslarl=ucuslarl, yolcu=yolcu, ucret=ucret,
                           detay=detay)


check = 0


@app.route('/passenger-info', methods=['POST', 'GET'])
@login_required
def passenger():
    global timer
    connection = engine.connect()
    metadata = db.MetaData()
    print(ali.kolcu)
    print(ali.id)
    query = db.select([Flight_Details.price]).where(Flight_Details.flight_id == ali.id)
    result = connection.execute(query)
    tekil = result.fetchall()
    ucret = int(tekil[0][0]) * ali.kolcu
    name = request.form.get('name')
    email = request.form.get('email')
    lastname = request.form.get('lastName')
    bday = request.form.get('bday')
    nationID = request.form.get('nationID')
    pNumber = request.form.get('pNumber')
    global check
    print(name)
    print(lastname)
    print(check)
    if not name == "" and not lastname == "" and not name == None and not lastname == None:
        check = check + 1
        print("düştüm")
        print(check)
        query = db.insert(Ticket_Info).values(user_id=current_user.id,
                                              flight_id=ali.id,
                                              flight_departure_date=1,
                                              status='pending',
                                              idNo=nationID,
                                              name=name,
                                              lastname=lastname,
                                              birthday=bday,
                                              mail=email,
                                              phone=pNumber)
        result = connection.execute(query)
        if check == ali.kolcu:
            timer = threading.Timer(600.0, sil)
            timer.start()
            print('başladı')
            check = 0
            return redirect(url_for('basket'))
    if ali.kolcu == None and ali.id == None:
        print('başladı')
        return redirect(url_for('basket'))
    return render_template("passenger-info.html", msg=check + 1, ucret=ucret)


meren = Yolcu(None, None)


@app.route('/basket', methods=['POST', 'GET'])
@login_required
def basket():
    global it
    global check
    check = 0
    connection = engine.connect()
    metadata = db.MetaData()
    if it == 666:
        query = db.delete(Ticket_Info).where(
            db.and_(Ticket_Info.status == "pending", Ticket_Info.user_id == current_user.id))
        ResultProxy = connection.execute(query)
        it = 0

    edit = request.form.get('edit')
    delete = request.form.get('delete')
    alldelete = request.form.get('alldelete')
    check = request.form.get('check')
    if edit != None:
        meren.id = edit
        print(meren.id)
        return redirect(url_for('edit_ticket'))
    if delete != None:
        query = db.delete(Ticket_Info).where(Ticket_Info.ticket_id == delete)
        result = connection.execute(query)
    if alldelete != None:
        query = db.delete(Ticket_Info).where(
            db.and_(Ticket_Info.user_id == current_user.id, Ticket_Info.status == 'pending'))
        result = connection.execute(query)
    print(edit)
    print(delete)
    print(alldelete)
    query = db.select([Ticket_Info]).where(
        db.and_(Ticket_Info.user_id == current_user.id, Ticket_Info.status == 'pending'))
    result = connection.execute(query)
    fids = result.fetchall()
    print(fids)
    fidsl = len(fids)
    biletler = []
    global totalfiyat
    totalfiyat = 0
    for i in range(fidsl):
        query = db.select([Flight, Flight_Details]).where(
            db.and_(Flight.flight_id == fids[i][2], Flight.flight_id == Flight_Details.flight_id))
        result = connection.execute(query)
        bilet = result.fetchall()
        biletler = biletler + bilet
        totalfiyat = totalfiyat + int(biletler[i][11])

    print(biletler)
    print(totalfiyat)
    query = db.select([Points.point]).where(Points.id == current_user.id)
    result = connection.execute(query)
    puan = result.fetchall()
    print(puan[0][0])
    offprice = totalfiyat - puan[0][0]
    print(offprice)
    point = request.form.get('point')
    msg = 'puansız'
    if point == 'point':
        totalfiyat = offprice
        msg = 'puanlı'
    print(check)
    if check == 'puanlı':
        query = db.select([Ticket_Info.ticket_id]).where(
            db.and_(Ticket_Info.user_id == current_user.id, Ticket_Info.status == 'pending'))
        result = connection.execute(query)
        tid = result.fetchall()
        for i in range(fidsl):
            query = db.select([Flight_Details.available_seats]).where(Flight_Details.flight_id == fids[i][2])
            result = connection.execute(query)
            kol = result.fetchall()
            if kol[0][0] == 0:
                query = db.update(Flight).values(status='dolu').where(Flight.flight_id == fidsl[i][2])
                result = connection.execute(query)
                return redirect(url_for('basket'))
            koltuk = int(kol[0][0]) - 1
            query = db.update(Flight_Details).values(available_seats=koltuk).where(
                Flight_Details.flight_id == fids[i][2])
            result = connection.execute(query)
            query = db.update(Ticket_Info).values(status='aktif').where(Ticket_Info.ticket_id == tid[i][0])
            result = connection.execute(query)

        query = db.update(Points).values(point=0).where(Points.id == current_user.id)
        result = connection.execute(query)
        print(totalfiyat)
        bonus = offprice * 0.3
        query = db.update(Points).values(point=bonus).where(Points.id == current_user.id)
        result = connection.execute(query)
        return redirect(url_for('basket'))
    if check == 'puansız':
        query = db.select([Ticket_Info.ticket_id]).where(
            db.and_(Ticket_Info.user_id == current_user.id, Ticket_Info.status == 'pending'))
        result = connection.execute(query)
        tid = result.fetchall()
        for i in range(fidsl):
            query = db.select([Flight_Details.available_seats]).where(Flight_Details.flight_id == fids[i][2])
            result = connection.execute(query)
            kol = result.fetchall()
            if kol[0][0] == 0:
                query = db.update(Flight).values(status='dolu').where(Flight.flight_id == fidsl[i][2])
                result = connection.execute(query)
                return redirect(url_for('basket'))
            koltuk = int(kol[0][0]) - 1
            query = db.update(Flight_Details).values(available_seats=koltuk).where(
                Flight_Details.flight_id == fids[i][2])
            result = connection.execute(query)
            query = db.update(Ticket_Info).values(status='aktif').where(Ticket_Info.ticket_id == tid[i][0])
            result = connection.execute(query)
        query = db.select([Points.point]).where(Points.id == current_user.id)
        result = connection.execute(query)
        varolanpuan = result.fetchall()
        bonus = totalfiyat * 0.3
        bonus = bonus + int(varolanpuan[0][0])
        query = db.update(Points).values(point=bonus).where(Points.id == current_user.id)
        result = connection.execute(query)
        return redirect(url_for('basket'))
    return render_template("basket.html", fids=fids, fidsl=fidsl, biletler=biletler, totalfiyat=totalfiyat, puan=puan,
                           offprice=offprice, msg=msg)


@app.route('/edit-ticket', methods=['POST', 'GET'])
@login_required
def edit_ticket():
    connection = engine.connect()
    metadata = db.MetaData()
    name = request.form.get('name')
    lastName = request.form.get('lastName')
    nationID = request.form.get('nationID')
    bday = request.form.get('bday')
    email = request.form.get('email')
    pNumber = request.form.get('pNumber')
    if name or lastName or nationID or bday or email or pNumber:
        query = db.update(Ticket_Info).values(idNo=nationID, name=name, lastname=lastName, birthday=bday, mail=email,
                                              phone=pNumber).where(Ticket_Info.ticket_id == meren.id)
        result = connection.execute(query)
    query = db.select([Ticket_Info]).where(Ticket_Info.ticket_id == meren.id)
    result = connection.execute(query)
    ticket = result.fetchall()
    query = db.select([Flight, Flight_Details]).where(
        db.and_(Flight.flight_id == ticket[0][2], Flight.flight_id == Flight_Details.flight_id))
    result = connection.execute(query)
    flight = result.fetchall()

    print(ticket)
    print(flight)
    return render_template('edit-ticket.html', ticket=ticket, flight=flight)


@app.route('/account')
@login_required
def account():
    global check
    check = 0
    connection = engine.connect()
    metadata = db.MetaData()
    query = db.select([Ticket_Info]).where(
        db.and_(Ticket_Info.user_id == current_user.id, Ticket_Info.status == 'aktif'))
    ResultProxy = connection.execute(query)
    aidler = ResultProxy.fetchall()
    print(aidler)
    query = db.select([Ticket_Info]).where(
        db.and_(Ticket_Info.user_id == current_user.id, Ticket_Info.status == 'pasif'))
    ResultProxy = connection.execute(query)
    pidler = ResultProxy.fetchall()
    print(pidler)
    name = current_user.first_name + ' ' + current_user.last_name
    id = 'AW-TK' + str(current_user.id)
    arrayl = len(aidler)
    array2l = len(pidler)
    aktif = []
    pasif = []
    for i in range(arrayl):
        query = db.select([Flight]).where(Flight.flight_id == aidler[i][2])
        ResultProxy = connection.execute(query)
        aktif = aktif + [ResultProxy.fetchall()]
    for i in range(array2l):
        query1 = db.select([Flight]).where(Flight.flight_id == pidler[i][2])
        ResultProxy1 = connection.execute(query1)
        pasif = pasif + [ResultProxy1.fetchall()]
    aktifl = len(aktif)
    pasifl = len(pasif)
    print(aktif)
    print(pasif)
    query = db.select([Points.point]).where(Points.id == current_user.id)
    result = connection.execute(query)
    puan = result.fetchall()
    print(puan)
    return render_template("account.html", name=name, id=id, aktif=aktif, aktifl=aktifl, pasif=pasif, pasifl=pasifl,
                           puan=puan)


@app.route('/dashboard', methods=['POST', 'GET'])
@roles_required('Admin')
def dashboard():
    global check
    check = 0
    connection = engine.connect()
    metadata = db.MetaData()
    airline_Name = request.form.get('airlineNamee')
    from_location = request.form.get('origine')
    to_location = request.form.get('wheree')
    departure_time = request.form.get('departureTimee')
    arrival_time = request.form.get('arrivalTimee')
    depart_date = request.form.get('departureDatee')
    total_seats = request.form.get('totalSeatse')
    status = 'aktif'
    price = request.form.get('price')
    flightid = request.form.get('flightID')
    query = db.select([Flight]).where(Flight.flight_id == 1)
    result = connection.execute(query)
    flightdetay = result.fetchall()
    flightdetayl = len(flightdetay)
    print(flightdetay)
    if airline_Name and from_location and to_location and departure_time and depart_date and arrival_time and total_seats and status:
        # obje nesnesine kayıt et
        object1 = Flight(
            airline_Name=airline_Name,
            from_location=from_location,
            to_location=to_location,
            departure_time=departure_time,
            depart_date=depart_date,
            arrival_time=arrival_time,
            total_seats=total_seats,
            status=status
        )

        # veritabanınıa uçuş ekle
        db.session.add(object1)
        db.session.commit()
        query = db.select([Flight.flight_id])
        result = connection.execute(query)
        id = result.fetchall()
        idl = len(id)
        for i in range(idl):
            fid = id[i][0]
        query = db.select([Flight_Details.flight_departure_date])
        result = connection.execute(query)
        id = result.fetchall()
        idl = len(id)
        for i in range(idl):
            fdate = id[i][0]
        fdate = int(fdate)
        fdate = fdate + 2
        fdate = str(fdate)
        print(fdate)
        query = db.insert(Flight_Details).values(flight_id=fid, price=price, available_seats=total_seats,
                                                 flight_departure_date=fdate)
        result = connection.execute(query)
        # /veritabanına uçuş ekle
        query = db.select([Flight.flight_id])
        result = connection.execute(query)
        editid = result.fetchall()
        editidl = len(editid)
        return render_template('dashboard.html', flightdetay=flightdetay, editid=editid, editidl=editidl)
    elif flightid:
        airline_Name = request.form.get('airlineName')
        from_location = request.form.get('origin')
        to_location = request.form.get('where')
        departure_time = request.form.get('departureTime')
        arrival_time = request.form.get('arrivalTime')
        depart_date = request.form.get('departureDate')
        total_seats = request.form.get('totalSeats')
        status = request.form.get('airlineID')
        price = request.form.get('pricee')
        query = db.select([Flight, Flight_Details]).where(
            db.and_(Flight.flight_id == flightid, Flight.flight_id == Flight_Details.flight_id))
        result = connection.execute(query)
        flightdetay = result.fetchall()
        flightdetayl = len(flightdetay)
        print(flightdetay)
        query = db.select([Flight.flight_id])
        result = connection.execute(query)
        editid = result.fetchall()
        editidl = len(editid)
        edit = request.form.get('edit')
        delete = request.form.get('delete')
        print(delete)
        print(edit)
        if not edit == None:
            query = db.update(Flight).values(airline_Name=airline_Name,
                                             from_location=from_location,
                                             to_location=to_location,
                                             departure_time=departure_time,
                                             depart_date=depart_date,
                                             arrival_time=arrival_time,
                                             total_seats=total_seats,
                                             status=status).where(Flight.flight_id == flightid)
            result = connection.execute(query)
            if not status == 'aktif':
                query = db.update(Ticket_Info).values(status=status).where(Ticket_Info.flight_id == flightid)
                result = connection.execute(query)
            query = db.update(Flight_Details).values(price=price).where(Flight_Details.flight_id == flightid)
            result = connection.execute(query)
            query = db.select([Flight]).where(Flight.flight_id == flightid)
            result = connection.execute(query)
            flightdetay = result.fetchall()
            flightdetayl = len(flightdetay)
        if not delete == None:
            query = db.delete(Flight).where(Flight.flight_id == flightid)
            result = connection.execute(query)
            query = db.update(Ticket_Info).values(status='pasif').where(Ticket_Info.flight_id == flightid)
            result = connection.execute(query)
            query = db.select([Flight]).where(Flight.flight_id == 1)
            result = connection.execute(query)
            flightdetay = result.fetchall()
            flightdetayl = len(flightdetay)
            return render_template("dashboard.html", flightdetay=flightdetay, editid=editid, editidl=editidl)
    query = db.select([Flight.flight_id])
    result = connection.execute(query)
    editid = result.fetchall()
    editidl = len(editid)
    # tüm bölümler girilmediyse uyarı ver
    return render_template("dashboard.html", editid=editid, editidl=editidl, flightdetay=flightdetay)


# giriş yapma fonksiyonu
@app.route('/login', methods=['POST', 'GET'])
def login():
    email = request.form.get("name")
    password1 = request.form.get("psw")
    remember = request.form.get("remember")

    # verilerin formdan geldiğini doğrula
    if not email or not password1:
        msg = 'Lütfen doldurunuz'
        return render_template('signin.html', msg=msg)
    else:
        # eposta adresinin daha önce kullanılıp kullanılmadığını doğrula
        user = User.query.filter_by(email=email).first()
        if user and user_manager.verify_password(password1, user):
            login_user(user, remember=remember)
            return redirect(url_for('index'))
        # giriş yap veya hata ver
        msg = 'giris başarız'
    return render_template('signin.html', msg=msg)


# çıkış yapma fonksiyonu
@app.route('/logout')
@login_required
def logout():
    connection = engine.connect()
    metadata = db.MetaData()
    query = db.delete(Ticket_Info).where(
        db.and_(Ticket_Info.status == "pending", Ticket_Info.user_id == current_user.id))
    ResultProxy = connection.execute(query)
    logout_user()
    flash("çıkış yaptınız")
    return redirect(url_for('index'))


# kayıt olma fonksiyonu
@app.route('/signup', methods=['POST', 'GET'])
def registering():
    connection = engine.connect()
    metadata = db.MetaData()
    # formdan verileri al
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("mail")
    email_confirmed_at = datetime.utcnow()
    password1 = request.form.get("password")
    print(first_name)
    print(last_name)
    print(email)
    print(password1)

    # tüm blokların doldurulduğunu kontrol et
    if not first_name or not last_name or not email or not password1:
        msg = "lütfen tüm alanları doldurun"
        return render_template('signup.html', msg=msg)
    else:
        # epostanın kullanılıp kullanılmadığını kontrol et
        if not User.query.filter(User.email == email).first():
            password = user_manager.hash_password(password1)
            user = User(first_name=first_name,
                        last_name=last_name,
                        email=email,
                        email_confirmed_at=datetime.utcnow(),
                        password=password)
            db.session.add(user)
            db.session.commit()
            query = db.insert(Points).values(point='10')
            result = connection.execute(query)
            msg = 'kayıt başarılı'
        # epostayı kayıt et veya hata ver
        else:
            msg = 'Bu e-posta zaten kullanılmaktadır'
        return render_template('signup.html', msg=msg)
