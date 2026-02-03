import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS } from 'chart.js/auto';

const Dashboard = ({ token, onLogout }) => {
  const [file, setFile] = useState(null);
  const [history, setHistory] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  const authHeader = { headers: { Authorization: `Token ${token}` } };

  // Fetch history on load
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

  // --- FIXED DOWNLOAD FUNCTION ---
  const downloadPDF = async (id, filename) => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/pdf/${id}/`, {
        headers: { Authorization: `Token ${token}` },
        responseType: 'blob', // IMPORTANT: Expect binary data
      });

      // Create a Blob from the PDF Stream
      const file = new Blob(
        [response.data], 
        {type: 'application/pdf'}
      );

      // Build a link to trigger the download
      const fileURL = URL.createObjectURL(file);
      const link = document.createElement('a');
      link.href = fileURL;
      link.setAttribute('download', `report_${filename}.pdf`);
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      link.remove();
    } catch (error) {
      console.error(error);
      alert("Error downloading PDF");
    }
  };

  // Prepare Chart Data
  const chartData = analytics ? {
    labels: Object.keys(analytics.type_distribution),
    datasets: [{
      label: 'Equipment Count by Type',
      data: Object.values(analytics.type_distribution),
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
    }]
  } : null;

  return (
    <div>
      <div className="d-flex justify-content-between mb-4">
        <h2>Dashboard</h2>
        <button className="btn btn-outline-danger" onClick={onLogout}>Logout</button>
      </div>

      {/* Upload Section */}
      <div className="card mb-4 p-3">
        <h4>Upload New Dataset</h4>
        <form onSubmit={handleUpload} className="d-flex gap-2">
          <input type="file" className="form-control" onChange={e => setFile(e.target.files[0])} required />
          <button type="submit" className="btn btn-success">Upload</button>
        </form>
      </div>

      <div className="row">
        {/* History Sidebar */}
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

        {/* Analytics View */}
        <div className="col-md-8">
          {analytics ? (
            <div className="card p-3">
              <h3>Analysis: {analytics.filename}</h3>
              
              {/* FIXED BUTTON CALL */}
              <button className="btn btn-primary mb-3 w-25" 
                 onClick={() => downloadPDF(history.find(h => h.filename === analytics.filename)?.id, analytics.filename)}>
                  Download PDF Report
              </button>

              <div className="row mb-3">
                <div className="col"><strong>Total Count:</strong> {analytics.total_count}</div>
                <div className="col"><strong>Avg Temp:</strong> {analytics.averages.Temperature?.toFixed(2)}</div>
                <div className="col"><strong>Avg Pressure:</strong> {analytics.averages.Pressure?.toFixed(2)}</div>
              </div>

              <div style={{ height: '300px' }}>
                <Bar data={chartData} options={{ maintainAspectRatio: false }} />
              </div>

              <h5 className="mt-4">Data Preview</h5>
              <table className="table table-sm table-striped">
                <thead>
                  <tr>{Object.keys(analytics.preview[0] || {}).map(k => <th key={k}>{k}</th>)}</tr>
                </thead>
                <tbody>
                  {analytics.preview.map((row, i) => (
                    <tr key={i}>{Object.values(row).map((val, j) => <td key={j}>{val}</td>)}</tr>
                  ))}
                </tbody>
              </table>
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