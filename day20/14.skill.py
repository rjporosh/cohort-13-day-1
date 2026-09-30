# --------------------------------------------
# Fake Database
# --------------------------------------------

ORDERS = {
    "1001": {
        "order_id": "1001",
        "status": "Shipped",
        "amount": 5000,
        "delivery_partner": "Pathao",
        "delivery_days_remaining": 2
    },
    "1002": {
        "order_id": "1002",
        "status": "Processing",
        "amount": 3000,
        "delivery_partner": "Steadfast",
        "delivery_days_remaining": 4
    },
    "1003": {
        "order_id": "1003",
        "status": "Delivered",
        "amount": 7000,
        "delivery_partner": "RedX",
        "delivery_days_remaining": 0
    }
}


# ============================================
# TOOLS
# ============================================

# --------------------------------------------
# Order Tracking Tools
# --------------------------------------------

def get_order_status(order_id: str) -> str:
    """
    Tool 1
    Get the current status of an order.
    """

    order = ORDERS.get(order_id)

    if not order:
        return "Order not found."

    return order["status"]


def get_delivery_information(order_id: str) -> dict:
    """
    Tool 2
    Get delivery-related information.
    """

    order = ORDERS.get(order_id)

    if not order:
        return {}

    return {
        "delivery_partner": order["delivery_partner"],
        "days_remaining": order["delivery_days_remaining"]
    }


def calculate_delivery_eta(days_remaining: int) -> str:
    """
    Tool 3
    Calculate a human-readable delivery estimate.
    """
    if days_remaining == 0:
        return "Delivered"

    if days_remaining == 1:
        return "Expected tomorrow"
    return f"Expected in {days_remaining} days"

# --------------------------------------------
# Order Cancellation Tools
# --------------------------------------------
def get_order_details(order_id: str) -> dict:
    """
    Tool 1
    Get complete order information.
    """

    return ORDERS.get(order_id)

def check_cancellation_policy(order: dict) -> dict:
    """
    Tool 2
    Apply business rules for cancellation.
    """

    if not order:
        return {
            "eligible": False,
            "reason": "Order not found."
        }

    if order["status"] == "Delivered":
        return {
            "eligible": False,
            "reason": "Delivered orders cannot be cancelled."
        }

    if order["status"] == "Shipped":
        return {
            "eligible": False,
            "reason": "Shipped orders cannot be cancelled."
        }

    return {
        "eligible": True,
        "reason": "Order can be cancelled."
    }


def cancel_order_in_system(order_id: str) -> dict:
    """
    Tool 3
    Actually cancel the order.
    """

    order = ORDERS.get(order_id)

    if not order:
        return {
            "success": False,
            "message": "Order not found."
        }

    order["status"] = "Cancelled"

    return {
        "success": True,
        "message": f"Order {order_id} has been cancelled."
    }

# --------------------------------------------
# Refund Processing Tools
# --------------------------------------------
def check_refund_eligibility(order: dict) -> dict:
    """
    Tool 1
    Check whether the order is eligible for refund.
    """
    if not order:
        return {
            "eligible": False,
            "reason": "Order not found."
        }

    if order["status"] != "Delivered":
        return {
            "eligible": False,
            "reason": "Only delivered orders can be refunded."
        }

    return {
        "eligible": True,
        "reason": "Order is eligible for refund."
    }


def calculate_refund_amount(order: dict) -> float:
    """
    Tool 2
    Calculate refund amount.
    """
    return order["amount"]

def create_refund(order_id: str, amount: float) -> dict:
    """
    Tool 3
    Create the refund.
    """

    return {
        "success": True,
        "order_id": order_id,
        "refund_amount": amount,
        "message": f"Refund of {amount} BDT has been initiated."
    }


# ============================================
# SKILLS
# ============================================

# --------------------------------------------
# Skill 1: Order Tracking
# --------------------------------------------

def track_order(order_id: str) -> dict:
    """
    Skill: Order Tracking

    Uses:
        1. get_order_status()
        2. get_delivery_information()
        3. calculate_delivery_eta()
    """

    status = get_order_status(order_id)

    if status == "Order not found.":
        return {
            "success": False,
            "message": "Order not found."
        }

    delivery_info = get_delivery_information(order_id)

    eta = calculate_delivery_eta(
        delivery_info["days_remaining"]
    )

    return {
        "success": True,
        "order_id": order_id,
        "status": status,
        "delivery_partner": delivery_info["delivery_partner"],
        "eta": eta
    }


# --------------------------------------------
# Skill 2: Order Cancellation
# --------------------------------------------
def cancel_order(order_id: str) -> dict:
    """
    Skill: Order Cancellation

    Uses:
        1. get_order_details()
        2. check_cancellation_policy()
        3. cancel_order_in_system()
    """

    order = get_order_details(order_id)

    if not order:
        return {
            "success": False,
            "message": "Order not found."
        }

    eligibility = check_cancellation_policy(order)

    if not eligibility["eligible"]:
        return {
            "success": False,
            "message": eligibility["reason"]
        }

    cancellation_result = cancel_order_in_system(order_id)

    return cancellation_result


# --------------------------------------------
# Skill 3: Refund Processing
# --------------------------------------------

def process_refund(order_id: str) -> dict:
    """
    Skill: Refund Processing

    Uses:
        1. get_order_details()
        2. check_refund_eligibility()
        3. calculate_refund_amount()
        4. create_refund()
    """

    order = get_order_details(order_id)

    if not order:
        return {
            "success": False,
            "message": "Order not found."
        }

    eligibility = check_refund_eligibility(order)

    if not eligibility["eligible"]:
        return {
            "success": False,
            "message": eligibility["reason"]
        }

    refund_amount = calculate_refund_amount(order)

    refund_result = create_refund(
        order_id,
        refund_amount
    )

    return refund_result


# ============================================
# DEMO
# ============================================

def main():
    print("\n--- ORDER TRACKING SKILL ---")
    result = track_order("1001")
    print(result)

    print("\n--- ORDER CANCELLATION SKILL ---")
    result = cancel_order("1002")
    print(result)

    print("\n--- REFUND PROCESSING SKILL ---")
    result = process_refund("1003")
    print(result)

if __name__ == "__main__":
    main()