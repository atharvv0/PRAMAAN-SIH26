--
-- PostgreSQL database dump
--

\restrict DmPV10KfejlRezDjg31wMZd1y4bhhfWAKlqGQ3HWYs2R614gsZTfWQFSIhLEpe6

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

-- Started on 2026-08-26 11:49:38

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2 (class 3079 OID 16414)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 5271 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 237 (class 1259 OID 16888)
-- Name: approvals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approvals (
    approval_id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_id uuid NOT NULL,
    requested_from uuid NOT NULL,
    status character varying(30) DEFAULT 'pending'::character varying NOT NULL,
    decision character varying(30),
    decided_at timestamp with time zone,
    comment text
);


ALTER TABLE public.approvals OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16935)
-- Name: audit_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_events (
    audit_event_id uuid DEFAULT gen_random_uuid() NOT NULL,
    actor_type character varying(30) NOT NULL,
    actor_id uuid,
    action character varying(80) NOT NULL,
    target_type character varying(50) NOT NULL,
    target_id uuid,
    decision character varying(20) DEFAULT 'none'::character varying,
    reason text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_events OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 16911)
-- Name: deliverables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deliverables (
    deliverable_id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_id uuid NOT NULL,
    file_id uuid NOT NULL,
    format character varying(30) NOT NULL,
    version character varying(50) DEFAULT '1.0'::character varying NOT NULL,
    approval_state character varying(30) DEFAULT 'pending'::character varying NOT NULL
);


ALTER TABLE public.deliverables OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 16830)
-- Name: document_chunks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document_chunks (
    chunk_id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id uuid NOT NULL,
    chunk_index integer NOT NULL,
    page_no integer,
    region_json jsonb,
    text text NOT NULL,
    qdrant_point_id character varying(120) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.document_chunks OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 16780)
-- Name: documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.documents (
    document_id uuid DEFAULT gen_random_uuid() NOT NULL,
    knowledge_base_id uuid NOT NULL,
    file_id uuid NOT NULL,
    title character varying(250) NOT NULL,
    version character varying(50),
    source_type character varying(40) NOT NULL,
    status character varying(30) DEFAULT 'indexing'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.documents OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 16853)
-- Name: evidence_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.evidence_records (
    evidence_id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_id uuid NOT NULL,
    claim_text text NOT NULL,
    document_id uuid,
    chunk_id uuid,
    model_call_id uuid,
    confidence numeric(5,4),
    validation_status character varying(30) DEFAULT 'pending'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.evidence_records OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16599)
-- Name: files; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.files (
    file_id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    uploaded_by uuid NOT NULL,
    filename character varying(255) NOT NULL,
    mime_type character varying(100) NOT NULL,
    size_bytes bigint NOT NULL,
    storage_path text NOT NULL,
    sha256 character(64) NOT NULL,
    sensitivity_class character varying(30) DEFAULT 'confidential'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.files OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16760)
-- Name: knowledge_bases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.knowledge_bases (
    knowledge_base_id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid NOT NULL,
    name character varying(150) NOT NULL,
    description text,
    status character varying(30) DEFAULT 'active'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.knowledge_bases OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 16736)
-- Name: model_calls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.model_calls (
    model_call_id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_id uuid NOT NULL,
    model_version_id uuid NOT NULL,
    purpose character varying(50) NOT NULL,
    input_tokens integer,
    output_tokens integer,
    latency_ms integer,
    status character varying(30) DEFAULT 'success'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.model_calls OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16683)
-- Name: model_capabilities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.model_capabilities (
    model_version_id uuid NOT NULL,
    capability character varying(80) NOT NULL,
    score numeric(5,4),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.model_capabilities OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16661)
-- Name: model_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.model_versions (
    model_version_id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_id uuid NOT NULL,
    version character varying(80) NOT NULL,
    weights_path text NOT NULL,
    quantization character varying(50),
    vram_required_gb numeric(8,2),
    license character varying(120) NOT NULL,
    status character varying(30) DEFAULT 'active'::character varying NOT NULL
);


