from flask import Flask, request
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register_metadata():
    data = request.get_json()

    filename = data.get('filename')
    created_str = data.get('created_time')
    modified_str = data.get('modified_time')

    if not filename or not created_str or not modified_str:
        return {"valid": False, "reason": "필수 메타데이터 누락"}, 400

    try:
        created_time = datetime.fromisoformat(created_str)
        modified_time = datetime.fromisoformat(modified_str)
    except ValueError:
        return {"valid": False, "reason": "시간 형식 오류"}, 400

    diff_seconds = abs((modified_time - created_time).total_seconds())

    if diff_seconds <= 30:
        return {"valid": True}, 200
    else:
        return {
            "valid": False,
            "reason": f"{round(diff_seconds)}초 차이",
        }, 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
