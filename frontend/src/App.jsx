
import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  FileText,
  Upload,
  ShieldCheck,
  ClipboardCheck,
  History,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  RefreshCw,
  Search,
  Bell,
  Menu,
  X,
  GitCompareArrows,
  Play,
  Check,
  XCircle,
} from "lucide-react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const selectStyle = {
  display: "block",
  width: "100%",
  padding: "13px",
  marginTop: "10px",
  border: "1px solid #dce2ea",
  borderRadius: "8px",
  background: "#ffffff",
  fontSize: "14px",
  color: "#263247",
};

function App() {
  const [activePage, setActivePage] = useState("Dashboard");

  const [documents, setDocuments] = useState([]);
  const [approvals, setApprovals] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [verifications, setVerifications] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [comparing, setComparing] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [compareError, setCompareError] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const [actionError, setActionError] = useState("");

  const [search, setSearch] = useState("");
  const [mobileMenu, setMobileMenu] = useState(false);

  const [selectedPO, setSelectedPO] = useState("");
  const [selectedInvoice, setSelectedInvoice] = useState("");
  const [comparison, setComparison] = useState(null);
  const [processingId, setProcessingId] = useState("");

  const navigation = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Documents", icon: FileText },
    { name: "Comparison", icon: GitCompareArrows },
    { name: "Approvals", icon: ClipboardCheck },
    { name: "Audit Trail", icon: History },
  ];

  // LOAD ALL DASHBOARD DATA
  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const endpoints = [
        "/documents",
        "/approvals",
        "/executions",
        "/verifications",
        "/audit-logs",
      ];

      const responses = await Promise.all(
        endpoints.map((endpoint) => fetch(`${API}${endpoint}`))
      );

      if (responses.some((response) => !response.ok)) {
        throw new Error("Dashboard loading failed.");
      }

      const [
        docs,
        approvalData,
        executionData,
        verificationData,
        auditData,
      ] = await Promise.all(responses.map((response) => response.json()));

      setDocuments(docs.documents || []);
      setApprovals(approvalData.approvals || []);
      setExecutions(executionData.executions || []);
      setVerifications(verificationData.verifications || []);
      setAuditLogs(auditData.audit_logs || []);
    } catch (err) {
      setError(
        "Backend connection failed. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  // DOCUMENT UPLOAD
  async function handleUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    setMessage("");
    setError("");

    try {
      const response = await fetch(`${API}/upload`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Upload failed.");
      }

      setMessage(`${file.name} uploaded successfully.`);
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  // DOCUMENT COMPARISON
  async function handleCompare() {
    if (!selectedPO || !selectedInvoice) {
      setCompareError("Please select both documents.");
      return;
    }

    if (selectedPO === selectedInvoice) {
      setCompareError("Select two different documents.");
      return;
    }

    setComparing(true);
    setCompareError("");
    setComparison(null);

    try {
      const response = await fetch(`${API}/compare`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          po_document_id: selectedPO,
          invoice_document_id: selectedInvoice,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Comparison failed.");
      }

      setComparison(result);
      await loadDashboard();
    } catch (err) {
      setCompareError(err.message);
    } finally {
      setComparing(false);
    }
  }

  // APPROVE OR REJECT
  async function handleApprovalDecision(approvalId, decision) {
    setProcessingId(approvalId);
    setActionMessage("");
    setActionError("");

    try {
      const response = await fetch(
        `${API}/approvals/${approvalId}/review`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ decision }),
        }
      );

      const result = await response.json();

      if (!response.ok || result.status === "error") {
        throw new Error(result.message || "Approval review failed.");
      }

      setActionMessage(result.message);
      await loadDashboard();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setProcessingId("");
    }
  }

  // EXECUTE APPROVED ACTION
  async function handleExecute(approvalId) {
    setProcessingId(approvalId);
    setActionMessage("");
    setActionError("");

    try {
      const response = await fetch(`${API}/executions/${approvalId}`, {
        method: "POST",
      });

      const result = await response.json();

      if (!response.ok || result.execution_status !== "executed") {
        throw new Error(result.message || "Execution failed.");
      }

      setActionMessage(
        `Action executed. Execution ID: ${result.execution_id}`
      );

      await loadDashboard();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setProcessingId("");
    }
  }

  // VERIFY EXECUTION
  async function handleVerify(executionId) {
    setProcessingId(executionId);
    setActionMessage("");
    setActionError("");

    try {
      const response = await fetch(`${API}/verifications/${executionId}`, {
        method: "POST",
      });

      const result = await response.json();

      if (!response.ok || result.verification_status !== "verified") {
        throw new Error(result.message || "Verification failed.");
      }

      setActionMessage(result.message);
      await loadDashboard();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setProcessingId("");
    }
  }

  const pendingApprovals = approvals.filter(
    (item) => item.approval_status === "pending"
  ).length;

  const verifiedCount = verifications.filter(
    (item) => item.verification_status === "verified"
  ).length;

  const reviewedCount = approvals.filter(
    (item) => item.approval_status === "pending"
  ).length;

  const filteredDocuments = documents.filter((doc) =>
    `${doc.filename} ${doc.document_type} ${doc.document_id}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  // DASHBOARD
  function renderDashboard() {
    return (
      <>
        <div className="welcome-section">
          <div>
            <p className="eyebrow">OVERVIEW</p>
            <h2>Business Intelligence Dashboard</h2>
            <p className="welcome-text">
              Monitor documents, investigate discrepancies and manage approvals.
            </p>
          </div>

          <button className="refresh-button" onClick={loadDashboard}>
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>

        <div className="stats-grid">
          <StatCard
            icon={<FileText />}
            label="Total Documents"
            value={documents.length}
            color="blue"
          />

          <StatCard
            icon={<AlertTriangle />}
            label="Pending Reviews"
            value={reviewedCount}
            color="orange"
          />

          <StatCard
            icon={<Clock3 />}
            label="Pending Approvals"
            value={pendingApprovals}
            color="purple"
          />

          <StatCard
            icon={<ShieldCheck />}
            label="Verified Actions"
            value={verifiedCount}
            color="green"
          />
        </div>

        <div className="dashboard-grid">
          <section className="panel upload-panel">
            <div className="panel-heading">
              <div>
                <h3>Upload Business Document</h3>
                <p>Upload a Purchase Order, Invoice or supported PDF/XLSX file.</p>
              </div>
              <div className="heading-icon">
                <Upload size={20} />
              </div>
            </div>

            <label className="upload-area">
              <div className="upload-icon">
                <Upload size={25} />
              </div>

              <strong>
                {uploading ? "Uploading..." : "Choose a document"}
              </strong>

              <span>PDF or XLSX · Maximum 10 MB</span>

              <input
                type="file"
                accept=".pdf,.xlsx"
                onChange={handleUpload}
                disabled={uploading}
              />

              <span className="browse-button">
                {uploading ? "Please wait..." : "Browse files"}
              </span>
            </label>

            {message && <p className="success-message">{message}</p>}
            {error && <p className="error-message">{error}</p>}
          </section>

          <section className="panel activity-panel">
            <div className="panel-heading">
              <div>
                <h3>Workflow Summary</h3>
                <p>Current activity in your system</p>
              </div>
              <ShieldCheck className="summary-shield" size={23} />
            </div>

            <WorkflowItem
              label="Documents uploaded"
              value={documents.length}
              color="blue-dot"
            />

            <WorkflowItem
              label="Approval requests"
              value={approvals.length}
              color="purple-dot"
            />

            <WorkflowItem
              label="Actions executed"
              value={executions.length}
              color="orange-dot"
            />

            <WorkflowItem
              label="Actions verified"
              value={verifications.length}
              color="green-dot"
            />
          </section>
        </div>

        <section className="panel recent-panel">
          <div className="panel-heading">
            <div>
              <h3>Recent Documents</h3>
              <p>Your latest uploaded business documents</p>
            </div>

            <button
              className="text-button"
              onClick={() => setActivePage("Documents")}
            >
              View all
            </button>
          </div>

          <DocumentTable documents={documents.slice(0, 5)} />
        </section>
      </>
    );
  }

  // DOCUMENTS PAGE
  function renderDocuments() {
    return (
      <section className="panel page-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">DOCUMENT MANAGEMENT</p>
            <h2>All Documents</h2>
            <p>View business documents stored in ProofChain AI.</p>
          </div>

          <label className="browse-button upload-small">
            <Upload size={15} />
            Upload

            <input
              type="file"
              accept=".pdf,.xlsx"
              onChange={handleUpload}
              disabled={uploading}
            />
          </label>
        </div>

        <div className="search-box">
          <Search size={17} />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search documents..."
          />
        </div>

        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}

        <DocumentTable documents={filteredDocuments} />
      </section>
    );
  }

  // COMPARISON PAGE
  function renderComparison() {
    const purchaseOrders = documents.filter(
      (doc) =>
        doc.document_type === "Purchase Order" ||
        doc.extracted_data?.po_number
    );

    const invoices = documents.filter(
      (doc) =>
        doc.document_type === "Invoice" ||
        doc.extracted_data?.invoice_number
    );

    return (
      <section className="panel page-panel">
        <p className="eyebrow">DOCUMENT INTELLIGENCE</p>
        <h2>Document Comparison</h2>

        <p className="welcome-text">
          Compare Purchase Orders and Invoices to identify business discrepancies.
        </p>

        <div
          style={{
            display: "grid",
            gap: 20,
            maxWidth: 650,
            marginTop: 25,
          }}
        >
          <div>
            <label><strong>Purchase Order</strong></label>

            <select
              value={selectedPO}
              onChange={(event) => setSelectedPO(event.target.value)}
              style={selectStyle}
            >
              <option value="">Select Purchase Order</option>

              {purchaseOrders.map((doc) => (
                <option key={doc.document_id} value={doc.document_id}>
                  {doc.filename} — {doc.document_id}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label><strong>Invoice</strong></label>

            <select
              value={selectedInvoice}
              onChange={(event) => setSelectedInvoice(event.target.value)}
              style={selectStyle}
            >
              <option value="">Select Invoice</option>

              {invoices.map((doc) => (
                <option key={doc.document_id} value={doc.document_id}>
                  {doc.filename} — {doc.document_id}
                </option>
              ))}
            </select>
          </div>

          <button
            className="refresh-button"
            onClick={handleCompare}
            disabled={comparing}
          >
            <GitCompareArrows size={17} />
            {comparing ? "Comparing..." : "Compare Documents"}
          </button>
        </div>

        {purchaseOrders.length === 0 && (
          <p className="error-message">
            No Purchase Orders found. Upload a PO first.
          </p>
        )}

        {invoices.length === 0 && (
          <p className="error-message">
            No Invoices found. Upload an Invoice first.
          </p>
        )}

        {compareError && (
          <p className="error-message">{compareError}</p>
        )}

        {comparison && (
          <div style={{ marginTop: 35 }}>
            <h3>Comparison Results</h3>

            <div style={{ marginTop: 15 }}>
              <StatusBadge status={comparison.comparison.status} />
            </div>

            <p style={{ marginTop: 15 }}>
              {comparison.comparison.message}
            </p>

            {comparison.comparison.discrepancies?.length > 0 ? (
              <div className="table-wrapper" style={{ marginTop: 20 }}>
                <table>
                  <thead>
                    <tr>
                      <th>FIELD</th>
                      <th>PURCHASE ORDER</th>
                      <th>INVOICE</th>
                      <th>DIFFERENCE</th>
                    </tr>
                  </thead>

                  <tbody>
                    {comparison.comparison.discrepancies.map(
                      (item, index) => (
                        <tr key={index}>
                          <td>{item.field.replaceAll("_", " ")}</td>
                          <td>{item.purchase_order}</td>
                          <td>{item.invoice}</td>
                          <td>{item.difference ?? "Price difference"}</td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>No discrepancies in the compared fields.</p>
            )}

            <div style={{ marginTop: 25 }}>
              <h3>Investigation</h3>
              <p>{comparison.investigation.explanation}</p>

              <p>
                <strong>Recommendation:</strong>{" "}
                {comparison.investigation.recommendation}
              </p>
            </div>

            <div style={{ marginTop: 20 }}>
              <h3>Approval Status</h3>

              <StatusBadge
                status={comparison.approval.approval_status}
              />

              <p>
                {comparison.approval.message || comparison.approval.reason}
              </p>
            </div>
          </div>
        )}
      </section>
    );
  }

  // APPROVAL MANAGEMENT
  function renderApprovals() {
    return (
      <section className="panel page-panel">
        <p className="eyebrow">HUMAN REVIEW</p>
        <h2>Approval Management</h2>

        <p className="welcome-text">
          Review requests before executing important business actions.
        </p>

        {actionMessage && (
          <p className="success-message">{actionMessage}</p>
        )}

        {actionError && (
          <p className="error-message">{actionError}</p>
        )}

        {approvals.length === 0 ? (
          <EmptyState text="No approval requests found." />
        ) : (
          <div className="approval-list">
            {approvals.map((item) => {
              const execution = executions.find(
                (entry) => entry.approval_id === item.approval_id
              );

              const verification = execution
                ? verifications.find(
                    (entry) => entry.execution_id === execution.execution_id
                  )
                : null;

              return (
                <div className="approval-item" key={item.approval_id}>
                  <div style={{ flex: 1 }}>
                    <strong>{item.approval_id}</strong>

                    <p>{item.reason}</p>
                    <small>{item.created_at}</small>

                    <div style={{ marginTop: 12 }}>
                      <StatusBadge status={item.approval_status} />
                    </div>

                    {item.approval_status === "pending" && (
                      <div
                        style={{
                          display: "flex",
                          gap: 10,
                          marginTop: 15,
                          flexWrap: "wrap",
                        }}
                      >
                        <button
                          className="refresh-button"
                          disabled={processingId === item.approval_id}
                          onClick={() =>
                            handleApprovalDecision(
                              item.approval_id,
                              "approve"
                            )
                          }
                        >
                          <Check size={16} />
                          Approve
                        </button>

                        <button
                          className="refresh-button"
                          disabled={processingId === item.approval_id}
                          onClick={() =>
                            handleApprovalDecision(
                              item.approval_id,
                              "reject"
                            )
                          }
                        >
                          <XCircle size={16} />
                          Reject
                        </button>
                      </div>
                    )}

                    {item.approval_status === "approved" && !execution && (
                      <button
                        className="refresh-button"
                        style={{ marginTop: 15 }}
                        disabled={processingId === item.approval_id}
                        onClick={() => handleExecute(item.approval_id)}
                      >
                        <Play size={16} />
                        Execute Approved Action
                      </button>
                    )}

                    {execution && (
                      <div style={{ marginTop: 15 }}>
                        <p>
                          <strong>Execution ID:</strong>{" "}
                          {execution.execution_id}
                        </p>

                        <StatusBadge status={execution.execution_status} />

                        {!verification && (
                          <button
                            className="refresh-button"
                            style={{ marginTop: 12 }}
                            disabled={
                              processingId === execution.execution_id
                            }
                            onClick={() =>
                              handleVerify(execution.execution_id)
                            }
                          >
                            <ShieldCheck size={16} />
                            Verify Execution
                          </button>
                        )}

                        {verification && (
                          <div style={{ marginTop: 12 }}>
                            <p><strong>Verification</strong></p>

                            <StatusBadge
                              status={verification.verification_status}
                            />

                            <p>{verification.message}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    );
  }

  // AUDIT TRAIL
  function renderAudit() {
    return (
      <section className="panel page-panel">
        <p className="eyebrow">SYSTEM RECORDS</p>
        <h2>Audit Trail</h2>

        <p className="welcome-text">
          Review recorded workflow events and their timestamps.
        </p>

        {auditLogs.length === 0 ? (
          <EmptyState text="No audit events found." />
        ) : (
          <div className="audit-list">
            {auditLogs.map((log) => (
              <div className="audit-item" key={log.audit_id}>
                <div className="audit-icon">
                  <History size={17} />
                </div>

                <div className="audit-content">
                  <strong>{log.action.replaceAll("_", " ")}</strong>
                  <p>{log.audit_id}</p>
                  <small>{log.timestamp}</small>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    );
  }

  function renderPage() {
    switch (activePage) {
      case "Documents":
        return renderDocuments();

      case "Comparison":
        return renderComparison();

      case "Approvals":
        return renderApprovals();

      case "Audit Trail":
        return renderAudit();

      default:
        return renderDashboard();
    }
  }

  // MAIN LAYOUT
  return (
    <div className="app-shell">
      {mobileMenu && (
        <button
          className="mobile-overlay"
          onClick={() => setMobileMenu(false)}
          aria-label="Close navigation"
        />
      )}

      <aside className={`sidebar ${mobileMenu ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-logo">
            <ShieldCheck size={25} />
          </div>

          <div>
            <h1>ProofChain<span> AI</span></h1>
            <p>DOCUMENT INTELLIGENCE</p>
          </div>

          <button
            className="close-menu"
            onClick={() => setMobileMenu(false)}
            aria-label="Close menu"
          >
            <X size={19} />
          </button>
        </div>

        <p className="nav-label">WORKSPACE</p>

        <nav className="navigation">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.name}
                className={`nav-item ${
                  activePage === item.name ? "active" : ""
                }`}
                onClick={() => {
                  setActivePage(item.name);
                  setMobileMenu(false);
                  setCompareError("");
                  setActionError("");
                }}
              >
                <Icon size={19} />
                <span>{item.name}</span>

                {item.name === "Approvals" && pendingApprovals > 0 && (
                  <span className="nav-count">{pendingApprovals}</span>
                )}
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="security-card">
            <ShieldCheck size={20} />
            <strong>Approval-first workflow</strong>
            <p>Important actions require human approval.</p>
          </div>

          <div className="profile">
            <div className="profile-avatar">PC</div>
            <div>
              <strong>ProofChain Admin</strong>
              <p>Workspace administrator</p>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button
            className="menu-button"
            onClick={() => setMobileMenu(true)}
            aria-label="Open menu"
          >
            <Menu size={21} />
          </button>

          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{activePage}</strong>
          </div>

          <div className="topbar-right">
            <span className="system-status">
              <span /> System connected
            </span>

            <div className="notification-icon">
              <Bell size={19} />
            </div>
          </div>
        </header>

        <div className="content-area">
          {loading ? (
            <div className="loading-state">
              <RefreshCw className="spin" size={23} />
              <p>Loading ProofChain AI...</p>
            </div>
          ) : (
            <>
              {error && <p className="error-message">{error}</p>}
              {renderPage()}
            </>
          )}

          <footer>
            ProofChain AI <span>·</span> Business Document Intelligence
            <span>·</span> Human approval before execution
          </footer>
        </div>
      </main>
    </div>
  );
}

