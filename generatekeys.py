# Core Python module 
import pickle
from pathlib import Path 

import streamlit_authenticator as stauth

def hash_passwords(passwords):
    return stauth.Hasher(passwords).generate()

#convert plain text passwords to hashed passwords 
hashed_passwords = hash_passwords(['admin', 'def'])
# streamlit_authenticator used bcrypt for password hashing 


file_path=Path(__file__).parent / "hashed_passwords.pkl"

with file_path.open("wb") as file:
	pickle.dump(hashed_passwords,file)