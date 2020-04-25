from dotenv import load_dotenv
import os

load_dotenv()
HOST = os.getenv('DB_HOST')
NAME = os.getenv('DB_NAME')
PASS = os.getenv('DB_PASS')
USER = os.getenv('DB_USER')
CERT = b'-----BEGIN PUBLIC KEY-----\n' \
       b'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlc6LMgsz5b2m2Q3M/ps2\n' \
       b'XRKIuBRdwOUrY532F9OmkYrrdPsVpDpWTjRsc3Srrc9hUCIWNMQa++Cjq4yMFTHl\n' \
       b'D3Yn8x1kHJnO+DWw7sIJvg1+8PxZWZnslXUHjFRuuxUNUH5wxy5z/C1T6aMqIO93\n' \
       b'tXJty1q2nzVdW9GON0AI0oPHhSdPJalbxC7mo1ExZRa5SoYiBv8xe7ER4e1Neb3K\n' \
       b'sUF+Rfny1t79PQJC6uk0FwnloEQVj5yYvmwAv8HTda0mhFY0GdYqNk5+ks0D3hGg\n' \
       b'3D7FspI98MOX1lUatEJDq6/xE0JlK111uh24i7aZaZD5Bn3dqZl83zK4PdexXE/z\n' \
       b'JwIDAQAB\n' \
       b'-----END PUBLIC KEY-----'