ALTER TABLE public.model_versions OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16648)
-- Name: models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.models (
    model_id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(150) NOT NULL,
    provider_family character varying(150),
    runtime character varying(30) NOT NULL,
    status character varying(30) DEFAULT 'active'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.models OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16525)
-- Name: projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projects (
    project_id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid NOT NULL,
    name character varying(150) NOT NULL,
    description text,
    status character varying(30) DEFAULT 'active'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.projects OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16629)
-- Name: task_files; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_files (
    task_id uuid NOT NULL,
    file_id uuid NOT NULL,
    role character varying(50) DEFAULT 'input'::character varying NOT NULL
);


ALTER TABLE public.task_files OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16578)
-- Name: task_steps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_steps (
    step_id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_id uuid NOT NULL,
    step_no integer NOT NULL,
    step_type character varying(40) NOT NULL,
    status character varying(30) DEFAULT 'pending'::character varying NOT NULL,
    input_ref jsonb,
    output_ref jsonb,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    error_message text
);


ALTER TABLE public.task_steps OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16547)
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    task_id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    created_by uuid NOT NULL,
    title character varying(200) NOT NULL,
    intent text NOT NULL,
    status character varying(30) DEFAULT 'queued'::character varying NOT NULL,
    sensitivity_class character varying(30) DEFAULT 'confidential'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16710)
-- Name: tool_calls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tool_calls (
    tool_call_id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_id uuid NOT NULL,
    tool_id uuid NOT NULL,
    agent_name character varying(80) NOT NULL,
    args_json jsonb,
    result_json jsonb,
    status character varying(30) DEFAULT 'started'::character varying NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    ended_at timestamp with time zone,
    error_message text
);


ALTER TABLE public.tool_calls OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 16697)
-- Name: tools; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tools (
    tool_id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(150) NOT NULL,
    tool_type character varying(80) NOT NULL,
    status character varying(30) DEFAULT 'active'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tools OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16452)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying(255) NOT NULL,
    display_name character varying(120) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16469)
