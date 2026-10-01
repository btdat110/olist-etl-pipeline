with payments_agg as (
    select
        order_id,
        sum(payment_value) as order_payment_value
    from {{ ref('stg_payments') }}
    group by order_id
)

select
    oi.order_id,
    oi.order_item_id,
    o.customer_id,
    oi.product_id,
    oi.seller_id,
    cast(o.order_purchase_ts as date) as order_date,
    o.order_status,
    oi.price,
    oi.freight_value,
    oi.price + oi.freight_value as item_total,
    p.order_payment_value
from {{ ref('stg_order_items') }} oi
join {{ ref('stg_orders') }} o on oi.order_id = o.order_id
left join payments_agg p on oi.order_id = p.order_id
