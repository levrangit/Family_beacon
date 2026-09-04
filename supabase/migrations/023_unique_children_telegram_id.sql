-- A Telegram account may belong to at most one child record.
-- NULL remains allowed for children that have not been linked yet.
create unique index if not exists children_telegram_id_unique_idx
on public.children (telegram_id)
where telegram_id is not null;
