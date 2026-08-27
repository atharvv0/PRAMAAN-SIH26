import type { AgentState } from '@/types/agent'
import type { AuditEvent } from '@/types/audit'
import type { Deliverable } from '@/types/deliverable'
import type { EvidenceRecord } from '@/types/evidence'
import type { ModelAdapter } from '@/types/model'
import type { DashboardOverview } from '@/types/overview'
import type { PolicyDecision } from '@/types/policy'
import type { NetworkEvent, SovereigntyStatus } from '@/types/sovereignty'
import type { TaskDefinition } from '@/types/task'
import type { Workspace } from '@/types/workspace'

/** Fixed demo timestamps around 2026-08-27T14:30:00+05:30 (IST). */
function at(h: number, m: number, s: number): string {
  const hh = String(h).padStart(2, '0')
  const mm = String(m).padStart(2, '0')
  const ss = String(s).padStart(2, '0')
  return `2026-08-27T${hh}:${mm}:${ss}+05:30`
}

export const DEMO_WORKSPACE_ID = 'ws-mrpl-inspection'
export const DEMO_TASK_ID = 'task-insp-pkg-review'
export const DEMO_RUN_ID = 'run-insp-20260827-001'

export const workspaces: Workspace[] = [
  {
    id: DEMO_WORKSPACE_ID,
    name: 'MRPL Inspection Review',
    description:
      'Confidential turnaround inspection package for Mangalore Refinery CDU/VDU units — local-only document intelligence, P&ID cross-check, and approval-gated deliverables.',
    documentCount: 48,
    activeTasks: 1,
    pendingApprovals: 1,
    deliverableCount: 3,
    updatedAt: at(14, 42, 18),
  },
  {
    id: 'ws-hsse-compliance',
    name: 'HSSE Compliance Archive',
    description:
      'Plant HSSE procedures, incident close-outs, and permit-to-work evidence retained under sovereignty controls.',
    documentCount: 126,
    activeTasks: 0,
    pendingApprovals: 0,
    deliverableCount: 8,
    updatedAt: at(11, 5, 0),
  },
  {
    id: 'ws-maintenance-planning',
    name: 'Turnaround Maintenance Planning',
    description:
      'Mechanical work packs, material take-offs, and critical-path schedules for planned shutdown windows.',
    documentCount: 72,
    activeTasks: 0,
    pendingApprovals: 1,
    deliverableCount: 5,
    updatedAt: at(9, 40, 12),
  },
]

export const models: ModelAdapter[] = [
  {
    id: 'model-local-vision',
    name: 'Local Vision Encoder',
    version: '2.4.1',
    runtime: 'local',
    capabilities: ['ocr', 'diagram_parse', 'region_grounding', 'handwriting'],
    status: 'healthy',
    vramGb: 12,
    description:
      'On-prem vision adapter for scanned inspection sheets, stamped drawings, and P&ID symbol grounding. No egress.',
    active: true,
  },
  {
    id: 'model-local-reasoner',
    name: 'Local Reasoning Engine',
    version: '1.9.0',
    runtime: 'local',
    capabilities: ['planning', 'sop_alignment', 'claim_validation', 'approval_draft'],
    status: 'healthy',
    vramGb: 24,
    description:
      'Air-gapped reasoning model for inspection claim synthesis, SOP clause matching, and approval note drafting.',
    active: true,
  },
  {
    id: 'model-spreadsheet-engine',
    name: 'Deterministic Spreadsheet Engine',
    version: '3.1.0',
    runtime: 'deterministic',
    capabilities: ['xlsx_eval', 'unit_conversion', 'tolerance_check', 'calc_trace'],
    status: 'healthy',
    description:
      'Deterministic workbook evaluator for thickness readings, corrosion allowances, and measurement reconciliations.',
    active: true,
  },
  {
    id: 'model-embedding-local',
    name: 'Local Document Embedder',
    version: '0.8.3',
    runtime: 'local',
    capabilities: ['retrieval', 'semantic_index', 'chunk_rank'],
    status: 'healthy',
    vramGb: 4,
    description:
      'Local embedding index over SOP libraries and prior inspection packages for grounded retrieval.',
    active: true,
  },
  {
    id: 'model-legacy-ocr',
    name: 'Legacy OCR Fallback',
    version: '1.2.0',
    runtime: 'local',
    capabilities: ['ocr'],
    status: 'inactive',
    vramGb: 2,
    description: 'Standby OCR path retained for degraded-mode failover; not scheduled for active runs.',
    active: false,
  },
]

