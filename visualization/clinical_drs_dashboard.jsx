import React, { useState } from "react";

/**
 * ClinicalDRSDashboard
 *
 * Fetches a DRS object using the clinician's GA4GH Passport session token
 * and resolves the secure cloud URI for downstream analysis tools.
 *
 * Previously: clinical_drs_dashboard.jsx
 */
function ClinicalDRSDashboard({ sessionToken }) {
  const [cloudUri, setCloudUri] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchDrsObject = async (datasetId) => {
    setError(null);
    setLoading(true);
    try {
      const response = await fetch(
        `https://your-biobank.org/ga4gh/drs/v1/objects/${datasetId}`,
        { headers: { Authorization: `Bearer ${sessionToken}` } }
      );
      if (!response.ok) {
        throw new Error(`DRS request failed: ${response.status}`);
      }
      const data = await response.json();
      setCloudUri(data.access_methods.access_url.url);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => fetchDrsObject("cohort-A001")} disabled={loading}>
        {loading ? "Loading…" : "Load Patient Cohort"}
      </button>
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {cloudUri && <p>Target Cloud Dataset: {cloudUri}</p>}
    </div>
  );
}

export default ClinicalDRSDashboard;
