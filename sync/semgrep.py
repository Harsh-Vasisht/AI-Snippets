import os
import random
import joblib
import pickle
import tarfile
from cryptography.hazmat.primitives.asymmetric import dh, dsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

# --- Violation 1: Use DH instead of ECDH ---
parameters = dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())
private_key = parameters.generate_private_key()
peer_key = parameters.generate_private_key().public_key()
shared_key = private_key.exchange(peer_key)  # Should use ECDH instead

# --- Violation 2: Use of DSA (insecure) ---
dsa_private_key = dsa.generate_private_key(key_size=1024, backend=default_backend())  # Should use EdDSA or ECDSA

# --- Violation 3: Insecure PKCS1v15 Padding ---
from cryptography.hazmat.primitives.asymmetric import rsa
rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
message = b"secret"
rsa_key.sign(message, padding.PKCS1v15(), hashes.SHA256())  # Should use PSS instead

# --- Violation 4: Use of non-crypto secure RNG ---
otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # Should use secrets or os.urandom

# --- Violation 5: Unsafe Deserialization via joblib ---
model = joblib.load("model.pkl")  # Unsafe if file is from untrusted source

# --- Violation 6: Path Traversal in tarfile extraction ---
def unsafe_extract_tar(tar_path):
    with tarfile.open(tar_path) as tar:
        tar.extractall(path="./extracted")  # No check for path traversal

# --- Violation 7: Insecure Deserialization in AWS Lambda Function ---
def lambda_handler(event, context):
    user_input = event.get("data")
    obj = pickle.loads(user_input)  # Direct user input deserialization — unsafe!

# Call violations for demo (optional execution)
if __name__ == "__main__":
    unsafe_extract_tar("sample.tar")
    print("OTP generated (insecure):", otp)
