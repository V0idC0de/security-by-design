import sqlite3
import subprocess


def get_user_info(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


def ping_host(host):
    subprocess.call(f"ping -c 1 {host}", shell=True)


if __name__ == "__main__":
    user = input("Enter username: ")
    print(get_user_info(user))
    host = input("Enter host to ping: ")
    ping_host(host)