export const inspectionTask: TaskDefinition = {
  id: DEMO_TASK_ID,
  title: 'Inspection Package Review',
  instruction:
    'Review the confidential MRPL turnaround inspection package for CDU-101. Extract findings from the scanned inspection report, cross-reference annotated P&ID regions against SOP-MRPL-INSP-042, reconcile thickness / corrosion readings in the measurement workbook, and draft an Approval Note for the Inspection Authority. All processing must remain on-prem; deny external model or network calls.',
  workspaceId: DEMO_WORKSPACE_ID,
  workspaceName: 'MRPL Inspection Review',
  status: 'approval_required',
  progress: 92,
  currentStep: 'APPROVAL REQUIRED',
  model: 'Local Reasoning Engine',
  createdBy: 'insp.officer@mrpl.local',
  createdAt: at(14, 30, 0),
  updatedAt: at(14, 42, 18),
  elapsedMs: 738_000,
  runId: DEMO_RUN_ID,
  files: [
    {
      id: 'file-insp-scan',
      name: 'CDU101_Inspection_Report_Scan.pdf',
      type: 'pdf',
      sizeBytes: 4_820_441,
      status: 'completed',
      localProcessing: true,
    },
    {
      id: 'file-pid-anno',
      name: 'P&ID_CDU101_Annotated.png',
      type: 'image',
      sizeBytes: 2_140_880,
      status: 'completed',
      localProcessing: true,
    },
    {
      id: 'file-thickness-xlsx',
      name: 'Thickness_Corrosion_Readings.xlsx',
      type: 'spreadsheet',
      sizeBytes: 186_432,
      status: 'completed',
      localProcessing: true,
    },
    {
      id: 'file-sop',
      name: 'SOP-MRPL-INSP-042_Visual_Inspection.docx',
      type: 'document',
      sizeBytes: 412_096,
      status: 'completed',
      localProcessing: true,
    },
  ],
}

export const tasks: TaskDefinition[] = [inspectionTask]

const policyBlockExternal: PolicyDecision = {
  id: 'pol-dec-egress-001',
  decision: 'denied',
  reason:
    'Egress deny-by-default: outbound HTTPS to api.external-llm.example blocked for sovereign workspace MRPL Inspection Review.',
  policyId: 'pol-egress-deny-default',
  policyName: 'Sovereign Egress Deny-by-Default',
  timestamp: at(14, 33, 42),
  resource: 'https://api.external-llm.example/v1/chat',
  actor: 'agent.run',
}

const policyRequireApproval: PolicyDecision = {
  id: 'pol-dec-approval-001',
  decision: 'require_approval',
  reason:
    'Deliverable Approval_Note.docx requires Inspection Authority sign-off before release from sovereign workspace.',
  policyId: 'pol-human-gate-deliverable',
  policyName: 'Human Approval Gate — Inspection Deliverables',
  timestamp: at(14, 41, 55),
  resource: 'deliv-approval-note',
  actor: 'agent.run',
}

