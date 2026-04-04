def calculate_estimate(proposals: dict, rate_table: dict) -> list[dict]:
    estimates = []

    rate = {k: v["price"] for k, v in rate_table.items()}

    for proposal in proposals["proposals"]:
        cf = proposal["cost_factors"]
        items = []

        if "撮影費" in rate:
            items.append({
                "item": "撮影費",
                "unit_price": rate["撮影費"],
                "quantity": cf["shooting_days"],
                "unit": "日",
                "subtotal": rate["撮影費"] * cf["shooting_days"],
            })

        if "編集費" in rate:
            items.append({
                "item": "編集費",
                "unit_price": rate["編集費"],
                "quantity": cf["post_production_days"],
                "unit": "日",
                "subtotal": rate["編集費"] * cf["post_production_days"],
            })

        if "ディレクション費" in rate:
            direction_days = cf["shooting_days"] + cf["post_production_days"]
            items.append({
                "item": "ディレクション費",
                "unit_price": rate["ディレクション費"],
                "quantity": direction_days,
                "unit": "日",
                "subtotal": rate["ディレクション費"] * direction_days,
            })

        if "出演者費" in rate and cf.get("talent_count", 0) > 0:
            items.append({
                "item": "出演者費",
                "unit_price": rate["出演者費"],
                "quantity": cf["talent_count"] * cf["shooting_days"],
                "unit": "人日",
                "subtotal": rate["出演者費"] * cf["talent_count"] * cf["shooting_days"],
            })

        if "ロケハン費" in rate and cf.get("locations", 0) > 0:
            items.append({
                "item": "ロケハン費",
                "unit_price": rate["ロケハン費"],
                "quantity": cf["locations"],
                "unit": "箇所",
                "subtotal": rate["ロケハン費"] * cf["locations"],
            })

        if "ナレーション" in rate and cf.get("needs_narration"):
            items.append({
                "item": "ナレーション",
                "unit_price": rate["ナレーション"],
                "quantity": 1,
                "unit": "本",
                "subtotal": rate["ナレーション"],
            })

        if "BGM/SE" in rate and cf.get("needs_bgm"):
            items.append({
                "item": "BGM/SE",
                "unit_price": rate["BGM/SE"],
                "quantity": 1,
                "unit": "本",
                "subtotal": rate["BGM/SE"],
            })

        total = sum(item["subtotal"] for item in items)

        estimates.append({
            "title": proposal["title"],
            "items": items,
            "total": total,
        })

    return estimates
