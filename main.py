import hashlib
import datetime
import google.oauth2.id_token
from flask import Flask, render_template, request
from google.auth.transport import requests
from flask import Flask, render_template
from google.cloud import datastore

datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

#user_key = datastore_client.key("User", "User1")
#user_task = datastore.Entity(key=user_key)
#datastore_client.put(user_task)

#room_key = datastore_client.key("Room", "Room1")
#room_task = datastore.Entity(key=room_key)
#datastore_client.put(room_task)

#booking_key = datastore_client.key("Booking", "Booking1")
#booking_task = datastore.Entity(key=booking_key)
#datastore_client.put(booking_task)

def getClientInfo():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
    return claims

def addRoom(result):
    room_key = datastore_client.key("Room",result['name'])
    room_task = datastore.Entity(key=room_key)
    room_task.update({
        'Name': result['name'],
        'Capacity': result['capacity'],
    })
    datastore_client.put(room_task)


def addBooking(result,email):
    str = result['roomid']+email+result['dateIn']+result['dateOut']
    book_key = datastore_client.key("Booking",str)
    book_task = datastore.Entity(key=book_key)
    book_task.update({
        'RoomId': result['roomid'],
        'UserEmail': email,
        'DateIn': result['dateIn'],
        'DateOut': result['dateOut'],
    })
    datastore_client.put(book_task)

def editPrevBooking(result,email):
    datastore_client.delete(datastore_client.key("Booking",result['str']))
    addBooking(result,email)

def deleteBookingDB(roomid,dateIn,dateOut,UserEmail):
    str = roomid+UserEmail+dateIn+dateOut
    datastore_client.delete(datastore_client.key("Booking",str))


def fetchBookingDuplicate(result):
    query = datastore_client.query(kind='Booking')
    query.add_filter('RoomId', "=", result['roomid'])
    query.add_filter("DateIn", "=", result['dateIn'])
    query.add_filter("DateOut", "=", result['dateOut'])
    bookings = query.fetch()
    return bookings

def fetchRoomsByName(search):
    query = datastore_client.query(kind='Room')
    query.add_filter("Name", "=", search)
    rooms = query.fetch()
    return rooms

def fetchRoomsAll():
    query = datastore_client.query(kind='Room')
    query.order = ["-Name"]
    rooms = query.fetch()
    return rooms

def fetchBookingsByRoomId(roomid):
    query = datastore_client.query(kind='Booking')
    query.add_filter("RoomId", "=", roomid)
    bookings = query.fetch()
    return bookings

def rangeCheck(result,bookings):
    dateIn =  datetime.datetime.strptime(result['dateIn'], "%Y-%m-%d")
    dateOut =  datetime.datetime.strptime(result['dateOut'], "%Y-%m-%d")
    err=""
    for booking in bookings:
        start = datetime.datetime.strptime(booking['DateIn'], "%Y-%m-%d")
        end = datetime.datetime.strptime(booking['DateOut'], "%Y-%m-%d")
        if start <= dateIn <= end:
            err = "Booking on these dates is Full"
        elif start <= dateOut <= end:
            err = "Booking on these dates is Full"
    return err

def filterBookingsByDate(lists,dateFrom,dateTo):
    DateFrom =  datetime.datetime.strptime(dateFrom, "%Y-%m-%d")
    DateTo =  datetime.datetime.strptime(dateTo, "%Y-%m-%d")
    result=[]
    for list1 in lists:
        start = datetime.datetime.strptime(list1['DateIn'], "%Y-%m-%d")
        end = datetime.datetime.strptime(list1['DateOut'], "%Y-%m-%d")

        if DateFrom <= start <= DateTo:
            result.append(list1)
        elif DateFrom <= end <= DateTo:
            result.append(list1)
    return result


app = Flask(__name__)

@app.route('/roomBookDB', methods=['POST'])
def roomBookDB():
    claims = getClientInfo()
    result = request.form
    email = claims['email']
    rooms = fetchRoomsAll()
    bookings =  fetchBookingsByRoomId(result['roomid'])
    res = rangeCheck(result,bookings)
    if res != "":
        err = res
    else:
        addBooking(result,email)
        err=""
    return render_template('index.html',user_data=claims, rooms=rooms, error=err)

@app.route('/listBookings')
def listBookings():
    roomid = request.args.get('roomid')
    claims = getClientInfo()
    rooms = fetchRoomsAll()
    bookings = fetchBookingsByRoomId(roomid)
    return render_template('index.html',user_data=claims,roomid=roomid, rooms=rooms , bookings=bookings)

@app.route('/searchByRoom')
def searchByRoom():
    # claims = getClientInfo()
     search = request.args.get('search')
     rooms = fetchRoomsByName(search)
     return render_template('index.html', rooms=rooms)#, user_data=claims

@app.route('/bookRoom')
def bookRoom():
    roomid = request.args.get('roomid')
    #claims = getClientInfo()
    rooms = fetchRoomsAll()
    return render_template('book.html',roomid=roomid, rooms=rooms)#,user_data=claims

@app.route('/deleteBooking')
def deleteBooking():
    claims = getClientInfo()
    roomid = request.args.get('roomid')
    dateIn = request.args.get('dateIn')
    dateOut = request.args.get('dateOut')
    UserEmail = request.args.get('UserEmail')
    deleteBookingDB(roomid,dateIn,dateOut,UserEmail)
    rooms = fetchRoomsAll()
    bookings = fetchBookingsByRoomId(roomid)
    return render_template('index.html',user_data=claims, roomid=roomid, rooms=rooms , bookings=bookings)

@app.route('/editBooking')
def editBooking():
    result = request.args
    #claims = getClientInfo()
    str = result['roomid']+result['UserEmail']+result['dateIn']+result['dateOut']

    res = fetchRoomsByName(result['roomid'])
    return render_template('editBooking.html',bookings=result, rooms=res,roomid=result['roomid'],str=str)#,user_data=claims


@app.route('/editBookDB', methods=['POST'])
def editBookDB():
    claims = getClientInfo()
    result = request.form
    email = claims['email']
    rooms = fetchRoomsAll()
    lists =  fetchBookingsByRoomId(result['roomid'])
    bookings=[]
    for list1 in lists:
        if result['str'] != list1['RoomId']+list1['UserEmail']+list1['DateIn']+list1['DateOut']:
            bookings.append(list1)
    res = rangeCheck(result,bookings)
    if res != "":
        err = res
    else:
        editPrevBooking(result,email)
        err=""
    return render_template('index.html',user_data=claims, rooms=rooms, error=err)


@app.route('/', methods=['POST'])
def save():
    #claims = getClientInfo()
    result = request.form
    res = fetchRoomsByName(result['name'])
    rooms = fetchRoomsAll()
    if sum(1 for _ in res) ==0:
        addRoom(result)
        err=""
    else:
        err="Room With this name already exists"
    return render_template('index.html',error=err, rooms=rooms)#,user_data=claims

@app.route('/filterByDate', methods=['POST'])
def filterByDate():
     result = request.form
     claims = getClientInfo()
     rooms = fetchRoomsAll()
     lists =  fetchBookingsByRoomId(result['roomid'])
     res = filterBookingsByDate(lists,result['dateFrom'],result['dateTo'])
     return render_template('index.html',user_data=claims, roomid=result['roomid'], rooms=rooms , bookings=res)

@app.route('/')
def root():
     rooms = fetchRoomsAll()
     return render_template('index.html', rooms=rooms)#,user_data=claims

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