export const agentRun: AgentState = {
  id: DEMO_RUN_ID,
  taskId: DEMO_TASK_ID,
  status: 'approval_required',
  currentStepId: 'step-approval',
  progress: 92,
  startedAt: at(14, 30, 5),
  updatedAt: at(14, 42, 18),
  plan: [
    {
      id: 'step-created',
      label: 'TASK CREATED',
      status: 'completed',
      startedAt: at(14, 30, 5),
      completedAt: at(14, 30, 6),
      durationMs: 820,
      details: 'Inspection Package Review queued under MRPL Inspection Review workspace.',
    },
    {
      id: 'step-planning',
      label: 'PLANNING',
      status: 'completed',
      startedAt: at(14, 30, 7),
      completedAt: at(14, 30, 28),
      durationMs: 21_400,
      modelId: 'model-local-reasoner',
      details:
        'Decomposed package into OCR, P&ID grounding, SOP retrieval, spreadsheet reconciliation, and approval drafting.',
    },
    {
      id: 'step-model-routed',
      label: 'MODEL ROUTED',
      status: 'completed',
      startedAt: at(14, 30, 29),
      completedAt: at(14, 30, 41),
      durationMs: 11_200,
      details: 'Local vision, reasoning, and deterministic spreadsheet adapters selected; cloud paths excluded.',
    },
    {
      id: 'step-ocr',
      label: 'DOCUMENT OCR',
      status: 'completed',
      startedAt: at(14, 30, 42),
      completedAt: at(14, 33, 10),
      durationMs: 148_000,
      toolId: 'tool-local-ocr',
      modelId: 'model-local-vision',
      evidenceCount: 2,
      details: 'Scanned CDU-101 inspection report OCR completed on-prem with region bounding boxes.',
    },
    {
      id: 'step-pid',
      label: 'P&ID ANALYSIS',
      status: 'completed',
      startedAt: at(14, 33, 12),
      completedAt: at(14, 35, 40),
      durationMs: 148_500,
      toolId: 'tool-pid-grounder',
      modelId: 'model-local-vision',
      evidenceCount: 2,
      details: 'Annotated nozzles N-12 / N-18 and corrosion coupon locations grounded on P&ID sheet.',
    },
    {
      id: 'step-sop',
      label: 'SOP RETRIEVAL',
      status: 'completed',
      startedAt: at(14, 35, 42),
      completedAt: at(14, 37, 5),
      durationMs: 83_000,
      toolId: 'tool-sop-retriever',
      modelId: 'model-embedding-local',
      evidenceCount: 1,
      details: 'Retrieved SOP-MRPL-INSP-042 clauses 4.2–4.6 for visual inspection acceptance criteria.',
    },
    {
      id: 'step-spreadsheet',
      label: 'SPREADSHEET COMPUTATION',
      status: 'completed',
      startedAt: at(14, 37, 8),
      completedAt: at(14, 38, 55),
      durationMs: 107_200,
      toolId: 'tool-xlsx-eval',
      modelId: 'model-spreadsheet-engine',
      evidenceCount: 1,
      details: 'Thickness readings reconciled against minimum allowable wall; two points flagged within alert band.',
    },
    {
      id: 'step-validation',
      label: 'VALIDATION',
      status: 'completed',
      startedAt: at(14, 38, 58),
      completedAt: at(14, 40, 50),
      durationMs: 112_000,
      modelId: 'model-local-reasoner',
      evidenceCount: 5,
      warning: 'Point T-44 within 8% of minimum allowable thickness — elevated for authority review.',
      details: 'Cross-validated OCR claims, P&ID tags, SOP clauses, and workbook tolerances.',
    },
    {
      id: 'step-approval',
      label: 'APPROVAL REQUIRED',
      status: 'approval_required',
      startedAt: at(14, 41, 0),
      modelId: 'model-local-reasoner',
      details: 'Approval_Note.docx staged; awaiting Inspection Authority decision under human-gate policy.',
    },
    {
      id: 'step-deliverable',
      label: 'DELIVERABLE GENERATED',
      status: 'completed',
      startedAt: at(14, 40, 52),
      completedAt: at(14, 41, 48),
      durationMs: 56_000,
      details: 'Evidence pack, calculation sheet, and Approval Note artefacts generated locally.',
    },
    {
      id: 'step-audit',
      label: 'AUDIT COMPLETE',
      status: 'completed',
      startedAt: at(14, 41, 50),
      completedAt: at(14, 42, 18),
      durationMs: 28_000,
      details: 'Full provenance chain sealed to local audit ledger; egress blocks recorded.',
    },
  ],
  modelRoutings: [
    {
      stepId: 'step-ocr',
      taskLabel: 'DOCUMENT OCR',
      modelId: 'model-local-vision',
      modelName: 'Local Vision Encoder',
      reason: 'Qwen-VL-class local vision required for scanned PDF OCR and stamp/region grounding.',
      local: true,
      status: 'completed',
    },
    {
      stepId: 'step-pid',
      taskLabel: 'P&ID ANALYSIS',
      modelId: 'model-local-vision',
      modelName: 'Local Vision Encoder',
      reason: 'Diagram symbol and annotation grounding on P&ID_CDU101_Annotated.png.',
      local: true,
      status: 'completed',
    },
    {
      stepId: 'step-planning',
      taskLabel: 'PLANNING / VALIDATION',
      modelId: 'model-local-reasoner',
      modelName: 'Local Reasoning Engine',
      reason: 'Local reasoning for plan synthesis, SOP alignment, and approval note drafting.',
      local: true,
      status: 'completed',
    },
    {
      stepId: 'step-spreadsheet',
      taskLabel: 'SPREADSHEET COMPUTATION',
      modelId: 'model-spreadsheet-engine',
      modelName: 'Deterministic Spreadsheet Engine',
      reason: 'Deterministic workbook evaluation for thickness / corrosion tolerance checks.',
      local: true,
      status: 'completed',
    },
  ],
  toolInvocations: [
    {
      id: 'inv-ocr-01',
      tool: 'LOCAL_OCR',
      status: 'completed',
      permission: 'allowed',
      reason: 'On-prem OCR permitted for workspace-scoped PDF.',
      timestamp: at(14, 30, 45),
      durationMs: 142_000,
      inputSummary: 'CDU101_Inspection_Report_Scan.pdf · pages 1–14',
      outputSummary: '1,842 text regions · 96.1% mean OCR confidence',
    },
    {
      id: 'inv-pid-01',
      tool: 'PID_GROUNDER',
      status: 'completed',
      permission: 'allowed',
      reason: 'Local vision diagram parse allowed.',
      timestamp: at(14, 33, 15),
      durationMs: 145_000,
      inputSummary: 'P&ID_CDU101_Annotated.png',
      outputSummary: '12 tagged equipment nodes · 4 highlighted inspection loci',
    },
    {
      id: 'inv-net-blocked',
      tool: 'NETWORK_REQUEST',
      status: 'external_blocked',
      permission: 'blocked',
      reason:
        'Sovereign egress deny-by-default blocked outbound call during model fallback probe.',
      timestamp: at(14, 33, 42),
      durationMs: 18,
      inputSummary: 'POST https://api.external-llm.example/v1/chat',
      outputSummary: 'DENIED — no bytes egressed; policy pol-egress-deny-default',
    },
    {
      id: 'inv-sop-01',
      tool: 'SOP_RETRIEVER',
      status: 'completed',
      permission: 'allowed',
      reason: 'Local embedding retrieval over SOP library.',
      timestamp: at(14, 35, 45),
      durationMs: 78_000,
      inputSummary: 'query: visual inspection acceptance CDU vessel nozzles',
      outputSummary: 'SOP-MRPL-INSP-042 §4.2–4.6 · top-3 chunks',
    },
    {
      id: 'inv-xlsx-01',
      tool: 'XLSX_EVAL',
      status: 'completed',
      permission: 'allowed',
      reason: 'Deterministic spreadsheet engine permitted.',
      timestamp: at(14, 37, 10),
      durationMs: 104_000,
      inputSummary: 'Thickness_Corrosion_Readings.xlsx · sheets Readings, Limits',
      outputSummary: '48 points evaluated · 2 alert-band · 0 below MAWT',
    },
  ],
}

