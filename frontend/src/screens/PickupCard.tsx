import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Bus, CarFront, Clock3, Hash } from "lucide-react";
import { api } from "../lib/api";
import { Button, Card, ErrorState, Heading, Screen, Skeleton } from "../components/ui";
import { useTrip } from "../state/trip";

export function PickupCard() {
  const navigate = useNavigate();
  const { trip, setTrip } = useTrip();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!trip) navigate("/");
  }, [trip, navigate]);

  const refresh = () => {
    if (!trip) return;
    setLoading(true);
    api
      .trip(trip.id)
      .then(setTrip)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  };

  if (!trip) return null;

  const slot = new Date(trip.assignment.slot_start).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  const Icon = trip.assignment.vehicle_type === "feeder-bus" ? Bus : CarFront;

  if (loading) {
    return (
      <Screen>
        <Heading title="Your pickup" />
        <Skeleton className="h-64" />
      </Screen>
    );
  }

  if (error) {
    return (
      <Screen>
        <ErrorState message={error} onRetry={refresh} />
      </Screen>
    );
  }

  return (
    <Screen>
      <Heading kicker="Before the train arrives" title="Your pickup is ready" />
      <Card>
        <div className="flex items-start justify-between">
          <div>
            <p className="text-[14px] text-mute">{trip.station_name}</p>
            <p className="mt-1 text-[28px] font-semibold text-ink">{trip.drop.zone_name}</p>
          </div>
          <Icon size={28} strokeWidth={1.6} className="text-accent" />
        </div>
        <div className="mt-8 grid grid-cols-3 gap-4">
          <div>
            <Hash size={16} strokeWidth={1.75} className="text-mute" />
            <p className="mt-2 text-[13px] text-mute">Bay</p>
            <p className="text-[22px] font-medium text-ink">{trip.assignment.bay}</p>
          </div>
          <div>
            <Clock3 size={16} strokeWidth={1.75} className="text-mute" />
            <p className="mt-2 text-[13px] text-mute">Slot</p>
            <p className="text-[22px] font-medium text-ink">{slot}</p>
          </div>
          <div>
            <p className="text-[13px] text-mute">Group</p>
            <p className="mt-6 text-[22px] font-medium text-ink">{trip.assignment.group_size}</p>
          </div>
        </div>
        <p className="mt-8 text-[15px] text-mute">
          {trip.assignment.vehicle_type === "feeder-bus" ? "Feeder bus" : "Shared e-auto"} {trip.assignment.vehicle_id}
        </p>
      </Card>
      <div className="mt-8">
        <Button onClick={() => navigate("/summary")}>Pay {trip.assignment.fare_inr} rupees</Button>
      </div>
    </Screen>
  );
}
