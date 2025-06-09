import os
import hashlib
import requests
from datetime import datetime
from tkinter import Tk, Label, Button, filedialog, messagebox, Frame
from tkinterdnd2 import DND_FILES, TkinterDnD


def get_file_times(filepath):
    stats = os.stat(filepath)
    created_time = datetime.fromtimestamp(stats.st_ctime)
    modified_time = datetime.fromtimestamp(stats.st_mtime)
    return created_time, modified_time

def calculate_sha256(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def validate_and_upload(filepath):
    if not filepath.lower().endswith(".xlsx"):
        messagebox.showerror("오류", "엑셀 파일(.xlsx)만 업로드 가능합니다.")
        return

    filename = os.path.basename(filepath)
    created_time, modified_time = get_file_times(filepath)
    sha256 = calculate_sha256(filepath)

    try:
        res = requests.post("http://localhost:5000/register", json={
            "filename": filename,
            "created_time": created_time.isoformat(),
            "modified_time": modified_time.isoformat(),
            "sha256": sha256
        })

        result = res.json()
        if not result["valid"]:
            messagebox.showerror("무결성 실패", f"{result['reason']} (차이: {round(result['diff_minutes'])}분)")
            return

        with open(filepath, 'rb') as f:
            upload_res = requests.post("http://localhost:5000/upload", files={'file': (filename, f)})
        if upload_res.status_code == 200:
            messagebox.showinfo("성공", "✅ 무결성 통과 및 업로드 완료")
        else:
            messagebox.showerror("업로드 실패", "서버 업로드 중 오류 발생")
    except Exception as e:
        messagebox.showerror("에러", f"서버 통신 실패: {e}")

def select_file():
    filepath = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if filepath:
        validate_and_upload(filepath)

def handle_drop(event):
    filepath = event.data.strip('{}')  # Windows 경로는 중괄호로 감싸져 있음
    validate_and_upload(filepath)

# --- GUI 구성 ---
app = TkinterDnD.Tk()
app.title("Excel 무결성 업로더")
app.geometry("400x300")
app.resizable(False, False)

Label(app, text="🔒 Excel 파일 무결성 검사기", font=("Arial", 16)).pack(pady=20)

frame = Frame(app, width=350, height=100, bg="#f0f0f0", relief="ridge", bd=2)
frame.pack(pady=10)
frame.pack_propagate(False)

Label(frame, text="여기에 파일을 드래그하거나\n아래 버튼을 클릭하세요", font=("Arial", 11)).pack(expand=True)

frame.drop_target_register(DND_FILES)
frame.dnd_bind('<<Drop>>', handle_drop)

Button(app, text="📂 파일 선택", command=select_file, width=20, height=2).pack(pady=15)

Label(app, text="Made By JH", font=("Arial", 9), fg="gray").pack(side="bottom", pady=5)

app.mainloop()
