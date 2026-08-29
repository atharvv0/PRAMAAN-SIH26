-- PRAMAAN internal runtime persistence extension.
-- The supplied pramaan/schema.sql contains the core 16 domain tables.
-- This table durably stores the serialized AgentState/run checkpoint so the
-- FastAPI process can restart without losing the active run.
CREATE TABLE IF NOT EXISTS public.task_runs (
    run_id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    task_id uuid NOT NULL UNIQUE REFERENCES public.tasks(task_id) ON DELETE CASCADE,
    status varchar(30) NOT NULL DEFAULT 'queued',
    state_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    started_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);