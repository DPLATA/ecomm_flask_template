import uuid

def generate_order_number():
    return str(uuid.uuid4().hex)[:8].upper()