
import { CheckCircle, XCircle, AlertTriangle, Loader } from "lucide-react";
import PropTypes from "prop-types";

export const StatusIndicator = ({ status, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center text-gray-500">
        <Loader className="w-10 h-10 animate-spin mb-1" />
        <span className="text-sm font-medium">Loading...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center text-red-500">
        <AlertTriangle className="w-10 h-10 mb-1" />
        <span className="text-sm font-medium">Status unavailable</span>
      </div>
    );
  }

  const statusConfig = {
    Pass: { icon: CheckCircle, color: "text-green-500", label: "Pass" },
    Fail: { icon: XCircle, color: "text-red-500", label: "Fail" },
    Incomplete: { icon: AlertTriangle, color: "text-yellow-500", label: "Incomplete" },
  };

  const config = statusConfig[status] || statusConfig["Incomplete"];
  const Icon = config.icon;

  return (
    <div className="flex flex-col items-center justify-center">
      <Icon className={`w-12 h-12 ${config.color}`} />
      <span className="text-sm font-semibold mt-1">{config.label}</span>
    </div>
  );
};

StatusIndicator.propTypes = {
  status: PropTypes.oneOf(["Pass", "Fail", "Incomplete"]),
  isLoading: PropTypes.bool,
  error: PropTypes.string,
};
