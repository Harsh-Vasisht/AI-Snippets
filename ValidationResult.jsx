
import React, { useEffect, useState } from "react";
import axios from "axios";
import { StatusIndicator } from "../components/StatusIndicator";

export const ValidationResult = ({ featureName }) => {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await axios.get(`/api/validation/status?feature=${featureName}`);
        setStatus(res.data.status);
      } catch (err) {
        setError("Failed to fetch status");
      } finally {
        setLoading(false);
      }
    };
    fetchStatus();
  }, [featureName]);

  return (
    <div className="flex flex-col items-center justify-center mt-6">
      <h2 className="text-xl font-bold mb-4">{featureName} Validation</h2>
      <StatusIndicator status={status} isLoading={loading} error={error} />
    </div>
  );
};
