select
    p.product_id,
    coalesce(t.product_category_name_english, p.product_category_name) as category_name,
    p.product_weight_g as weight_g,
    p.product_length_cm as length_cm,
    p.product_height_cm as height_cm,
    p.product_width_cm as width_cm
from {{ source('raw', 'products') }} p
left join {{ source('raw', 'category_translation') }} t
    on p.product_category_name = t.product_category_name
