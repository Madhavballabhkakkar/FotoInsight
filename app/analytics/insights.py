"""Short sentences written from the calculated numbers. Nothing here is typed in advance."""

from app.analytics.enquiry_analysis import analyse as analyse_enquiries
from app.analytics.ranges import previous_period
from app.analytics.revenue import analyse as analyse_revenue
from app.constants import REVENUE_DEFINITION
from app.utils import format_inr


def build(start, end, revenue, customers, enquiries, services, seasonal, locations):
    insights = []
    if not any([
        revenue.get("has_data"),
        customers.get("has_data"),
        enquiries.get("has_data"),
        services.get("has_data"),
        seasonal.get("has_data"),
        locations.get("has_data"),
    ]):
        return ["Not enough data in the selected dates to generate business insights."]

    if revenue.get("has_data"):
        insights.append(
            f"Collected revenue in this range is {format_inr(revenue['total_revenue'])}. "
            "Pending amounts and unpaid booking totals are not included."
        )
        growth = revenue.get("growth")
        if growth:
            direction = "increased" if growth["percent"] >= 0 else "decreased"
            insights.append(
                f"Revenue {direction} by {abs(growth['percent']):.1f}% in {growth['current_label']} "
                f"compared with {growth['previous_label']}."
            )
    else:
        insights.append("No collected payments fall in this range, so revenue is INR 0. Unpaid booking amounts are not counted.")

    if services.get("highest_revenue"):
        insights.append(f"{services['highest_revenue']} is the highest-revenue service in this range.")
    if services.get("most_popular"):
        insights.append(f"{services['most_popular']} received the most enquiries in this range.")
    if services.get("most_booked") and services.get("most_booked") != services.get("most_popular"):
        insights.append(f"{services['most_booked']} was booked most often in this range.")

    if locations.get("top_city") and locations.get("top_city_share") is not None:
        insights.append(
            f"{locations['top_city']} contributes {locations['top_city_share']:.1f}% of bookings in this range."
        )

    if enquiries.get("has_data") and enquiries.get("conversion_rate") is not None:
        previous_start, previous_end = previous_period(start, end)
        previous = analyse_enquiries(previous_start, previous_end)
        if previous.get("conversion_rate") is not None:
            now = enquiries["conversion_rate"]
            then = previous["conversion_rate"]
            if now < then:
                insights.append(
                    f"Enquiry conversion decreased from {then:.1f}% to {now:.1f}% compared with the previous period of the same length."
                )
            elif now > then:
                insights.append(
                    f"Enquiry conversion increased from {then:.1f}% to {now:.1f}% compared with the previous period of the same length."
                )
            else:
                insights.append(f"Enquiry conversion stayed at {now:.1f}% compared with the previous period.")
        else:
            insights.append(f"Enquiry conversion for worked leads in this range is {enquiries['conversion_rate']:.1f}%.")

    if seasonal.get("has_data"):
        labels = seasonal["by_month_name"]["labels"]
        values = seasonal["by_month_name"]["values"]
        if sum(values) > 0:
            peak = max(values)
            names = [label for label, value in zip(labels, values) if value == peak]
            if len(names) == 1:
                insights.append(f"{names[0]} has the highest booking demand in this range.")
            else:
                insights.append(f"{' and '.join(names)} share the highest booking demand in this range.")
        if seasonal.get("high_demand"):
            insights.append("Higher-demand months in this range: " + ", ".join(seasonal["high_demand"]) + ".")
        if seasonal.get("low_demand"):
            insights.append("Quieter months in this range: " + ", ".join(seasonal["low_demand"]) + ".")

    if customers.get("new_customers"):
        insights.append(f"{customers['new_customers']} customers registered during the selected dates.")

    previous_revenue = analyse_revenue(*previous_period(start, end))
    if revenue.get("total_revenue", 0) == 0 and previous_revenue.get("total_revenue", 0) == 0 and len(insights) <= 1:
        return ["Not enough data in the selected dates to generate business insights."]
    return insights[:8]


def definitions():
    return {
        "revenue": REVENUE_DEFINITION,
        "conversion": "See the enquiry section. New enquiries are counted in the total, but not in the conversion ratio.",
    }
