def format_response(symbol, results):
    response_text = f"رمز السهم: {symbol}\n\n"

    order = ["Yaqeen", "Filterna", "Chart Idea"]
    arabic_names = {
        "Yaqeen": "فلتر يقين",
        "Filterna": "فلترنا",
        "Chart Idea": "فلتر فكرة شارت"
    }

    for key in order:
        value = results.get(key, "غير محدث")
        if "✅" in value:
            percentage = results.get(f"{key}_purification", "")
            if percentage:
                response_text += f"{arabic_names[key]}:\nحلال، نسبة التطهير {percentage}\n\n"
            else:
                response_text += f"{arabic_names[key]}:\nحلال (نسبة التطهير غير متوفرة حالياً)\n\n"
        elif "❌" in value:
            response_text += f"{arabic_names[key]}:\nغير شرعي\n\n"
        else:
            response_text += f"{arabic_names[key]}:\nغير محدث\n\n"

    response_text += (
        "قنوات JALWE العامة:\n"
        "- الأسهم: https://t.me/JalweTrader\n"
        "- العقود: https://t.me/jalweoption\n"
        "- التعليمية: https://t.me/JalweVip\n"
    )

    return response_text
if __name__ == "__main__":
    main()
