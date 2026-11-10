from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

is_server_online = True

VALID_CODES = {
    "VIP-12345": {
        "user": "Hmad",
        "expiry": "2026-12-31",
        "device": None,
        "banned": False
    }
}

@app.route('/', methods=['POST'])
def verify():
    global is_server_online
    
    # ✅ استخدام force=True لتجاوز مشاكل الترميز
    data = request.get_json(force=True, silent=True)
    if not data:
        # إذا لم يتم العثور على JSON، نحاول قراءته كـ form data
        data = request.form.to_dict()
    
    if not data:
        return jsonify({"status": "error", "message": "Missing JSON body"}), 400

    app_secret = data.get('secret')
    user_code = data.get('code')
    device_fingerprint = data.get('device')

    # التحقق من المفتاح السري
    if app_secret != "HmadApp2026Secret":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    # التحقق من حالة السيرفر
    if not is_server_online:
        return jsonify({"status": "error", "message": "Server Offline"}), 503

    if not user_code:
        return jsonify({"status": "error", "message": "Missing code"}), 400

    # التحقق من الكود
    if user_code in VALID_CODES:
        license_data = VALID_CODES[user_code]

        if license_data["banned"]:
            return jsonify({"status": "error", "message": "Banned"}), 403

        expiry_date = datetime.datetime.strptime(license_data["expiry"], "%Y-%m-%d").date()
        if expiry_date < datetime.date.today():
            return jsonify({"status": "error", "message": "Expired"}), 403

        if license_data["device"] and license_data["device"] != device_fingerprint:
            return jsonify({"status": "error", "message": "Device Mismatch"}), 403

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
