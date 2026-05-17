def save_health_metric(
    supabase,
    field,
    value
):

    data = {
        field: value
    }

    return (
        supabase
        .table("health_metrics")
        .insert(data)
        .execute()
    )


def get_latest_health_metrics(
    supabase
):

    response = (
        supabase
        .table("health_metrics")
        .select("*")
        .order(
            "created_at",
            desc=True
        )
        .limit(1)
        .execute()
    )

    if response.data:

        return response.data[0]

    return None
