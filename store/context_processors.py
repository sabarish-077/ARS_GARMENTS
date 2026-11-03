def cart_summary(request):
    cart = request.session.get("cart", {})
    count = 0
    for item in cart.values():
        try: count += max(0, int(item.get("quantity", 0)))
        except (TypeError, ValueError, AttributeError): continue
    return {"cart_count": count}
