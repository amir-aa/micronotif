from flask import Flask, request, jsonify
import memcache,datetime,logging


app = Flask(__name__)
cache = memcache.Client(['127.0.0.1:11211'], debug=0)



import json

def save_dict_with_list(key, dictionary, cache):
    """
    Save a dictionary containing a list as the value in Memcached.

    Args:
        key (str): The key to store the dictionary under in Memcached.
        dictionary (dict): The dictionary to store in Memcached.
        cache (memcache.Client): The Memcached client instance.

    Returns:
        bool: True if the dictionary was successfully stored in Memcached, False otherwise.
    """
    try:
        # Serialize the dictionary to JSON
        serialized_dict = json.dumps(dictionary)
        # Store the serialized dictionary in Memcached
        cache.set(key, serialized_dict)
        return True
    except Exception as e:
        print(f"Error saving dictionary in Memcached: {e}")
        return False

def load_dict_with_list(key, cache)->list:
    """
    Load a dictionary containing a list as the value from Memcached.

    Args:
        key (str): The key under which the dictionary is stored in Memcached.
        cache (memcache.Client): The Memcached client instance.

    Returns:
        dict or None: The dictionary retrieved from Memcached, or None if not found or error occurred.
    """
    try:
        # Retrieve the serialized dictionary from Memcached
        serialized_dict = cache.get(key)
        if serialized_dict:
            # Deserialize the serialized dictionary from JSON
            return list(json.loads(serialized_dict))
        else:
            return None
    except Exception as e:
        print(f"Error loading dictionary from Memcached: {e}")
        return None

user_notifications = {} #{username:[{notifmessage:message,notiftype:type,notifdt:datetime}]}
@app.route('/addnotif',methods=["POST"])
def addNotif():
    try:
        data=request.get_json()
        user=data['username']
        notif_from=data['notiffrom']
        if user in user_notifications.keys():
            user_notifications[user].append({"notifmessage":data['message'],"notiftype":data['notiftype'],'notifdt':datetime.datetime.now(),"notiffrom":notif_from})
        else:
            user_notifications[user]=[]
            user_notifications[user].append({"notifmessage":data['message'],"notiftype":data['notiftype'],'notifdt':datetime.datetime.now(),"notiffrom":notif_from})
        return jsonify({"message":'successfully added'})
    except Exception as ex:
        logging.error(f"adding notif ERROR {str(ex)}")
        return jsonify({"message":"something wrong with adding notif","error":str(ex)}),500
    
@app.route('/clearnotifs/<user>')
def clearNotifs(user):
    user_notifications[user]=[]
    logging.info(f"successfully removed notifs for user {user}")
    return jsonify({"message":f"successfully removed notifs for user {user}"})

@app.route('/removenotif/<user>/<index>')
def removeNotif_byid(user,index):
    try:
        user_notifications[user].pop(int(index))
        logging.info(f"successfully removed {str(user_notifications[user][int(index)])}")
        return jsonify({"message":"successfully removed"})
    except Exception as ex:
        return jsonify({"message":"something wrong with removing notif","error":str(ex)})

@app.route('/getnotifs/<user>')
def getNotifs_by_username(user):
    if user not in user_notifications.keys():
        return jsonify({"message":"Not Found"}),404
    return jsonify(user_notifications[user])
if __name__ == '__main__':
    app.run(debug=False)
