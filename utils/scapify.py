def int_to_gp(num):
    if num >= 10 ** 9:  # Billions
        return f"{num / 10 ** 9:.2f}B"
    elif num >= 10 ** 6:  # Millions
        return f"{num / 10 ** 6:.2f}M"
    elif num >= 10 ** 3:  # Thousands
        return f"{num / 10 ** 3:.2f}K"
    else:
        return str(num + " gp")