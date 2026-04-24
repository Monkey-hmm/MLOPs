import { useState, useRef, useEffect } from 'react';
import './App.css';

// -------------------------------------------------------------
// Component: JobUpload (The original form)
// -------------------------------------------------------------
function JobUpload() {
  const [teamId, setTeamId] = useState('');
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle');
  const [jobId, setJobId] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => e.preventDefault();

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!teamId.trim() || !file) {
      setErrorMsg('Please provide both Team ID and an image.');
      setStatus('error');
      return;
    }

    setStatus('loading');
    setErrorMsg('');

    const formData = new FormData();
    formData.append('team_id', teamId);
    formData.append('image', file);

    try {
      const response = await fetch('/append', {
        method: 'POST',
        headers: { 'accept': 'application/json' },
        body: formData
      });

      if (!response.ok) throw new Error('Failed to append job');

      const data = await response.json();
      setJobId(data.job_id);
      setStatus('success');
      setFile(null);
      setTeamId('');
      if(fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      console.error(err);
      setErrorMsg('An error occurred while uploading. Please try again.');
      setStatus('error');
    }
  };

  return (
    <div className="glass-card form-container">
      <header className="header">
        <h1 className="title">Submit Inference Job</h1>
        <p className="subtitle">Upload your image and set the team identifier to queue the job.</p>
      </header>

      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label htmlFor="teamId" className="label">Team ID</label>
          <input
            type="text"
            id="teamId"
            className="input"
            placeholder="e.g. alpha-squad"
            value={teamId}
            onChange={(e) => setTeamId(e.target.value)}
            disabled={status === 'loading'}
          />
        </div>

        <div className="form-group">
          <label className="label">Image Upload</label>
          <div 
            className={`dropzone ${file ? 'has-file' : ''}`}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              accept="image/*" 
              className="hidden-input"
              disabled={status === 'loading'}
            />
            {file ? (
              <div className="file-preview">
                <div className="file-icon">🖼️</div>
                <div className="file-info">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">{(file.size / 1024).toFixed(2)} KB</span>
                </div>
              </div>
            ) : (
              <div className="dropzone-content">
                <div className="upload-icon">⬆️</div>
                <p className="drop-text">Click or drag image to upload</p>
                <p className="drop-hint">Supports PNG, JPG, JPEG</p>
              </div>
            )}
          </div>
        </div>

        {status === 'error' && <div className="alert alert-error">{errorMsg}</div>}
        {status === 'success' && (
          <div className="alert alert-success">
            Job enqueued successfully! 
            <div className="job-id-box"><code>{jobId}</code></div>
          </div>
        )}

        <button type="submit" className={`submit-btn ${status === 'loading' ? 'loading' : ''}`} disabled={status === 'loading'}>
          {status === 'loading' ? 'Uploading...' : 'Submit Job'}
        </button>
      </form>
    </div>
  );
}

// -------------------------------------------------------------
// Component: Admin Login
// -------------------------------------------------------------
function AdminLogin({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username === 'cyberthon' && password === 'cyberthon') {
      onLogin();
    } else {
      setError(true);
    }
  };

  return (
    <div className="glass-card form-container">
      <header className="header">
        <h1 className="title">Admin Login</h1>
        <p className="subtitle">Secure access to the MLOps Dashboard.</p>
      </header>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="label">Username</label>
          <input 
            type="text" 
            className="input" 
            value={username} 
            onChange={e => setUsername(e.target.value)} 
          />
        </div>
        <div className="form-group">
          <label className="label">Password</label>
          <input 
            type="password" 
            className="input" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
          />
        </div>
        {error && <div className="alert alert-error">Invalid credentials.</div>}
        <button type="submit" className="submit-btn">Login to Dashboard</button>
      </form>
    </div>
  );
}