-- Name: workspaces; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workspaces (
    workspace_id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(150) NOT NULL,
    description text,
    sensitivity_class character varying(30) DEFAULT 'confidential'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.workspaces OWNER TO postgres;

--
-- TOC entry 5068 (class 2606 OID 16900)
-- Name: approvals approvals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approvals
    ADD CONSTRAINT approvals_pkey PRIMARY KEY (approval_id);


--
-- TOC entry 5072 (class 2606 OID 16949)
-- Name: audit_events audit_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_pkey PRIMARY KEY (audit_event_id);


--
-- TOC entry 5070 (class 2606 OID 16924)
-- Name: deliverables deliverables_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliverables
    ADD CONSTRAINT deliverables_pkey PRIMARY KEY (deliverable_id);


--
-- TOC entry 5062 (class 2606 OID 16846)
-- Name: document_chunks document_chunks_document_id_chunk_index_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_chunks
    ADD CONSTRAINT document_chunks_document_id_chunk_index_key UNIQUE (document_id, chunk_index);


--
-- TOC entry 5064 (class 2606 OID 16844)
-- Name: document_chunks document_chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_chunks
    ADD CONSTRAINT document_chunks_pkey PRIMARY KEY (chunk_id);


--
-- TOC entry 5060 (class 2606 OID 16794)
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (document_id);


--
-- TOC entry 5066 (class 2606 OID 16867)
-- Name: evidence_records evidence_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_records
    ADD CONSTRAINT evidence_records_pkey PRIMARY KEY (evidence_id);


--
-- TOC entry 5040 (class 2606 OID 16618)
-- Name: files files_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (file_id);


--
-- TOC entry 5058 (class 2606 OID 16774)
-- Name: knowledge_bases knowledge_bases_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.knowledge_bases
    ADD CONSTRAINT knowledge_bases_pkey PRIMARY KEY (knowledge_base_id);


--
-- TOC entry 5056 (class 2606 OID 16749)
-- Name: model_calls model_calls_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_calls
    ADD CONSTRAINT model_calls_pkey PRIMARY KEY (model_call_id);


--
-- TOC entry 5050 (class 2606 OID 16691)
-- Name: model_capabilities model_capabilities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_capabilities
    ADD CONSTRAINT model_capabilities_pkey PRIMARY KEY (model_version_id, capability);


--
-- TOC entry 5046 (class 2606 OID 16677)
-- Name: model_versions model_versions_model_id_version_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT model_versions_model_id_version_key UNIQUE (model_id, version);


--
-- TOC entry 5048 (class 2606 OID 16675)
-- Name: model_versions model_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT model_versions_pkey PRIMARY KEY (model_version_id);


--
-- TOC entry 5044 (class 2606 OID 16660)
-- Name: models models_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.models
    ADD CONSTRAINT models_pkey PRIMARY KEY (model_id);


--
-- TOC entry 5032 (class 2606 OID 16541)
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (project_id);


--
-- TOC entry 5042 (class 2606 OID 16637)
-- Name: task_files task_files_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_files
    ADD CONSTRAINT task_files_pkey PRIMARY KEY (task_id, file_id);


--
-- TOC entry 5036 (class 2606 OID 16591)
-- Name: task_steps task_steps_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_steps
    ADD CONSTRAINT task_steps_pkey PRIMARY KEY (step_id);


--
-- TOC entry 5038 (class 2606 OID 16593)
-- Name: task_steps task_steps_task_id_step_no_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_steps
    ADD CONSTRAINT task_steps_task_id_step_no_key UNIQUE (task_id, step_no);


--
-- TOC entry 5034 (class 2606 OID 16567)
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (task_id);


--
-- TOC entry 5054 (class 2606 OID 16725)
-- Name: tool_calls tool_calls_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tool_calls
    ADD CONSTRAINT tool_calls_pkey PRIMARY KEY (tool_call_id);


--
-- TOC entry 5052 (class 2606 OID 16709)
-- Name: tools tools_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tools
    ADD CONSTRAINT tools_pkey PRIMARY KEY (tool_id);


--
-- TOC entry 5026 (class 2606 OID 16468)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 5028 (class 2606 OID 16466)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- TOC entry 5030 (class 2606 OID 16482)
-- Name: workspaces workspaces_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces
    ADD CONSTRAINT workspaces_pkey PRIMARY KEY (workspace_id);


--
-- TOC entry 5095 (class 2606 OID 16906)
-- Name: approvals approvals_requested_from_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approvals
    ADD CONSTRAINT approvals_requested_from_fkey FOREIGN KEY (requested_from) REFERENCES public.users(user_id);


--
-- TOC entry 5096 (class 2606 OID 16901)
-- Name: approvals approvals_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approvals
    ADD CONSTRAINT approvals_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(task_id) ON DELETE CASCADE;


--
-- TOC entry 5097 (class 2606 OID 16930)
-- Name: deliverables deliverables_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliverables
    ADD CONSTRAINT deliverables_file_id_fkey FOREIGN KEY (file_id) REFERENCES public.files(file_id);


--
-- TOC entry 5098 (class 2606 OID 16925)
-- Name: deliverables deliverables_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliverables
    ADD CONSTRAINT deliverables_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(task_id) ON DELETE CASCADE;


--
-- TOC entry 5090 (class 2606 OID 16847)
-- Name: document_chunks document_chunks_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_chunks
    ADD CONSTRAINT document_chunks_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(document_id) ON DELETE CASCADE;


--
-- TOC entry 5088 (class 2606 OID 16800)
-- Name: documents documents_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_file_id_fkey FOREIGN KEY (file_id) REFERENCES public.files(file_id);


--
-- TOC entry 5089 (class 2606 OID 16795)
-- Name: documents documents_knowledge_base_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_knowledge_base_id_fkey FOREIGN KEY (knowledge_base_id) REFERENCES public.knowledge_bases(knowledge_base_id) ON DELETE CASCADE;


--
-- TOC entry 5091 (class 2606 OID 16878)
-- Name: evidence_records evidence_records_chunk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_records
    ADD CONSTRAINT evidence_records_chunk_id_fkey FOREIGN KEY (chunk_id) REFERENCES public.document_chunks(chunk_id);


--
-- TOC entry 5092 (class 2606 OID 16873)
-- Name: evidence_records evidence_records_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_records
    ADD CONSTRAINT evidence_records_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(document_id);


--
-- TOC entry 5093 (class 2606 OID 16883)
-- Name: evidence_records evidence_records_model_call_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_records
    ADD CONSTRAINT evidence_records_model_call_id_fkey FOREIGN KEY (model_call_id) REFERENCES public.model_calls(model_call_id);


--
-- TOC entry 5094 (class 2606 OID 16868)
-- Name: evidence_records evidence_records_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_records
    ADD CONSTRAINT evidence_records_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(task_id) ON DELETE CASCADE;


--
-- TOC entry 5077 (class 2606 OID 16619)
-- Name: files files_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE CASCADE;


--
-- TOC entry 5078 (class 2606 OID 16624)
-- Name: files files_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(user_id);


--
-- TOC entry 5087 (class 2606 OID 16775)
-- Name: knowledge_bases knowledge_bases_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.knowledge_bases
    ADD CONSTRAINT knowledge_bases_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspaces(workspace_id) ON DELETE CASCADE;


--
-- TOC entry 5085 (class 2606 OID 16755)
-- Name: model_calls model_calls_model_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_calls
    ADD CONSTRAINT model_calls_model_version_id_fkey FOREIGN KEY (model_version_id) REFERENCES public.model_versions(model_version_id) ON DELETE CASCADE;


--
-- TOC entry 5086 (class 2606 OID 16750)
-- Name: model_calls model_calls_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_calls
    ADD CONSTRAINT model_calls_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(task_id) ON DELETE CASCADE;


--
-- TOC entry 5082 (class 2606 OID 16692)
-- Name: model_capabilities model_capabilities_model_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_capabilities
    ADD CONSTRAINT model_capabilities_model_version_id_fkey FOREIGN KEY (model_version_id) REFERENCES public.model_versions(model_version_id) ON DELETE CASCADE;


--
-- TOC entry 5081 (class 2606 OID 16678)
-- Name: model_versions model_versions_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT model_versions_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.models(model_id) ON DELETE CASCADE;


--
-- TOC entry 5073 (class 2606 OID 16542)
-- Name: projects projects_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspaces(workspace_id) ON DELETE CASCADE;


--
-- TOC entry 5079 (class 2606 OID 16643)
-- Name: task_files task_files_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_files
    ADD CONSTRAINT task_files_file_id_fkey FOREIGN KEY (file_id) REFERENCES public.files(file_id) ON DELETE CASCADE;


--
-- TOC entry 5080 (class 2606 OID 16638)
-- Name: task_files task_files_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_files
    ADD CONSTRAINT task_files_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(task_id) ON DELETE CASCADE;


--
-- TOC entry 5076 (class 2606 OID 16594)
-- Name: task_steps task_steps_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_steps
    ADD CONSTRAINT task_steps_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(task_id) ON DELETE CASCADE;


--
-- TOC entry 5074 (class 2606 OID 16573)
-- Name: tasks tasks_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- TOC entry 5075 (class 2606 OID 16568)
-- Name: tasks tasks_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE CASCADE;


--
-- TOC entry 5083 (class 2606 OID 16726)
-- Name: tool_calls tool_calls_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tool_calls
    ADD CONSTRAINT tool_calls_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(task_id) ON DELETE CASCADE;


--
-- TOC entry 5084 (class 2606 OID 16731)
-- Name: tool_calls tool_calls_tool_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tool_calls
    ADD CONSTRAINT tool_calls_tool_id_fkey FOREIGN KEY (tool_id) REFERENCES public.tools(tool_id) ON DELETE CASCADE;


-- Completed on 2026-08-26 11:49:38

--
-- PostgreSQL database dump complete
--

\unrestrict DmPV10KfejlRezDjg31wMZd1y4bhhfWAKlqGQ3HWYs2R614gsZTfWQFSIhLEpe6

