from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# مفتاح التحكم بالسيرفر (true = شغال، false = طافي)
is_server_online = True

# كود التحقق (مؤقتاً، يمكنك ربطه بقاعدة بيانات لاحقاً)
VALID_CODES = {
    "VIP-12345": {
        "user": "Hmad",
        "expiry": "2026-12-31",
        "device": None,
        "banned": False
    }
}

@app.route('/', methods=['GET'])
def verify():
    global is_server_online
    
    # 1. التحقق من المفتاح السري أولاً (لأنه الأهم)
    app_secret = request.headers.get("X-App-Key")
    if app_secret != "HmadApp2026Secret":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    # 2. التحقق من حالة السيرفر
    if not is_server_online:
        return jsonify({"status": "error", "message": "Server Offline"}), 503

    # 3. قراءة الكود والبصمة من الرابط
    user_code = request.args.get('code')
    device_fingerprint = request.args.get('device')

    if not user_code:
        return jsonify({"status": "error", "message": "Missing code"}), 400

    # 4. التحقق من الكود
    if user_code in VALID_CODES:
        license_data = VALID_CODES[user_code]

        # التحقق من الحظر
        if license_data["banned"]:
            return jsonify({"status": "error", "message": "Banned"}), 403

        # التحقق من تاريخ الانتهاء
        expiry_date = datetime.datetime.strptime(license_data["expiry"], "%Y-%m-%d").date()
        if expiry_date < datetime.date.today():
            return jsonify({"status": "error", "message": "Expired"}), 403

        # التحقق من البصمة
        if license_data["device"] and license_data["device"] != device_fingerprint:
            return jsonify({"status": "error", "message": "Device Mismatch"}), 403

        # تسجيل البصمة إذا كانت أول مرة
        if not license_data["device"]:
            license_data["device"] = device_fingerprint

        return jsonify({
            "status": "success",
            "user": license_data["user"],
            "expiry": license_data["expiry"]
        })

    return jsonify({"status": "error", "message": "Invalid Code"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
