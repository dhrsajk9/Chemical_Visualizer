import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Scatter } from 'react-chartjs-2'; // Changed to Scatter
import { Chart as ChartJS } from 'chart.js/auto';

const Dashboard = ({ token, onLogout }) => {
  const [file, setFile] = useState(null);
  const [history, setHistory] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  const authHeader = { headers: { Authorization: `Token ${token}` } };

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/files/', authHeader);
      setHistory(res.data);
    } catch (err) { console.error(err); }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post('http://127.0.0.1:8000/api/files/', formData, authHeader);
      fetchHistory(); 
      alert("Upload Successful");
    } catch (err) { alert("Upload Failed"); }
  };

  const loadAnalytics = async (id) => {
    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/analytics/${id}/`, authHeader);
      setAnalytics(res.data);
    } catch (err) { console.error(err); }
  };

  const downloadPDF = async (id, filename) => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/pdf/${id}/`, {
        headers: { Authorization: `Token ${token}` },
        responseType: 'blob',
      });
      const file = new Blob([response.data], {type: 'application/pdf'});
      const fileURL = URL.createObjectURL(file);
      const link = document.createElement('a');
      link.href = fileURL;
      link.setAttribute('download', `report_${filename}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error(error);
      alert("Error downloading PDF");
    }
  };

  // --- AI CHART DATA ---
  const scatterData = analytics ? {
    datasets: [
      {
        label: 'Normal Operation',
        data: analytics.dataset
          .filter(row => !row.is_anomaly)
          .map(row => ({ x: row.Temperature, y: row.Pressure })),
        backgroundColor: 'rgba(54, 162, 235, 1)', // Blue
      },
      {
        label: 'AI Detected Anomalies',
        data: analytics.dataset
          .filter(row => row.is_anomaly)
          .map(row => ({ x: row.Temperature, y: row.Pressure })),
        backgroundColor: 'rgba(255, 99, 132, 1)', // Red
        pointRadius: 6,
      }
    ]
  } : null;

  return (
    <div>
      <div className="d-flex justify-content-between mb-4">
        <h2>Dashboard</h2>
        <button className="btn btn-outline-danger" onClick={onLogout}>Logout</button>
      </div>

      <div className="card mb-4 p-3">
        <h4>Upload New Dataset</h4>
        <form onSubmit={handleUpload} className="d-flex gap-2">
          <input type="file" className="form-control" onChange={e => setFile(e.target.files[0])} required />
          <button type="submit" className="btn btn-success">Upload</button>
        </form>
      </div>

      <div className="row">
        <div className="col-md-4">
          <div className="list-group">
            <h5>Recent Uploads (Last 5)</h5>
            {history.map(item => (
              <button key={item.id} className="list-group-item list-group-item-action"
                onClick={() => loadAnalytics(item.id)}>
                {item.filename} <br />
                <small className="text-muted">{new Date(item.uploaded_at).toLocaleString()}</small>
              </button>
            ))}
          </div>
        </div>

        <div className="col-md-8">
          {analytics ? (
            <div className="card p-3">
              <div className="d-flex justify-content-between">
                <h3>Analysis: {analytics.filename}</h3>
                <button className="btn btn-sm btn-dark" 
                  onClick={() => downloadPDF(history.find(h => h.filename === analytics.filename)?.id, analytics.filename)}>
                  Download Report
                </button>
              </div>

              {/* AI VISUALIZATION */}
              <div className="mt-3 p-2 border rounded bg-light">
                <h5 className="text-center">AI Anomaly Detection (Pressure vs Temp)</h5>
                <div style={{ height: '350px' }}>
                  <Scatter 
                    data={scatterData} 
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        x: { title: { display: true, text: 'Temperature (C)' } },
                        y: { title: { display: true, text: 'Pressure (Pa)' } }
                      }
                    }} 
                  />
                </div>
                <small className="text-muted d-block text-center mt-2">
                  *Red points indicate equipment behaving abnormally (Isolation Forest Model)
                </small>
              </div>

              {/* HIGHLIGHTED DATA TABLE */}
              <h5 className="mt-4">Detailed Data</h5>
              <div style={{ maxHeight: '300px', overflow: 'auto' }}>
                <table className="table table-sm table-bordered">
                  <thead className="table-dark" style={{ position: 'sticky', top: 0 }}>
                    <tr>
                      <th>Equipment</th>
                      <th>Type</th>
                      <th>Flowrate</th>
                      <th>Pressure</th>
                      <th>Temp</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.dataset.map((row, i) => (
                      <tr key={i} className={row.is_anomaly ? "table-danger" : ""}>
                        <td>{row['Equipment Name']}</td>
                        <td>{row.Type}</td>
                        <td>{row.Flowrate}</td>
                        <td>{row.Pressure}</td>
                        <td>{row.Temperature}</td>
                        <td>
                          {row.is_anomaly ? 
                            <span className="badge bg-danger">ANOMALY</span> : 
                            <span className="badge bg-success">OK</span>
                          }
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="alert alert-info">Select a file from the history to view analytics.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;