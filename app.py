from flask import Flask, request, jsonify
import memcache
import uuid

app = Flask(__name__)
cache = memcache.Client(['127.0.0.1:11211'], debug=0)


user_notifications = {}

@app.route('/notifications', methods=['POST'])
def create_notification():
    data = request.json
    notif_id = str(uuid.uuid4())
    cache.set(notif_id, data)
    username = data.get('username')
    if username in user_notifications:
        user_notifications[username].append(notif_id)
    else:
        user_notifications[username] = [notif_id]
    return jsonify({"message": "Notification created", "notif_id": notif_id}), 201

@app.route('/notifications/<notif_id>', methods=['GET'])
def get_notification(notif_id):
    notification = cache.get(notif_id)
    if notification:
        return jsonify(notification), 200
    else:
        return jsonify({"error": "Notification not found"}), 404

@app.route('/notifications/<notif_id>', methods=['PUT'])
def update_notification(notif_id):
    data = request.json
    existing_notification = cache.get(notif_id)
    if existing_notification:
        cache.set(notif_id, data)
        return jsonify({"message": "Notification updated"}), 200
    else:
        return jsonify({"error": "Notification not found"}), 404

@app.route('/notifications/<notif_id>', methods=['DELETE'])
def delete_notification(notif_id):
    existing_notification = cache.get(notif_id)
    if existing_notification:
        cache.delete(notif_id)
        for username, notifications in user_notifications.items():
            if notif_id in notifications:
                notifications.remove(notif_id)
        return jsonify({"message": "Notification deleted"}), 200
    else:
        return jsonify({"error": "Notification not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
