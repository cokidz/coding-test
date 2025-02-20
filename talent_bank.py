import sqlite3
import pyqrcode
import png
from pyzbar.pyzbar import decode
from PIL import Image

# 데이터베이스 연결
conn = sqlite3.connect('talent_bank.db')
c = conn.cursor()

# 학생 테이블 생성 (ID, 이름, 잔액)
c.execute('''CREATE TABLE IF NOT EXISTS students
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, balance INTEGER)''')

# 교사 인증키 설정
TEACHER_KEY = "teacher123"

### 학생 생성 및 QR 코드 생성 함수
def create_student(name):
    """학생을 생성하고 ID를 부여하며 QR 코드를 생성합니다."""
    c.execute("INSERT INTO students (name, balance) VALUES (?, 0)", (name,))
    conn.commit()
    student_id = c.lastrowid  # 새로 생성된 학생의 ID
    generate_qr_code(student_id)
    return student_id

def generate_qr_code(student_id):
    """학생 ID로 QR 코드를 생성하고 PNG 파일로 저장합니다."""
    qr = pyqrcode.create(str(student_id))
    qr.png(f'student_{student_id}.png', scale=6)

### QR 코드 인식 함수
def recognize_qr_code(image_path):
    """이미지 파일에서 QR 코드를 읽어 학생 ID를 반환합니다."""
    image = Image.open(image_path)
    decoded_objects = decode(image)
    if decoded_objects:
        return decoded_objects[0].data.decode('utf-8')
    return None

### 교사 인증 함수
def teacher_authentication():
    """교사 인증키를 입력받아 인증 여부를 확인합니다."""
    key = input("교사 인증키를 입력하세요: ")
    return key == TEACHER_KEY

### 달란트 입금 함수
def deposit(student_id, amount):
    """교사 인증 후 학생 계좌에 달란트를 입금합니다."""
    if teacher_authentication():
        c.execute("UPDATE students SET balance = balance + ? WHERE id = ?", (amount, student_id))
        conn.commit()
        print(f"{amount} 달란트가 입금되었습니다.")
    else:
        print("인증 실패")

### 달란트 출금 함수
def withdraw(student_id, amount):
    """교사 인증 후 학생 계좌에서 달란트를 출금합니다."""
    if teacher_authentication():
        c.execute("SELECT balance FROM students WHERE id = ?", (student_id,))
        balance = c.fetchone()
        if balance and balance[0] >= amount:
            c.execute("UPDATE students SET balance = balance - ? WHERE id = ?", (amount, student_id))
            conn.commit()
            print(f"{amount} 달란트가 출금되었습니다.")
        else:
            print("잔액 부족 또는 학생 ID가 존재하지 않습니다.")
    else:
        print("인증 실패")

### 잔액 조회 함수
def check_balance(student_id):
    """학생 ID로 현재 잔액을 조회합니다."""
    c.execute("SELECT balance FROM students WHERE id = ?", (student_id,))
    result = c.fetchone()
    if result:
        print(f"현재 잔액: {result[0]} 달란트")
    else:
        print("학생 ID가 존재하지 않습니다.")

### 메인 프로그램
def main():
    while True:
        print("\n=== 주일학교 달란트 은행 시스템 ===")
        print("1. 학생 생성")
        print("2. QR 코드 인식")
        print("3. 달란트 입금")
        print("4. 달란트 출금")
        print("5. 잔액 조회")
        print("6. 종료")
        choice = input("선택: ")

        if choice == '1':
            name = input("학생 이름: ")
            student_id = create_student(name)
            print(f"학생 ID: {student_id} (QR 코드는 student_{student_id}.png로 저장됨)")

        elif choice == '2':
            image_path = input("QR 코드 이미지 경로: ")
            student_id = recognize_qr_code(image_path)
            if student_id:
                print(f"인식된 학생 ID: {student_id}")
            else:
                print("QR 코드를 인식할 수 없습니다.")

        elif choice == '3':
            student_id = int(input("학생 ID: "))
            amount = int(input("입금할 달란트: "))
            deposit(student_id, amount)

        elif choice == '4':
            student_id = int(input("학생 ID: "))
            amount = int(input("출금할 달란트: "))
            withdraw(student_id, amount)

        elif choice == '5':
            student_id = int(input("학생 ID: "))
            check_balance(student_id)

        elif choice == '6':
            print("프로그램을 종료합니다.")
            break

        else:
            print("잘못된 선택입니다. 다시 입력해주세요.")

if __name__ == "__main__":
    main()

# 데이터베이스 연결 종료
conn.close()