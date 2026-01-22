import random

rng = random.SystemRandom()

def hash_string(string: str, salt, rounds=1000):
    hash_value = salt

    for _ in range(rounds):
        for char in string:
            hash_value ^= ord(char) # mix character
            hash_value = (hash_value * 31) # spread bits
            hash_value = hash_value & 0xFFFFFFFF # keep 32 bits

    return hash_value

class Hash:
    @staticmethod
    def hash_password(password: str):
        salt = rng.randint(0, 0xFFFFFFFF) # generate a random 32-bit salt
        hashed = hash_string(password, salt)
        return salt, hashed

    @staticmethod
    def verify_password(input_password: str, stored_salt, stored_hash):
        hashed = hash_string(input_password, stored_salt)
        return hashed == stored_hash

if __name__ == "__main__":
    password = "admin"
    salt, hashed = Hash.hash_password(password)
    print(f"Salt: {salt}, Hashed: {hashed}")
    success = Hash.verify_password("admin", salt, hashed)
    print(f"Password verification success: {success}")