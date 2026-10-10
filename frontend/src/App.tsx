import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Shell } from "./components/Shell";
import { Comparison } from "./screens/Comparison";
import { Destination } from "./screens/Destination";
import { OperatorDashboard } from "./screens/OperatorDashboard";
import { PickupCard } from "./screens/PickupCard";
import { TapIn } from "./screens/TapIn";
import { TripSummary } from "./screens/TripSummary";
import { TripProvider } from "./state/trip";

export function App() {
  return (
    <TripProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Shell />}>
            <Route path="/" element={<TapIn />} />
            <Route path="/drop" element={<Destination />} />
            <Route path="/pickup" element={<PickupCard />} />
            <Route path="/summary" element={<TripSummary />} />
            <Route path="/operator" element={<OperatorDashboard />} />
            <Route path="/compare" element={<Comparison />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </TripProvider>
  );
}
