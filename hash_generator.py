from hashlib import sha256
print("==>  ",sha256(input("HASH sha256: ").encode()).hexdigest())