// -------------------------------------------------------------
// Component: Admin Dashboard
// -------------------------------------------------------------
function AdminDashboard() {
  const [data, setData] = useState({ queued: [], running: [], completed: [], results: [] });
  const [loading, setLoading] = useState(true);

  const fetchDashboard = async () => {
    try {
      // Proxied to backend GET /
      const res = await fetch('/api/dashboard');
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Poll every 5 seconds
  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleTimeString();
  };

  return (
    <div className="glass-card dashboard-container" style={{ maxWidth: '100%' }}>
      <header className="header" style={{ marginBottom: '1rem', textAlign: 'left', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="title" style={{ fontSize: '1.5rem', marginBottom: '0' }}>MLOps Queue Monitor</h1>
          <p className="subtitle">Real-time status of all inference jobs.</p>
        </div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          {loading ? 'Refreshing...' : 'Live 🟢'}
        </div>
      </header>

      <div className="dashboard-grid">
        {/* Queued Panel */}
        <div className="dashboard-panel">
          <div className="panel-header">
            <h2 className="panel-title">
              <span className="badge badge-queued">Queued</span>
            </h2>
            <span className="panel-count">{data.queued.length} jobs</span>
          </div>
          <div className="table-container">
            {data.queued.length === 0 ? (
              <div className="empty-state">Queue is empty</div>
            ) : (
              <table className="data-table">
                <thead><tr><th>Job ID</th><th>Team</th><th>Created</th></tr></thead>
                <tbody>
                  {data.queued.map(job => (
                    <tr key={job.id}>
                      <td className="uuid-cell">{job.id.substring(0,8)}...</td>
                      <td>{job.team_id}</td>
                      <td>{formatDate(job.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Running Panel */}
        <div className="dashboard-panel">
          <div className="panel-header">
            <h2 className="panel-title">
              <span className="badge badge-running">Running</span>
            </h2>
            <span className="panel-count">{data.running.length} workers</span>
          </div>
          <div className="table-container">
            {data.running.length === 0 ? (
              <div className="empty-state">No active workers</div>
            ) : (
              <table className="data-table">
                <thead><tr><th>Job ID</th><th>Team</th><th>Started</th></tr></thead>
                <tbody>
                  {data.running.map(job => (
                    <tr key={job.id}>
                      <td className="uuid-cell">{job.id.substring(0,8)}...</td>
                      <td>{job.team_id}</td>
                      <td>{formatDate(job.started_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Completed Panel */}
        <div className="dashboard-panel">
          <div className="panel-header">
            <h2 className="panel-title">
              <span className="badge badge-completed">Completed</span>
            </h2>
            <span className="panel-count">{data.completed.length} total</span>
          </div>
          <div className="table-container">
            {data.completed.length === 0 ? (
              <div className="empty-state">No jobs completed yet</div>
            ) : (
              <table className="data-table">
                <thead><tr><th>Job ID</th><th>Team</th><th>Finished</th></tr></thead>
                <tbody>
                  {data.completed.map(job => (
                    <tr key={job.id}>
                      <td className="uuid-cell">{job.id.substring(0,8)}...</td>
                      <td>{job.team_id}</td>
                      <td>{formatDate(job.finished_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Results Panel */}
        <div className="dashboard-panel">
          <div className="panel-header">
            <h2 className="panel-title">
              <span>Results</span>
            </h2>
            <span className="panel-count">{data.results.length} total</span>
          </div>
          <div className="table-container">
            {data.results.length === 0 ? (
              <div className="empty-state">No inference results yet</div>
            ) : (
              <table className="data-table">
                <thead><tr><th>Job ID</th><th>Prediction</th><th>Confidence</th></tr></thead>
                <tbody>
                  {data.results.map(res => (
                    <tr key={res.id}>
                      <td className="uuid-cell">{res.job_id.substring(0,8)}...</td>
                      <td>
                        <span className={`badge ${res.prediction === 'real' ? 'badge-real' : 'badge-fake'}`}>
                          {res.prediction.toUpperCase()}
                        </span>
                      </td>
                      <td>{(res.confidence * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// Main App Component
// -------------------------------------------------------------
function App() {
  const [activeTab, setActiveTab] = useState('submit'); // 'submit' or 'admin'
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);

  return (
    <div className="app-container">
      <nav className="nav-bar">
        <button 
          className={`nav-tab ${activeTab === 'submit' ? 'active' : ''}`}
          onClick={() => setActiveTab('submit')}
        >
          Submit Job
        </button>
        <button 
          className={`nav-tab ${activeTab === 'admin' ? 'active' : ''}`}
          onClick={() => setActiveTab('admin')}
        >
          Admin Dashboard
        </button>
      </nav>

      {activeTab === 'submit' && <JobUpload />}
      
      {activeTab === 'admin' && (
        !isAdminAuthenticated ? (
          <AdminLogin onLogin={() => setIsAdminAuthenticated(true)} />
        ) : (
          <AdminDashboard />
        )
      )}
    </div>
  );
}

export default App;
