from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register_metadata():
    data = request.get_json()

    filename = data.get('filename')
    created_str = data.get('created_time')
    modified_str = data.get('modified_time')

    if not filename or not created_str or not modified_str:
        return {"valid": False, "reason": "필수 메타데이터 누락"}, 400

    created_time = datetime.fromisoformat(created_str)
    modified_time = datetime.fromisoformat(modified_str)

    diff_seconds = abs((modified_time - created_time).total_seconds())

    if diff_seconds <= 30:
        return {"valid": True, "diff_minutes": diff_seconds}, 200
    else:
        return {
            "valid": False,
            "reason": f"파일 수정 시간이 생성 시간보다 {round(diff_seconds)}초 이상 지남",
            "diff_minutes": diff_seconds
        }, 200

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file:
        file.save(f"uploads/{file.filename}")
        return {"status": "uploaded"}, 200
    return {"error": "파일 없음"}, 400

if __name__ == '__main__':
    app.run(debug=True)
