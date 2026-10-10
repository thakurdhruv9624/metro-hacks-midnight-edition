import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MapPin } from "lucide-react";
import { api, type Station } from "../lib/api";
import { Button, EmptyState, ErrorState, Heading, Screen, Skeleton } from "../components/ui";
import { useTrip } from "../state/trip";

export function TapIn() {
  const navigate = useNavigate();
  const { setStation } = useTrip();
  const [stations, setStations] = useState<Station[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error" | "empty">("loading");
  const [error, setError] = useState("The station list could not be reached.");

  const load = () => {
    setStatus("loading");
    api
      .stations()
      .then((data) => {
        setStations(data.stations);
        setStatus(data.stations.length ? "ready" : "empty");
      })
      .catch((err: Error) => {
        setError(err.message);
        setStatus("error");
      });
  };

  useEffect(load, []);

  return (
    <Screen>
      <Heading kicker="Gandhinagar metro" title="Tap in at your station" />
      {status === "loading" ? (
        <div className="grid gap-3">
          <Skeleton className="h-16" />
          <Skeleton className="h-16" />
          <Skeleton className="h-16" />
        </div>
      ) : null}
      {status === "error" ? <ErrorState message={error} onRetry={load} /> : null}
      {status === "empty" ? (
        <EmptyState title="No stations yet" body="Generate synthetic data, then refresh this page." />
      ) : null}
      {status === "ready" ? (
        <>
          <div className="grid gap-3 md:grid-cols-2">
            {stations.map((station) => {
              const active = selected === station.id;
              return (
                <button
                  key={station.id}
                  type="button"
                  onClick={() => setSelected(station.id)}
                  className={`flex items-center gap-4 rounded-card bg-white p-5 text-left shadow-card transition-colors duration-200 ${
                    active ? "ring-2 ring-accent" : ""
                  }`}
                >
                  <MapPin size={20} strokeWidth={1.75} className="text-accent" />
                  <span>
                    <span className="block text-[17px] font-medium text-ink">{station.name}</span>
                    <span className="block text-[14px] text-mute">{station.bays} pickup bays</span>
                  </span>
                </button>
              );
            })}
          </div>
          <div className="mt-8">
            <Button
              disabled={!selected}
              onClick={() => {
                const station = stations.find((item) => item.id === selected);
                if (!station) return;
                setStation(station);
                navigate("/drop");
              }}
            >
              Confirm tap-in
            </Button>
          </div>
        </>
      ) : null}
    </Screen>
  );
}
