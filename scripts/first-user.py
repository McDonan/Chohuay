import bcrypt
pin = "1234"
hashed = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
print(hashed)