export const evidenceRecords: EvidenceRecord[] = [
  {
    id: 'ev-001',
    taskId: DEMO_TASK_ID,
    runId: DEMO_RUN_ID,
    claim:
      'External visual inspection of vessel V-101 shell noted light surface scaling at south quadrant; no through-wall indication observed.',
    sourceDocument: 'CDU101_Inspection_Report_Scan.pdf',
    page: 3,
    region: { x: 0.12, y: 0.28, w: 0.76, h: 0.14 },
    extractedText:
      'V-101 shell S-quadrant: light scaling. UT follow-up recommended at TML-12. No crack-like indication under white-light exam.',
    confidence: 0.94,
    validationStatus: 'validated',
    modelId: 'model-local-vision',
    toolId: 'tool-local-ocr',
    createdAt: at(14, 32, 10),
  },
  {
    id: 'ev-002',
    taskId: DEMO_TASK_ID,
    runId: DEMO_RUN_ID,
    claim:
      'Nozzle N-12 reinforcement pad weld toe shows prior grind marks consistent with previous repair; current VT acceptable per SOP.',
    sourceDocument: 'CDU101_Inspection_Report_Scan.pdf',
    page: 5,
    region: { x: 0.18, y: 0.42, w: 0.64, h: 0.11 },
    extractedText:
      'N-12 RF pad WT: prior grind blend smooth. VT ACC per SOP-MRPL-INSP-042 §4.3. Dye-pen N/A this outage.',
    confidence: 0.91,
    validationStatus: 'validated',
    modelId: 'model-local-vision',
    toolId: 'tool-local-ocr',
    createdAt: at(14, 32, 48),
  },
  {
    id: 'ev-003',
    taskId: DEMO_TASK_ID,
    runId: DEMO_RUN_ID,
    claim:
      'P&ID annotation marks corrosion coupon CC-07 adjacent to line 8"-P-1014-A1A as priority UT location for this TAR.',
    sourceDocument: 'P&ID_CDU101_Annotated.png',
    page: 1,
    region: { x: 0.55, y: 0.31, w: 0.22, h: 0.18 },
    extractedText: 'CC-07 · 8"-P-1014-A1A · UT PRIORITY (red markup)',
    confidence: 0.89,
    validationStatus: 'validated',
    modelId: 'model-local-vision',
    toolId: 'tool-pid-grounder',
    createdAt: at(14, 34, 55),
  },
  {
    id: 'ev-004',
    taskId: DEMO_TASK_ID,
    runId: DEMO_RUN_ID,
    claim:
      'SOP-MRPL-INSP-042 §4.5 requires Independent Inspection Authority review when remaining life projection is below next planned TAR interval.',
    sourceDocument: 'SOP-MRPL-INSP-042_Visual_Inspection.docx',
    page: 7,
    region: { x: 0.1, y: 0.52, w: 0.8, h: 0.16 },
    extractedText:
      '4.5 Where calculated remaining life is less than the interval to the next scheduled turnaround, the package shall not be closed without Inspection Authority approval.',
    confidence: 0.97,
    validationStatus: 'validated',
    modelId: 'model-embedding-local',
    toolId: 'tool-sop-retriever',
    createdAt: at(14, 36, 40),
  },
  {
    id: 'ev-005',
    taskId: DEMO_TASK_ID,
    runId: DEMO_RUN_ID,
    claim:
      'Thickness point T-44 on V-101 shell reads 7.2 mm against MAWT 6.5 mm (alert band < 8.0 mm); remaining life projection flags for authority review.',
    sourceDocument: 'Thickness_Corrosion_Readings.xlsx',
    page: 1,
    region: { x: 0.08, y: 0.61, w: 0.84, h: 0.08 },
    extractedText: 'T-44 | V-101 shell | 7.2 mm | MAWT 6.5 | Alert | RL < next TAR',
    confidence: 0.99,
    validationStatus: 'pending',
    modelId: 'model-spreadsheet-engine',
    toolId: 'tool-xlsx-eval',
    createdAt: at(14, 38, 40),
  },
  {
    id: 'ev-006',
    taskId: DEMO_TASK_ID,
    runId: DEMO_RUN_ID,
    claim:
      'Nozzle N-18 VT disposition recorded as ACC with photographic evidence referenced on report page 9.',
    sourceDocument: 'CDU101_Inspection_Report_Scan.pdf',
    page: 9,
    region: { x: 0.2, y: 0.2, w: 0.55, h: 0.35 },
    extractedText: 'N-18 flange face VT: ACC. Photo ref IMG-4412 attached.',
    confidence: 0.88,
    validationStatus: 'validated',
    modelId: 'model-local-vision',
    toolId: 'tool-local-ocr',
    createdAt: at(14, 33, 2),
  },
]

