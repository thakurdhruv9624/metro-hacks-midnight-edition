import { useEffect, useState } from "react";
import { api, type Dashboard } from "../lib/api";
import { Card, EmptyState, ErrorState, Heading, Screen, Skeleton } from "../components/ui";

function heatStyle(heat: number) {
  const alpha = 0.08 + heat * 0.28;
  return { background: `rgba(0, 113, 227, ${alpha})` };
}

export function OperatorDashboard() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error" | "empty">("loading");
  const [error, setError] = useState("");

  const load = () => {
    setStatus("loading");
    api
      .dashboard()
      .then((dash) => {
        setData(dash);
        setStatus(dash.stations.length ? "ready" : "empty");
      })
      .catch((err: Error) => {
        setError(err.message);
        setStatus("error");
      });
  };

  useEffect(load, []);

  return (
    <Screen>
      <Heading kicker="Network" title="Demand this hour" />
      {status === "loading" ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
        </div>
      ) : null}
      {status === "error" ? <ErrorState message={error} onRetry={load} /> : null}
      {status === "empty" ? (
        <EmptyState title="No demand yet" body="Run the synthetic generator, then open this view again." />
      ) : null}
      {status === "ready" && data ? (
        <>
          <div className="mb-8 grid grid-cols-2 gap-3 md:grid-cols-4">
            <Card>
              <p className="text-[13px] text-mute">City wait</p>
              <p className="mt-2 text-[28px] font-semibold">{data.city_avg_wait} min</p>
            </Card>
            <Card>
              <p className="text-[13px] text-mute">Occupancy</p>
              <p className="mt-2 text-[28px] font-semibold">{data.city_occupancy}%</p>
            </Card>
          </div>
          <div className="grid gap-3 md:grid-cols-4">
            {data.stations.map((station) => (
              <div
                key={station.station_id}
                className="rounded-card p-5 shadow-card"
                style={heatStyle(station.heat)}
              >
                <p className="text-[16px] font-medium text-ink">{station.station_name}</p>
                <p className="mt-3 text-[24px] font-semibold text-ink">{station.predicted_exits}</p>
                <p className="text-[13px] text-mute">exits</p>
                <p className="mt-3 text-[13px] text-mute">
                  {station.avg_wait_minutes} min wait · {station.occupancy_pct}% full
                </p>
              </div>
            ))}
          </div>
          <h2 className="mb-4 mt-10 text-[20px] font-medium">Vehicles</h2>
          {data.vehicles.length === 0 ? (
            <EmptyState title="No vehicles listed" body="Feeder supply will appear after data generation." />
          ) : (
            <div className="overflow-hidden rounded-card bg-white shadow-card">
              <table className="w-full text-left text-[14px]">
                <thead className="text-mute">
                  <tr>
                    <th className="px-5 py-3 font-medium">Vehicle</th>
                    <th className="px-5 py-3 font-medium">Station</th>
                    <th className="px-5 py-3 font-medium">Load</th>
                  </tr>
                </thead>
                <tbody>
                  {data.vehicles.map((vehicle) => (
                    <tr key={vehicle.vehicle_id} className="border-t border-line">
                      <td className="px-5 py-3">{vehicle.vehicle_id}</td>
                      <td className="px-5 py-3">{vehicle.station_id}</td>
                      <td className="px-5 py-3">
                        {vehicle.occupancy}/{vehicle.capacity}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      ) : null}
    </Screen>
  );
}
