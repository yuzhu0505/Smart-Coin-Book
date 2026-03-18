import mysql.connector
conn = mysql.connector.connect(
    user = "root",
    password = "112024505",
    host = "localhost",
    database = "expensesystem"
)
print("資料庫連線成功！")

from fastapi import FastAPI, Request, Body
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import json

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="dinu")

# 註冊會員
@app.post("/api/member")
def signup(body=Body(None)):
    body = json.loads(body)
    name = body["name"]
    email = body["email"]
    password = body["password"]
    # 檢查 email 是否重複
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM member WHERE email = %s", (email,))
    result = cursor.fetchone()
    # 如果 result 是 None，表示沒有找到重複的 email，可以註冊
    if result == None:
        cursor.execute("INSERT INTO member(name, email, password) " \
        "VALUES(%s, %s, %s)", (name, email, password))
        conn.commit()
        return {"ok": True}

    else:
        return {"ok": False}    

# 登入
@app.put("/api/member/auth")
def signin(request:Request, body=Body(None)):
    body = json.loads(body)
    email = body["email"]
    password = body["password"]

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM member WHERE email = %s AND password = %s", (email, password))
    result = cursor.fetchone()
    # 如果 result 是 None，表示沒有找到符合的 email 和 password，登入失敗
    if result == None:
        request.session["member"] = None
        return {"ok": False}
    else:
        request.session["member"] = {
            "member_id": result[0],
            "name": result[1],
            "email": result[2]
        }
        return {"ok": True}
    

# 檢查登入狀態
@app.get("/api/member/auth")    
def checkstatus(request:Request):
    # 如果 session 中有 member，表示已經登入，回傳 member 的 name 和 email
    if "member" in request.session and request.session["member"] != None:
        member = request.session["member"]
        return {"ok": True, "member_id": member["member_id"], "name": member["name"], "email": member["email"]}
    else:
        return {"ok": False}

# 登出
@app.delete("/api/member/auth")
def signout(request:Request):
    request.session["member"] = None
    return {"ok":True}

# 顯示花費紀錄
@app.get("/api/member/auth/expenses")    
def checkexpenses(request:Request):
    member = request.session["member"]
    member_id = member["member_id"]
    email = member["email"]
    cursor = conn.cursor()
    cursor.execute("""
                SELECT expense.item, expense.cost, expense.category, expense.created_time 
                FROM member INNER JOIN expense 
                ON member.id = expense.member_id 
                WHERE member.id = %s 
                ORDER BY expense.created_time DESC 
                LIMIT 10;
            """, (member_id,))
    
    result = cursor.fetchall()
    return {"ok": True, "expenses": result}

# 新增花費紀錄
@app.post("/api/member/auth/expenses")
def input_expense(request:Request, body=Body(None)):
    body = json.loads(body)
    item = body["item"]
    cost = body["cost"]
    category = body["category"]
    member = request.session["member"]
    member_id = member["member_id"]
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO expense(member_id, item, cost, category) 
                   VALUES(%s, %s, %s, %s)
                   """, (member_id, item, cost, category))
    conn.commit()
    return {"ok": True}


# 計算平均花費
@app.get("/api/member/auth/expenses/avg")
def calculate_avg_expense(request:Request):
    member = request.session["member"]
    member_id = member["member_id"]
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT IFNULL(AVG(cost), 0) FROM expense 
                   WHERE member_id = %s
                    AND YEAR(created_time) = YEAR(CURRENT_DATE())
                    AND MONTH(created_time) = MONTH(CURRENT_DATE());
                   """, (member_id,))
    result = cursor.fetchone()
    avg_cost = float(result[0])
    return {"ok": True, "avg_cost": avg_cost}


app.mount("/", StaticFiles(directory="static", html=True))