export const deliverables: Deliverable[] = [
  {
    id: 'deliv-approval-note',
    name: 'Approval_Note.docx',
    type: 'docx',
    taskId: DEMO_TASK_ID,
    taskTitle: 'Inspection Package Review',
    createdAt: at(14, 41, 40),
    status: 'approval_required',
    approvalStatus: 'pending',
    evidenceCount: 6,
    provenanceSummary:
      'Drafted from local OCR + P&ID + SOP-MRPL-INSP-042 + spreadsheet reconciliation. Human gate required before release.',
    downloadUrl: '/demo/deliverables/Approval_Note.docx',
  },
  {
    id: 'deliv-evidence-pack',
    name: 'Evidence_Pack_CDU101.pdf',
    type: 'report',
    taskId: DEMO_TASK_ID,
    taskTitle: 'Inspection Package Review',
    createdAt: at(14, 41, 20),
    status: 'completed',
    approvalStatus: 'approved',
    evidenceCount: 6,
    provenanceSummary:
      'Compiled evidence ledger with page regions, confidence scores, and model/tool provenance for audit.',
    downloadUrl: '/demo/deliverables/Evidence_Pack_CDU101.pdf',
  },
  {
    id: 'deliv-calc-sheet',
    name: 'Thickness_Reconciliation.xlsx',
    type: 'calculation',
    taskId: DEMO_TASK_ID,
    taskTitle: 'Inspection Package Review',
    createdAt: at(14, 39, 10),
    status: 'completed',
    approvalStatus: 'approved',
    evidenceCount: 1,
    provenanceSummary:
      'Deterministic spreadsheet engine output with calc-trace for T-44 alert-band evaluation.',
    downloadUrl: '/demo/deliverables/Thickness_Reconciliation.xlsx',
  },
]

