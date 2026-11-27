erDiagram
brand_info {
serial brand_id PK
varchar brand_name
varchar tagline
text description
varchar operating_hours
varchar contact_whatsapp
varchar instagram_handle
timestamptz updated_at
}

    locations {
        varchar location_id PK
        varchar location_name
        varchar area
        varchar zone_type
        decimal latitude
        decimal longitude
        varchar source_status
        text notes
    }

    carts {
        varchar cart_id PK
        varchar cart_name
        varchar unit_type
        varchar default_mode
        varchar staff_alias
        varchar home_location_id FK
        integer cup_capacity
        varchar source_status
        boolean is_authorized
        boolean is_active
        varchar current_location_id FK
        decimal current_latitude
        decimal current_longitude
        timestamptz last_updated_at
    }

    users {
        varchar user_id PK
        varchar full_name
        varchar username UK
        text password_hash
        varchar role
        varchar assigned_cart_id FK
        boolean is_account_active
        timestamptz created_at
    }

    menu {
        varchar menu_id PK
        varchar category
        varchar menu_name UK
        varchar unit_type
        integer price
        integer hpp_asumsi
        integer estimated_margin
        varchar image_filename
        text image_gdrive_url
        boolean is_available
        varchar price_source
        varchar hpp_source
    }

    shifts {
        varchar shift_id PK
        date shift_date
        varchar cart_id FK
        varchar staff_user_id FK
        varchar location_id FK
        varchar mode_operasi
        timestamp start_time
        timestamp end_time
        varchar weather
        integer cup_dibawa
        integer cup_sisa
        integer setoran_tunai_fisik
        integer mutasi_qris_aktual
        varchar status
    }

    transactions {
        varchar transaction_id PK
        varchar shift_id FK
        varchar staff_user_id FK
        timestamp transaction_timestamp
        varchar cart_id FK
        varchar location_id FK
        varchar menu_id FK
        varchar menu_name
        varchar category
        varchar unit_type
        integer qty
        integer unit_price
        integer total_price
        integer hpp_asumsi_total
        varchar payment_method
        varchar order_type
    }

    ai_chat_logs {
        serial chat_id PK
        varchar user_id FK
        varchar session_id
        text user_question
        varchar predicted_intent
        decimal intent_confidence
        boolean is_out_of_context
        text ai_response
        boolean fallback_used
        timestamptz created_at
    }

    locations ||--o{ carts : "home_location_id"
    locations ||--o{ carts : "current_location_id"
    locations ||--o{ shifts : "location_id"
    locations ||--o{ transactions : "location_id"
    carts ||--o{ users : "assigned_cart_id"
    carts ||--o{ shifts : "cart_id"
    carts ||--o{ transactions : "cart_id"
    users ||--o{ shifts : "staff_user_id"
    users ||--o{ transactions : "staff_user_id"
    users ||--o{ ai_chat_logs : "user_id"
    shifts ||--o{ transactions : "shift_id"
    menu ||--o{ transactions : "menu_id"
