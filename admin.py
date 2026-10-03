from onewayswp import Admin

admin = Admin()

admin.load_keys(auto_generate=True)

secret = admin.secret_key
public = admin.public_key

print(f"{secret}\n{public}")

token1 = admin.create_license(
    type="duration",
    duration_seconds=150,
    additional_data={"future":["123", "321"]}
)

print(token1)