export const auditEvents: AuditEvent[] = [
  {
    id: 'aud-001',
    timestamp: at(14, 30, 6),
    actor: 'insp.officer@mrpl.local',
    taskId: DEMO_TASK_ID,
    action: 'task.created',
    eventType: 'task_lifecycle',
    result: 'Inspection Package Review created in MRPL Inspection Review',
    status: 'success',
  },
  {
    id: 'aud-002',
    timestamp: at(14, 30, 41),
    actor: 'agent.run',
    taskId: DEMO_TASK_ID,
    modelId: 'model-local-reasoner',
    action: 'model.routed',
    eventType: 'model_routing',
    result: 'Local-only adapters selected for vision, reasoning, and spreadsheet paths',
    status: 'sovereign',
    details: 'Cloud model candidates excluded by workspace sovereignty profile.',
  },
  {
    id: 'aud-003',
    timestamp: at(14, 33, 42),
    actor: 'agent.run',
    taskId: DEMO_TASK_ID,
    toolId: 'NETWORK_REQUEST',
    action: 'network.outbound_blocked',
    eventType: 'sovereignty',
    policyDecision: policyBlockExternal,
    result: 'Outbound request to api.external-llm.example denied; zero egress',
    status: 'external_blocked',
    details: 'Fallback probe during OCR confidence dip — blocked by deny-by-default egress.',
  },
  {
    id: 'aud-004',
    timestamp: at(14, 36, 40),
    actor: 'agent.run',
    taskId: DEMO_TASK_ID,
    modelId: 'model-embedding-local',
    toolId: 'SOP_RETRIEVER',
    action: 'evidence.captured',
    eventType: 'evidence',
    evidenceIds: ['ev-004'],
    result: 'SOP clause 4.5 captured as evidence for remaining-life gate',
    status: 'success',
  },
  {
    id: 'aud-005',
    timestamp: at(14, 38, 40),
    actor: 'agent.run',
    taskId: DEMO_TASK_ID,
    modelId: 'model-spreadsheet-engine',
    toolId: 'XLSX_EVAL',
    action: 'evidence.captured',
    eventType: 'evidence',
    evidenceIds: ['ev-005'],
    result: 'T-44 alert-band thickness finding recorded pending authority review',
    status: 'warning',
  },
  {
    id: 'aud-006',
    timestamp: at(14, 41, 55),
    actor: 'agent.run',
    taskId: DEMO_TASK_ID,
    action: 'approval.requested',
    eventType: 'approval',
    policyDecision: policyRequireApproval,
    evidenceIds: ['ev-001', 'ev-002', 'ev-003', 'ev-004', 'ev-005', 'ev-006'],
    result: 'Approval_Note.docx pending Inspection Authority decision',
    status: 'approval_required',
  },
  {
    id: 'aud-007',
    timestamp: at(14, 42, 18),
    actor: 'system.audit',
    taskId: DEMO_TASK_ID,
    action: 'audit.sealed',
    eventType: 'audit',
    result: 'Run provenance sealed to local audit ledger',
    status: 'completed',
    details: `Run ${DEMO_RUN_ID} hash-chained; 7 events committed.`,
  },
]

