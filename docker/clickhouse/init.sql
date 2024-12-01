CREATE TABLE IF NOT EXISTS event_log
(
    `event_type` String,
    `event_date_time` DateTime64(6),
    `environment` String,
    `event_context` String,
    `metadata_version` Int32 DEFAULT 1,
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date_time)
ORDER BY (event_date_time, event_type)
SETTINGS index_granularity = 8192;

CREATE TABLE IF NOT EXISTS event_log_buffer
(
    `event_type` String,
    `event_date_time` DateTime64(6),
    `environment` String,
    `event_context` String,
    `metadata_version` Int32 DEFAULT 1
)
ENGINE = Buffer(
    default,            -- База данных назначения
    event_log,          -- Таблица назначения
    16,                 -- Количество бакетов (по умолчанию 16)
    60,                 -- Минимальное время (секунды)
    3600,               -- Максимальное время (секунды) (например, 1 час)
    10000,              -- Минимальное количество строк
    1000000,            -- Максимальное количество строк
    10000000,           -- Минимальный размер в байтах (10 MB)
    100000000,          -- Максимальный размер в байтах (100 MB)
    60,                 -- Время ожидания для сброса в секундах (например, 60 секунд)
    1000,               -- Количество строк для сброса
    1000000             -- Максимальный размер данных для сброса (1 MB)
);

