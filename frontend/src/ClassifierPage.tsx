import React, { useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

const API_URL = "http://localhost:8000/process";

const ClassifierPage: React.FC = () => {
  const [connectionString, setConnectionString] = useState("");
  const [jsonFile, setJsonFile] = useState<File | null>(null);
  const [useFile, setUseFile] = useState(true);
  const [categories, setCategories] = useState<{[key: string]: string[]}>({});
  const [newCategoryName, setNewCategoryName] = useState("");
  const [newCategoryLabel, setNewCategoryLabel] = useState("");
  const [user, setUser] = useState("");
  const [azureContainer, setAzureContainer] = useState("images");
  const [azureCvEndpoint, setAzureCvEndpoint] = useState("");
  const [azureCvKey, setAzureCvKey] = useState("");
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({
    connectionString: false,
    jsonFile: false,
    categories: false,
  });

  const handleJsonUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setJsonFile(e.target.files[0]);
  };

  const handleAddCategory = () => {
    const categoryName = newCategoryName.trim();
    const categoryLabel = newCategoryLabel.trim();
    
    if (categoryName && categoryLabel) {
      setCategories(prev => ({
        ...prev,
        [categoryName]: prev[categoryName] 
          ? [...prev[categoryName], categoryLabel]
          : [categoryLabel]
      }));
      setNewCategoryLabel("");
    }
  };

  const handleRemoveCategory = (categoryName: string) => {
    setCategories(prev => {
      const newCategories = { ...prev };
      delete newCategories[categoryName];
      return newCategories;
    });
  };

  const handleRemoveLabel = (categoryName: string, labelToRemove: string) => {
    setCategories(prev => ({
      ...prev,
      [categoryName]: prev[categoryName].filter(label => label !== labelToRemove)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({ connectionString: false, jsonFile: false, categories: false });
    let hasError = false;

    if (!connectionString.trim()) {
      setErrors((prev) => ({ ...prev, connectionString: true }));
      hasError = true;
    }
    if (useFile && !jsonFile) {
      setErrors((prev) => ({ ...prev, jsonFile: true }));
      hasError = true;
    }
    if (!useFile && Object.keys(categories).length === 0) {
      setErrors((prev) => ({ ...prev, categories: true }));
      hasError = true;
    }
    if (hasError) return;

    try {
      setLoading(true);
      
      const formData = new FormData();
      
      if (useFile && jsonFile) {
        formData.append('categories_json', jsonFile);
      } else {
        // Create a JSON file from manual categories
        const jsonBlob = new Blob([JSON.stringify(categories)], { type: 'application/json' });
        formData.append('categories_json', jsonBlob, 'categories.json');
      }
      
      // Add optional parameters
      formData.append('azure_connection_string', connectionString);
      if (user.trim()) {
        formData.append('user', user);
      }
      if (azureContainer.trim()) {
        formData.append('azure_container', azureContainer);
      }
      if (azureCvEndpoint.trim()) {
        formData.append('azure_cv_endpoint', azureCvEndpoint);
      }
      if (azureCvKey.trim()) {
        formData.append('azure_cv_key', azureCvKey);
      }

      const res = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error(err);
      alert('Error processing request. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <div className="mb-4">
        <h2>🧠 Azure Image Processor</h2>
      </div>

      <form onSubmit={handleSubmit} className="card p-4 shadow-sm">
        <div className="mb-3">
          <label className="form-label fw-bold">Azure Storage Connection String</label>
          <input
            type="text"
            className={`form-control ${errors.connectionString ? "is-invalid" : ""}`}
            value={connectionString}
            onChange={(e) => setConnectionString(e.target.value)}
            placeholder="DefaultEndpointsProtocol=https;AccountName=..."
          />
          {errors.connectionString && (
            <div className="invalid-feedback">Connection string is required</div>
          )}
        </div>

        <div className="mb-3">
          <label className="form-label fw-bold">User (Optional)</label>
          <input
            type="text"
            className="form-control"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            placeholder="Specific user folder to process (leave empty for all users)"
          />
        </div>

        <div className="mb-3">
          <label className="form-label fw-bold">Azure Container</label>
          <input
            type="text"
            className="form-control"
            value={azureContainer}
            onChange={(e) => setAzureContainer(e.target.value)}
            placeholder="images"
          />
        </div>

        <div className="form-check form-switch mb-3">
          <input
            className="form-check-input"
            type="checkbox"
            id="useFileToggle"
            checked={!useFile}
            onChange={() => setUseFile(!useFile)}
          />
          <label className="form-check-label" htmlFor="useFileToggle">
            {useFile ? "Switch to manual category entry" : "Switch to JSON upload"}
          </label>
        </div>

        {useFile ? (
          <div className="mb-3">
            <label className="form-label fw-bold">Upload JSON File</label>
            <input
              type="file"
              className={`form-control ${errors.jsonFile ? "is-invalid" : ""}`}
              accept=".json"
              onChange={handleJsonUpload}
            />
            {errors.jsonFile && (
              <div className="invalid-feedback">Please upload a JSON file</div>
            )}
          </div>
        ) : (
          <div className="mb-3">
            <label className="form-label fw-bold">Categories</label>
            <div className="row mb-2">
              <div className="col-md-6">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Category name (e.g., 'animals')"
                  value={newCategoryName}
                  onChange={(e) => setNewCategoryName(e.target.value)}
                />
              </div>
              <div className="col-md-4">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Label (e.g., 'dog')"
                  value={newCategoryLabel}
                  onChange={(e) => setNewCategoryLabel(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddCategory();
                    }
                  }}
                />
              </div>
              <div className="col-md-2">
                <button
                  type="button"
                  className="btn btn-outline-primary w-100"
                  onClick={handleAddCategory}
                >
                  Add
                </button>
              </div>
            </div>
            {errors.categories && (
              <div className="text-danger small mb-2">
                Please add at least one category with labels
              </div>
            )}
            {Object.keys(categories).length > 0 && (
              <div>
                {Object.entries(categories).map(([categoryName, labels]) => (
                  <div key={categoryName} className="card mb-2">
                    <div className="card-header d-flex justify-content-between align-items-center">
                      <h6 className="mb-0">📁 {categoryName}</h6>
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => handleRemoveCategory(categoryName)}
                      >
                        Remove Category
                      </button>
                    </div>
                    <div className="card-body">
                      <div className="d-flex flex-wrap gap-1">
                        {labels.map((label, index) => (
                          <span
                            key={index}
                            className="badge bg-secondary d-flex align-items-center"
                          >
                            {label}
                            <button
                              type="button"
                              className="btn-close btn-close-white ms-1"
                              style={{ fontSize: '0.6em' }}
                              onClick={() => handleRemoveLabel(categoryName, label)}
                              aria-label="Remove label"
                            />
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <button type="submit" className="btn btn-primary w-100" disabled={loading}>
          {loading ? "Processing..." : "Process Images"}
        </button>
      </form>

      {response && (
        <div className="card mt-4 p-3">
          <h5>Processing Result</h5>
          <div className="alert alert-success">
            <strong>Status:</strong> {response.status}<br/>
            <strong>Message:</strong> {response.message}<br/>
            <strong>Total Results:</strong> {response.total_results}
            {response.user_filter && <><br/><strong>User Filter:</strong> {response.user_filter}</>}
          </div>

          {response.results && response.results.length > 0 && (
            <>
              <h6 className="mt-3">Category Results by User</h6>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={response.results.map((result: any) => ({
                    name: `${result.user} - ${result.category}`,
                    score: result.score,
                    user: result.user,
                    category: result.category
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis domain={[0, 1]} />
                  <Tooltip 
                    formatter={(value: any) => [
                      `${(value * 100).toFixed(1)}%`, 
                      'Confidence Score'
                    ]}
                    labelFormatter={(label: any, payload: any) => 
                      payload && payload[0] ? 
                      `User: ${payload[0].payload.user}, Category: ${payload[0].payload.category}` : 
                      label
                    }
                  />
                  <Legend />
                  <Bar dataKey="score" fill="#007bff" name="Confidence Score" />
                </BarChart>
              </ResponsiveContainer>

              <div className="mt-3">
                <h6>Detailed Results</h6>
                <div className="table-responsive">
                  <table className="table table-striped">
                    <thead>
                      <tr>
                        <th>User</th>
                        <th>Category</th>
                        <th>Confidence Score</th>
                        <th>Confidence %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {response.results
                        .sort((a: any, b: any) => b.score - a.score)
                        .map((result: any, index: number) => (
                        <tr key={index}>
                          <td><strong>{result.user}</strong></td>
                          <td><span className="badge bg-primary">{result.category}</span></td>
                          <td>{result.score.toFixed(3)}</td>
                          <td>
                            <div className="progress" style={{ width: '100px' }}>
                              <div 
                                className="progress-bar" 
                                style={{ width: `${result.score * 100}%` }}
                              >
                                {(result.score * 100).toFixed(1)}%
                              </div>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="mt-3">
                <h6>Summary by User</h6>
                <div className="row">
                  {Array.from(new Set(response.results.map((r: any) => r.user))).map((user: any) => {
                    const userResults = response.results.filter((r: any) => r.user === user);
                    const topCategory = userResults.reduce((prev: any, current: any) => 
                      (prev.score > current.score) ? prev : current
                    );
                    return (
                      <div key={user} className="col-md-4 mb-3">
                        <div className="card">
                          <div className="card-body">
                            <h6 className="card-title">👤 {user}</h6>
                            <p className="card-text">
                              <strong>Top Category:</strong> {topCategory.category}<br/>
                              <strong>Confidence:</strong> {(topCategory.score * 100).toFixed(1)}%
                            </p>
                            <div className="mt-2">
                              {userResults.map((result: any, idx: number) => (
                                <div key={idx} className="d-flex justify-content-between align-items-center mb-1">
                                  <small className="text-muted">{result.category}</small>
                                  <div className="progress" style={{ width: '60px', height: '8px' }}>
                                    <div 
                                      className="progress-bar progress-bar-sm" 
                                      style={{ width: `${result.score * 100}%` }}
                                    ></div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          )}

          {response.output_files && (
            <div className="mt-3">
              <h6>Output Files</h6>
              <div className="list-group">
                {response.output_files.excel && (
                  <a href={`http://localhost:8000/download/top3_by_user.xlsx`} className="list-group-item list-group-item-action">
                    📊 Download Excel Report
                  </a>
                )}
                {response.output_files.html && (
                  <a href={`http://localhost:8000/download/index.html`} className="list-group-item list-group-item-action">
                    📄 Download HTML Report
                  </a>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ClassifierPage;