export const networkEvents: NetworkEvent[] = [
  {
    id: 'net-001',
    timestamp: at(14, 33, 42),
    kind: 'outbound_attempt',
    message: 'Agent attempted outbound HTTPS to external LLM endpoint during OCR fallback probe.',
    destination: 'https://api.external-llm.example/v1/chat',
  },
  {
    id: 'net-002',
    timestamp: at(14, 33, 42),
    kind: 'policy_decision',
    message: 'Egress policy denied outbound request — sovereign deny-by-default.',
    decision: 'blocked',
    reason: 'pol-egress-deny-default · workspace MRPL Inspection Review',
    destination: 'https://api.external-llm.example/v1/chat',
  },
  {
    id: 'net-003',
    timestamp: at(14, 33, 43),
    kind: 'audit_recorded',
    message: 'Blocked egress event written to local audit ledger (aud-003).',
    decision: 'blocked',
    reason: 'Zero bytes egressed; session continued on local vision adapter.',
  },
  {
    id: 'net-004',
    timestamp: at(14, 30, 10),
    kind: 'policy_decision',
    message: 'Local model registry access permitted within air-gapped fabric.',
    decision: 'allowed',
    reason: 'Intra-sovereign model bus · no external hop',
    destination: 'local://model-bus/registry',
  },
]

export const sovereignty: SovereigntyStatus = {
  mode: 'active',
  egressPolicy: 'deny_by_default',
  externalAllowed: 0,
  externalBlocked: 1,
  localProcessingPercent: 100,
  auditRecording: true,
  healthyModels: 4,
  totalModels: 5,
}

/** Mutable store used by the mock adapter and overview builder. */
export const store = {
  workspaces,
  tasks: tasks as TaskDefinition[],
  runs: [agentRun] as AgentState[],
  evidence: evidenceRecords as EvidenceRecord[],
  deliverables: deliverables as Deliverable[],
  auditEvents: auditEvents as AuditEvent[],
  models,
  networkEvents: networkEvents as NetworkEvent[],
  sovereignty: sovereignty as SovereigntyStatus,
}

export function buildOverview(): DashboardOverview {
  return {
    sovereignty: { ...store.sovereignty },
    activeTasks: store.tasks.filter(
      (t) =>
        t.status === 'running' ||
        t.status === 'approval_required' ||
        t.status === 'pending' ||
        t.status === 'queued',
    ).length,
    pendingApprovals: store.deliverables.filter((d) => d.approvalStatus === 'pending')
      .length,
    recentDeliverables: store.deliverables.length,
    recentSecurityEvents: store.networkEvents.filter((e) => e.decision === 'blocked')
      .length,
    activity: store.auditEvents
      .slice()
      .sort((a, b) => b.timestamp.localeCompare(a.timestamp)),
    currentTasks: store.tasks.map((t) => ({
      ...t,
      files: t.files.map((f) => ({ ...f })),
    })),
    networkEvents: store.networkEvents
      .slice()
      .sort((a, b) => b.timestamp.localeCompare(a.timestamp)),
  }
}
