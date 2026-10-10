import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, type DropZone } from "../lib/api";
import { Button, EmptyState, ErrorState, Heading, Screen, Skeleton } from "../components/ui";
import { useTrip } from "../state/trip";

export function Destination() {
  const navigate = useNavigate();
  const { station, setTrip } = useTrip();
  const [zones, setZones] = useState<DropZone[]>([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<"loading" | "ready" | "error" | "empty">("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!station) navigate("/");
  }, [station, navigate]);

  const load = () => {
    setStatus("loading");
    api
      .stations()
      .then((data) => {
        setZones(data.drop_zones);
        setStatus(data.drop_zones.length ? "ready" : "empty");
      })
      .catch((err: Error) => {
        setError(err.message);
        setStatus("error");
      });
  };

  useEffect(load, []);

  const submit = async () => {
    if (!station || !text.trim()) return;
    setBusy(true);
    setError("");
    try {
      const trip = await api.createTrip(station.id, text.trim());
      setTrip(trip);
      navigate("/pickup");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Trip could not be created.");
      setStatus("error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Screen>
      <Heading kicker={station?.name ?? "Station"} title="Choose a drop" />
      {status === "loading" ? (
        <>
          <Skeleton className="mb-4 h-12" />
          <Skeleton className="h-24" />
        </>
      ) : null}
      {status === "empty" ? (
        <EmptyState title="No drop zones" body="Add drop zones in stations.json and reload." />
      ) : null}
      {status === "error" ? <ErrorState message={error || "Could not load destinations."} onRetry={load} /> : null}
      {status === "ready" ? (
        <>
          <label className="mb-2 block text-[14px] text-mute" htmlFor="drop">
            Drop
          </label>
          <input
            id="drop"
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Infocity offices, PDEU, CH Road"
            className="h-12 w-full rounded-[16px] border-0 bg-white px-4 text-[16px] text-ink shadow-card outline-none ring-0 placeholder:text-mute"
          />
          <div className="mt-4 flex flex-wrap gap-2">
            {zones.map((zone) => (
              <button
                key={zone.id}
                type="button"
                onClick={() => setText(zone.name)}
                className="rounded-full bg-white px-4 py-2 text-[14px] text-ink shadow-card transition-opacity duration-200 hover:opacity-80"
              >
                {zone.name}
              </button>
            ))}
          </div>
          <div className="mt-8">
            <Button disabled={!text.trim() || busy} onClick={() => void submit()}>
              {busy ? "Finding pickup" : "Find pickup"}
            </Button>
          </div>
        </>
      ) : null}
    </Screen>
  );
}