// REUSABLE COMPONENTS

function WorkflowItem({ label, value, color }) {
  return (
    <div className="workflow-item">
      <span className={`workflow-dot ${color}`} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${color}`}>{icon}</div>

      <div>
        <p>{label}</p>
        <h3>{value}</h3>
      </div>
    </div>
  );
}

function DocumentTable({ documents }) {
  if (!documents.length) {
    return <EmptyState text="No documents uploaded yet." />;
  }

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>DOCUMENT</th>
            <th>TYPE</th>
            <th>DOCUMENT ID</th>
            <th>UPLOADED</th>
            <th>STATUS</th>
          </tr>
        </thead>

        <tbody>
          {documents.map((doc) => (
            <tr key={doc.document_id}>
              <td>
                <div className="file-cell">
                  <div className="file-icon">
                    <FileText size={17} />
                  </div>
                  <strong>{doc.filename}</strong>
                </div>
              </td>

              <td>{doc.document_type || "Unknown"}</td>
              <td className="id-cell">{doc.document_id}</td>
              <td>{new Date(doc.upload_time).toLocaleDateString()}</td>
              <td><StatusBadge status="processed" /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StatusBadge({ status }) {
  const normalized = (status || "unknown").toLowerCase();

  return (
    <span className={`status-badge ${normalized}`}>
      {normalized.replaceAll("_", " ")}
    </span>
  );
}

function EmptyState({ text }) {
  return (
    <div className="empty-state">
      <CheckCircle2 size={25} />
      <p>{text}</p>
    </div>
  );
}

export default App;
